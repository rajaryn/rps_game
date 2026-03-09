from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Store game state: { room_id: { 'players': [sid1, sid2], 'choices': {sid: choice} } }
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_room')
def handle_join(data):
    room = data['room']
    sid = request.sid

    if room not in games:
        games[room] = {'players': [], 'choices': {}}

    if len(games[room]['players']) >= 2:
        emit('error', {'message': 'Room is full!'}, to=sid)
        return

    games[room]['players'].append(sid)
    join_room(room)
    
    emit('status', {'message': f'Player joined room: {room}. Waiting for opponent...'}, to=room)

    # Start the game if 2 players are in
    if len(games[room]['players']) == 2:
        emit('start_game', {'message': 'Game starting! Make your choice.'}, to=room)

@socketio.on('make_choice')
def handle_choice(data):
    room = data['room']
    choice = data['choice']
    sid = request.sid

    if room in games and sid in games[room]['players']:
        games[room]['choices'][sid] = choice

        # Check if both players have made their choices
        if len(games[room]['choices']) == 2:
            evaluate_winner(room)

def evaluate_winner(room):
    players = games[room]['players']
    p1, p2 = players[0], players[1]
    choice1, choice2 = games[room]['choices'][p1], games[room]['choices'][p2]

    # Game Logic
    rules = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    
    if choice1 == choice2:
        result = "It's a tie!"
    elif rules.get(choice1) == choice2:
        result = "Player 1 wins!"
    else:
        result = "Player 2 wins!"

    # Broadcast result
    socketio.emit('game_result', {
        'result': result, 
        'p1_choice': choice1, 
        'p2_choice': choice2
    }, to=room)

    # Reset choices for the next round
    games[room]['choices'] = {}

if __name__ == '__main__':
    socketio.run(app, debug=True)