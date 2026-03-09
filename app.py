from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# State: { room_id: { players, choices, scores, ready, mode, limit } }
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_room')
def handle_join(data):
    room = data['room']
    sid = request.sid
    mode_data = data.get('settings', 'rounds_3').split('_')
    mode = mode_data[0]
    limit = int(mode_data[1])

    if room not in games:
        # First player creates the room settings
        games[room] = {
            'players': [], 'choices': {}, 'scores': {}, 
            'ready': [], 'mode': mode, 'limit': limit
        }

    if len(games[room]['players']) >= 2:
        emit('error', {'message': 'Room is full!'}, to=sid)
        return

    games[room]['players'].append(sid)
    games[room]['scores'][sid] = 0
    join_room(room)
    
    emit('status', {'message': f'Joined {room}. Waiting for opponent...'}, to=sid)

    if len(games[room]['players']) == 2:
        # Send room settings to both players to sync UI
        emit('start_match', {
            'message': 'Match starting!',
            'mode': games[room]['mode'],
            'limit': games[room]['limit']
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
    choice1, choice2 = games[room]['choices'][p1], games[room]['choices'][p2]
    
    rules = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    
    winner_sid = None
    if choice1 == choice2:
        result_text = "It's a tie!"
    elif rules.get(choice1) == choice2:
        result_text = "Player 1 wins!"
        winner_sid = p1
        games[room]['scores'][p1] += 1
    else:
        result_text = "Player 2 wins!"
        winner_sid = p2
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
        'scores': list(games[room]['scores'].values()),
        'game_over': game_over
    }, to=room)

    # Clear choices for the next round
    games[room]['choices'] = {}

    # NEW: Automatically start the next round after a 3-second delay
    if not game_over:
        socketio.sleep(3) 
        socketio.emit('start_round', to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)