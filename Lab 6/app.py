"""
Fake Goose Counting Game
A demo game showing collaborative counting with simulated players
"""

from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Game configuration
CORRECT_ANSWER = 14  # 14 geese in the image
IMAGE_DISPLAY_TIME = 5  # seconds
COUNTDOWN_BEFORE_ANSWER = 5  # seconds countdown before answering
ANSWER_TIME_LIMIT = 5  # seconds to answer

# Simulated players with their responses
PLAYERS = [
    {
        'id': 1,
        'name': 'Player 1',
        'ip': '10.56.129.168',
        'answer': 14,
        'response_time': 4.9,  # answers around 4 seconds
        'status': 'answered'
    },
    {
        'id': 2,
        'name': 'Player 2', 
        'ip': '10.56.130.30',
        'answer': 14,
        'response_time': 4.1,  # answers close to 5 seconds
        'status': 'answered'
    },
    {
        'id': 3,
        'name': 'Player 3',
        'ip': '10.56.130.29',
        'answer': 13,
        'response_time': 3.9,  # didn't answer in time
        'status': 'answered'
    }
]


@app.route('/')
def index():
    """Main game page"""
    return render_template('game.html')


@app.route('/api/game-config')
def game_config():
    """Get game configuration"""
    return jsonify({
        'correct_answer': CORRECT_ANSWER,
        'image_display_time': IMAGE_DISPLAY_TIME,
        'countdown_before_answer': COUNTDOWN_BEFORE_ANSWER,
        'answer_time_limit': ANSWER_TIME_LIMIT,
        'players': PLAYERS
    })


if __name__ == '__main__':
    print("=" * 60)
    print("  Fake Goose Counting Game")
    print("=" * 60)
    print("  URL: http://localhost:5000")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)