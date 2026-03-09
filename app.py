from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# State: { room_id: { players, names, choices, scores, mode, limit } }
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_room')
def handle_join(data):
    room = data['room']
    player_name = data.get('name', 'Anonymous')
    sid = request.sid
    mode_data = data.get('settings', 'rounds_3').split('_')
    mode = mode_data[0]
    limit = int(mode_data[1])

    if room not in games:
        games[room] = {
            'players': [], 'names': {}, 'choices': {}, 'scores': {}, 
            'mode': mode, 'limit': limit
        }

    if len(games[room]['players']) >= 2:
        emit('error', {'message': 'Room is full!'}, to=sid)
        return

    games[room]['players'].append(sid)
    games[room]['names'][sid] = player_name
    games[room]['scores'][sid] = 0
    join_room(room)
    
    emit('status', {'message': f'Joined {room} as {player_name}. Waiting for opponent...'}, to=sid)

    if len(games[room]['players']) == 2:
        p1, p2 = games[room]['players'][0], games[room]['players'][1]
        emit('start_match', {
            'message': 'Match starting!',
            'mode': games[room]['mode'],
            'limit': games[room]['limit'],
            'names': [games[room]['names'][p1], games[room]['names'][p2]]
        }, to=room)

@socketio.on('make_choice')
def handle_choice(data):
    room = data['room']
    choice = data['choice']
    sid = request.sid

    if room in games and sid in games[room]['players']:
        games[room]['choices'][sid] = choice

        if len(games[room]['choices']) == 2:
            evaluate_winner(room)

def evaluate_winner(room):
    players = games[room]['players']
    p1, p2 = players[0], players[1]
    p1_name = games[room]['names'][p1]
    p2_name = games[room]['names'][p2]
    choice1, choice2 = games[room]['choices'][p1], games[room]['choices'][p2]
    
    rules = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    
    winner_sid = 'tie' # NEW: Default to tie
    if choice1 == choice2:
        result_text = "It's a tie!"
    elif rules.get(choice1) == choice2:
        result_text = f"{p1_name} wins!"
        winner_sid = p1 # NEW
        games[room]['scores'][p1] += 1
    else:
        result_text = f"{p2_name} wins!"
        winner_sid = p2 # NEW
        games[room]['scores'][p2] += 1

    # Check for game over in 'rounds' mode
    game_over = False
    if games[room]['mode'] == 'rounds':
        if games[room]['scores'][p1] >= games[room]['limit'] or games[room]['scores'][p2] >= games[room]['limit']:
            game_over = True

    socketio.emit('round_result', {
        'result': result_text, 
        'p1_choice': choice1, 
        'p2_choice': choice2,
        'scores': [games[room]['scores'][p1], games[room]['scores'][p2]],
        'names': [p1_name, p2_name],
        'game_over': game_over,
        'winner_sid': winner_sid # NEW: Send this to the frontend
    }, to=room)

    games[room]['choices'] = {}

    if not game_over:
        socketio.sleep(3) 
        socketio.emit('start_round', to=room)
        
if __name__ == '__main__':
    socketio.run(app, debug=True)