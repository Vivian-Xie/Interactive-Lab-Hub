"""
Real-time Goose Counting Game
Connects to physical buttons via MQTT and displays game in real-time
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import json
from datetime import datetime
from collections import OrderedDict
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'goose-game-2025'

# Try eventlet first, fall back to threading
try:
    import eventlet
    eventlet.monkey_patch()
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
except ImportError:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Game state
game_state = {
    'started': False,
    'phase': 'waiting',  # waiting, image_display, countdown, answering, finished
    'players': OrderedDict(),  # {mac: {'name': str, 'ip': str, 'clicks': int, 'answer': int, 'time': float}}
    'correct_answer': 14,
    'winner': None,
    'answer_phase_start': None
}

# Game configuration
GAME_CONFIG = {
    'correct_answer': 14,
    'image_display_time': 5,
    'countdown_before_answer': 5,
    'answer_time_limit': 5
}


@app.route('/')
def index():
    """Main game page"""
    return render_template('game.html')


@app.route('/api/game-config')
def game_config():
    """Get game configuration"""
    return json.dumps(GAME_CONFIG)


@socketio.on('connect')
def handle_connect():
    """Client connected - send current game state"""
    print(f'Client connected: {request.sid}')
    emit('game_state', {
        'state': game_state['phase'],
        'players': [
            {
                'mac': mac,
                'name': data['name'],
                'ip': data['ip'],
                'clicks': data.get('clicks', 0),
                'answer': data.get('answer'),
                'time': data.get('time')
            }
            for mac, data in game_state['players'].items()
        ],
        'winner': game_state['winner']
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('start_game')
def handle_start_game():
    """Start the game"""
    if not game_state['started']:
        game_state['started'] = True
        game_state['phase'] = 'image_display'
        game_state['players'].clear()
        game_state['winner'] = None
        game_state['answer_phase_start'] = None
        
        emit('game_started', {
            'config': GAME_CONFIG
        }, broadcast=True)
        
        print('Game started')


@socketio.on('button_press')
def handle_button_press(data):
    """Handle button press from Pi"""
    try:
        mac = data.get('mac')
        ip = data.get('ip', 'unknown')
        timestamp = data.get('timestamp', int(datetime.now().timestamp()))
        
        # Only count during answering phase
        if game_state['phase'] != 'answering':
            return
        
        # Initialize player if new
        if mac not in game_state['players']:
            player_num = len(game_state['players']) + 1
            game_state['players'][mac] = {
                'name': f'Player {player_num}',
                'ip': ip,
                'clicks': 0,
                'answer': None,
                'time': None,
                'first_click_time': datetime.now(),
                'last_click_time': None
            }
        
        # Increment click count
        game_state['players'][mac]['clicks'] += 1
        game_state['players'][mac]['last_click_time'] = datetime.now()
        clicks = game_state['players'][mac]['clicks']
        
        # Do NOT broadcast click count - keep it hidden
        print(f'{game_state["players"][mac]["name"]}: Click {clicks}')
        
    except Exception as e:
        print(f'Error handling button press: {e}')


@socketio.on('phase_change')
def handle_phase_change(data):
    """Change game phase (from web client or timer)"""
    phase = data.get('phase')
    if phase:
        game_state['phase'] = phase
        
        # If entering answering phase, record start time
        if phase == 'answering':
            game_state['answer_phase_start'] = datetime.now()
            
            # Start timer to auto-calculate answers after 5 seconds
            def auto_end_answer_phase():
                import time
                time.sleep(GAME_CONFIG['answer_time_limit'])
                with app.app_context():
                    calculate_and_reveal_answers()
            
            timer_thread = threading.Thread(target=auto_end_answer_phase)
            timer_thread.daemon = True
            timer_thread.start()
        
        emit('phase_changed', {'phase': phase}, broadcast=True)
        print(f'Phase changed to: {phase}')


def calculate_and_reveal_answers():
    """Calculate all players' answers and reveal results"""
    try:
        print('Calculating answers...')
        
        # Get all players who participated
        participants = []
        for mac, data in game_state['players'].items():
            if data['clicks'] > 0 and data['last_click_time']:
                # Calculate elapsed time from start to last click
                elapsed = (data['last_click_time'] - data['first_click_time']).total_seconds()
                participants.append((mac, data, elapsed))
        
        # Sort by elapsed time (faster is better)
        participants.sort(key=lambda x: x[2])
        
        # Calculate answers and determine winner
        for mac, player_data, elapsed in participants:
            answer = player_data['clicks']
            player_data['answer'] = answer
            player_data['time'] = round(elapsed, 1)
            
            # Check if winner
            is_correct = answer == GAME_CONFIG['correct_answer']
            is_winner = is_correct and game_state['winner'] is None
            
            if is_winner:
                game_state['winner'] = mac
            
            # Broadcast result for this player
            socketio.emit('player_answer', {
                'mac': mac,
                'name': player_data['name'],
                'ip': player_data['ip'],
                'answer': answer,
                'time': player_data['time'],
                'is_correct': is_correct,
                'is_winner': is_winner
            }, broadcast=True, namespace='/')
            
            status = 'WINNER' if is_winner else ('correct' if is_correct else 'incorrect')
            print(f'{player_data["name"]}: Answer {answer} in {elapsed:.1f}s [{status}]')
        
        # Mark phase as finished
        game_state['phase'] = 'finished'
        socketio.emit('phase_changed', {'phase': 'finished'}, broadcast=True, namespace='/')
        
        print('All answers revealed')
        
    except Exception as e:
        print(f'Error calculating answers: {e}')


@socketio.on('reset_game')
def handle_reset_game():
    """Reset game"""
    game_state['started'] = False
    game_state['phase'] = 'waiting'
    game_state['players'].clear()
    game_state['winner'] = None
    game_state['answer_phase_start'] = None
    
    emit('game_reset', broadcast=True)
    print('Game reset')


if __name__ == '__main__':
    print("=" * 60)
    print("  Real-time Goose Counting Game")
    print("=" * 60)
    print(f"  Game URL: http://0.0.0.0:5000")
    print("=" * 60)
    
    # Try to enable MQTT bridge
    try:
        from mqtt_game_bridge import start_mqtt_bridge
        start_mqtt_bridge(socketio, game_state)
        print("  MQTT bridge enabled")
    except ImportError:
        print("  MQTT bridge not available (install paho-mqtt)")
    except Exception as e:
        print(f"  MQTT bridge disabled: {e}")
    
    print("=" * 60)
    print()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
