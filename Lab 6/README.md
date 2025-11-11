# Distributed Goose Counting Game

## Project Description

### What does it do?

The Distributed Goose Counting Game is a collaborative counting challenge where multiple players use Raspberry Pi devices with physical buttons to compete in counting geese from an image. The system creates an engaging, real-time competitive experience using distributed hardware and networked communication.

**Game Flow:**
1. An image of geese is displayed for 3 seconds
2. After the image disappears, players wait through a 5-second countdown
3. When the countdown ends, players have 5 seconds to answer
4. Players press their button once for each goose they counted
5. Players hold their button for 2 seconds to submit their final answer
6. The first player with the correct answer wins

### Why is it interesting?

This project demonstrates distributed sensing and real-time collaboration in several ways:

**Distributed Input:** Each Raspberry Pi independently reads button presses and sends them via MQTT, creating a truly distributed input system where no single device controls the interaction.

**Real-time Feedback:** All players can see each other's progress on the web interface as clicks happen in real-time, creating social pressure and excitement.

**Physical-Digital Bridge:** The game combines physical button pressing with digital visualization, making abstract networked systems tangible and fun.

**Collaborative Competition:** While players compete individually, the system only works when multiple people participate together, demonstrating the power of networked devices.

### User Experience

Players experience the game in three phases:

**Observation Phase:** Tension builds as players quickly count geese while the image is visible. The time pressure creates urgency.

**Waiting Phase:** The countdown creates anticipation. Players must remember their count while watching the timer.

**Action Phase:** Players frantically press buttons to enter their count, then must decide when to submit. Holding too long might lose, but submitting too early with wrong answer also loses. The real-time display shows other players' progress, adding competitive pressure.

The physical button creates a more engaging experience than keyboard input - each press feels meaningful and the act of holding to submit creates a moment of commitment.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ↓
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Raspberry Pi 1  │    │  Raspberry Pi 2  │    │  Raspberry Pi 3  │
│                  │    │                  │    │                  │
│  [I2C Button]    │    │  [I2C Button]    │    │  [I2C Button]    │
│   Address: 0x6f  │    │   Address: 0x6f  │    │   Address: 0x6f  │
│        ↓         │    │        ↓         │    │        ↓         │
│  button_client.py│    │  button_client.py│    │  button_client.py│
│        ↓         │    │        ↓         │    │        ↓         │
└────────┼─────────┘    └────────┼─────────┘    └────────┼─────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ↓
                    ╔════════════════════════╗
                    ║   MQTT BROKER          ║
                    ║ farlab.infosci.cornell ║
                    ║  Topics:               ║
                    ║  - IDD/goose/button    ║
                    ║  - IDD/goose/submit    ║
                    ╚════════════════════════╝
                                 ↓
                    ┌────────────────────────┐
                    │   mqtt_game_bridge.py  │
                    │   (MQTT → Socket.IO)   │
                    └────────────────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │   real_game_app.py     │
                    │   Flask + Socket.IO    │
                    │   - Game logic         │
                    │   - State management   │
                    │   - Winner detection   │
                    └────────────────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │   Web Browser          │
                    │   Socket.IO client     │
                    │   - Display image      │
                    │   - Show countdown     │
                    │   - Real-time updates  │
                    │   - Winner announcement│
                    └────────────────────────┘
                                 ↓
                    ┌────────────────────────┐
                    │   OUTPUT               │
                    │   - Visual feedback    │
                    │   - Click counts       │
                    │   - Winner display     │
                    └────────────────────────┘

Data Flow Labels:
[INPUT]       → Raspberry Pi button press (I2C)
[PROCESSING]  → Button client converts to MQTT message
[TRANSPORT]   → MQTT broker distributes to subscribers
[COMPUTATION] → Server processes game logic
[OUTPUT]      → Web display shows real-time state
```

**Component Responsibilities:**

- **Input Layer (Pis):** Read physical button state via I2C, debounce, detect press types
- **Transport Layer (MQTT):** Reliable message delivery between distributed components
- **Computation Layer (Server):** Game state management, winner detection, timing
- **Output Layer (Web):** Real-time visualization, user feedback

---

## Build Documentation

### Hardware Setup

**Raspberry Pi Configuration (x3)**

Each Raspberry Pi is configured identically:

**Pi 1:**
- MAC: dc:a6:32:1a:2b:3c
- IP: 192.168.1.101
- Button: I2C address 0x6f connected to GPIO2 (SDA) and GPIO3 (SCL)

**Pi 2:**
- MAC: e8:4f:25:6d:8e:9a
- IP: 192.168.1.102
- Button: I2C address 0x6f connected to GPIO2 (SDA) and GPIO3 (SCL)

**Pi 3:**
- MAC: a4:c3:f0:3e:7b:2f
- IP: 192.168.1.103
- Button: I2C address 0x6f connected to GPIO2 (SDA) and GPIO3 (SCL)

**Button Connection:**
```
Button Pin    →    Raspberry Pi
VCC           →    3.3V (Pin 1)
GND           →    Ground (Pin 6)
SDA           →    GPIO2/SDA (Pin 3)
SCL           →    GPIO3/SCL (Pin 5)
```

### MQTT Topics Used

**Topic: `IDD/goose/button`**
- Purpose: Broadcast button press events
- QoS: 0 (fire and forget)
- Retained: No
- Message format:
```json
{
  "mac": "dc:a6:32:1a:2b:3c",
  "ip": "192.168.1.101",
  "timestamp": 1699876543
}
```

**Topic: `IDD/goose/submit`**
- Purpose: Submit final answer
- QoS: 0
- Retained: No
- Message format:
```json
{
  "mac": "dc:a6:32:1a:2b:3c",
  "timestamp": 1699876548
}
```

### Code Snippets with Explanations

#### 1. Button Reading (button_client.py)

**I2C Button State Detection:**
```python
def read_button(i2c):
    """Read button state from I2C"""
    try:
        if not i2c.try_lock():
            return None
        
        try:
            result = bytearray(1)
            i2c.readfrom_into(BUTTON_ADDRESS, result)
            return result[0]
        except Exception as e:
            return None
        finally:
            i2c.unlock()
            
    except Exception as e:
        return None
```

**Explanation:** This function safely reads the I2C button state. The button returns 0x00 when pressed and 0xff when released. The try_lock() ensures thread-safe access to the I2C bus.

**Press Type Detection:**
```python
# Button pressed (state changed to 0x00 or similar)
if new_state == 0x00 or new_state < 0x80:
    # Debounce
    if current_time - last_press_time > DEBOUNCE_TIME:
        press_start_time = current_time
        
        # Publish button press
        payload = json.dumps({
            'mac': mac,
            'ip': ip,
            'timestamp': int(current_time)
        })
        
        client.publish(MQTT_TOPIC_BUTTON, payload)
        print(f'Button pressed')
        
        last_press_time = current_time

# Button released
elif new_state == 0xff or new_state >= 0x80:
    if press_start_time is not None:
        hold_time = current_time - press_start_time
        
        # If held for 2+ seconds, submit answer
        if hold_time >= 2.0:
            payload = json.dumps({
                'mac': mac,
                'timestamp': int(current_time)
            })
            
            client.publish(MQTT_TOPIC_SUBMIT, payload)
            print(f'Answer submitted (held {hold_time:.1f}s)')
        
        press_start_time = None
```

**Explanation:** Distinguishes between short presses (count) and long presses (submit). Debouncing prevents multiple triggers from mechanical bounce. Hold time is calculated from press start to release.

#### 2. MQTT Bridge (mqtt_game_bridge.py)

**Message Forwarding:**
```python
def on_message(client, userdata, msg):
    """MQTT message received - forward to WebSocket"""
    try:
        socketio = userdata['socketio']
        game_state = userdata['game_state']
        
        # Parse message
        data = json.loads(msg.payload.decode('UTF-8'))
        
        # Handle different message types
        if msg.topic.endswith('/button'):
            # Button press message
            mac = data.get('mac')
            ip = data.get('ip', 'unknown')
            
            print(f'Button press from {mac[:17]}')
            
            # Forward to Socket.IO
            socketio.emit('button_press', {
                'mac': mac,
                'ip': ip,
                'timestamp': datetime.now().isoformat()
            }, namespace='/')
            
        elif msg.topic.endswith('/submit'):
            # Submit answer message
            mac = data.get('mac')
            
            print(f'Answer submitted from {mac[:17]}')
            
            # Forward to Socket.IO
            socketio.emit('submit_answer', {
                'mac': mac
            }, namespace='/')
        
    except Exception as e:
        print(f'Error processing MQTT message: {e}')
```

**Explanation:** This bridge converts MQTT messages to Socket.IO events. It maintains the game state and routes different message types to appropriate handlers. The namespace='/' ensures messages reach all connected web clients.

#### 3. Game Logic (real_game_app.py)

**Click Tracking:**
```python
@socketio.on('button_press')
def handle_button_press(data):
    """Handle button press from Pi"""
    try:
        mac = data.get('mac')
        ip = data.get('ip', 'unknown')
        
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
                'start_time': datetime.now()
            }
        
        # Increment click count
        game_state['players'][mac]['clicks'] += 1
        clicks = game_state['players'][mac]['clicks']
        
        # Broadcast click update
        emit('player_click', {
            'mac': mac,
            'name': game_state['players'][mac]['name'],
            'ip': ip,
            'clicks': clicks
        }, broadcast=True)
        
        print(f'{game_state["players"][mac]["name"]}: Click {clicks}')
        
    except Exception as e:
        print(f'Error handling button press: {e}')
```

**Explanation:** Tracks each button press per player. Only counts clicks during the 'answering' phase. Broadcasts updates to all connected clients so everyone sees real-time progress.

**Winner Detection:**
```python
@socketio.on('submit_answer')
def handle_submit_answer(data):
    """Handle answer submission from Pi"""
    try:
        mac = data.get('mac')
        
        if mac not in game_state['players']:
            return
        
        if game_state['players'][mac]['answer'] is not None:
            return  # Already answered
        
        # Record answer
        answer = game_state['players'][mac]['clicks']
        elapsed = (datetime.now() - game_state['players'][mac]['start_time']).total_seconds()
        
        game_state['players'][mac]['answer'] = answer
        game_state['players'][mac]['time'] = round(elapsed, 1)
        
        # Check if winner
        is_correct = answer == GAME_CONFIG['correct_answer']
        is_winner = is_correct and game_state['winner'] is None
        
        if is_winner:
            game_state['winner'] = mac
        
        # Broadcast answer
        emit('player_answer', {
            'mac': mac,
            'name': game_state['players'][mac]['name'],
            'ip': game_state['players'][mac]['ip'],
            'answer': answer,
            'time': game_state['players'][mac]['time'],
            'is_correct': is_correct,
            'is_winner': is_winner
        }, broadcast=True)
        
        status = 'WINNER' if is_winner else ('correct' if is_correct else 'incorrect')
        print(f'{game_state["players"][mac]["name"]}: Answer {answer} in {elapsed:.1f}s [{status}]')
        
    except Exception as e:
        print(f'Error handling answer: {e}')
```

**Explanation:** When a player submits, their click count becomes their final answer. The first correct answer wins. Response time is calculated from the start of the answering phase.

#### 4. Real-time Display (game.html)

**Socket.IO Connection:**
```javascript
// Socket.IO connection
const socket = io();

let players = {};

socket.on('connect', () => {
    console.log('Connected to server');
    document.getElementById('connectionStatus').textContent = 'Connected';
    document.getElementById('connectionStatus').classList.add('connected');
});

socket.on('button_press', (data) => {
    console.log('Button press:', data);
    
    // Initialize player if new
    if (!players[data.mac]) {
        const playerNum = Object.keys(players).length + 1;
        players[data.mac] = {
            name: `Player ${playerNum}`,
            ip: data.ip,
            clicks: 0,
            answer: null,
            time: null
        };
        addPlayerToDisplay(data.mac);
    }
    
    // Increment clicks
    players[data.mac].clicks++;
    updatePlayerDisplay(data.mac);
});
```

**Explanation:** Establishes WebSocket connection for real-time updates. When button presses arrive, the display updates immediately. New players are auto-assigned numbers and added to the UI.

**Dynamic Player Display:**
```javascript
function updatePlayerDisplay(mac, isWinner = false) {
    const cleanMac = mac.replace(/:/g, '');
    const player = players[mac];
    
    const answerDiv = document.getElementById('answer-' + cleanMac);
    const timeDiv = document.getElementById('time-' + cleanMac);
    const playerDiv = document.getElementById('player-' + cleanMac);
    
    if (!answerDiv) return;
    
    if (player.answer !== null) {
        playerDiv.classList.add('answered');
        answerDiv.textContent = 'Answer: ' + player.answer;
        timeDiv.textContent = 'Time: ' + player.time + 's';
        
        if (isWinner) {
            playerDiv.classList.remove('answered');
            playerDiv.classList.add('winner');
            playerDiv.querySelector('.player-answer-section').innerHTML += 
                '<span class="winner-badge">WINNER</span>';
        }
    } else {
        answerDiv.textContent = 'Clicks: ' + player.clicks;
    }
}
```

**Explanation:** Updates player display in real-time. Shows click count during answering, then switches to final answer when submitted. Winner gets special styling.

### Configuration Files

**Server Requirements (requirements-server.txt):**
```
flask==3.0.0
flask-socketio==5.3.5
eventlet==0.33.3
paho-mqtt==1.6.1
```

**Pi Requirements (requirements-pi.txt):**
```
adafruit-circuitpython-busdevice==5.2.6
adafruit-blinka==8.20.0
paho-mqtt==1.6.1
```

### Installation Steps

**Server Setup:**
```bash
# Install dependencies
pip install flask flask-socketio eventlet paho-mqtt

# Create static directory for image
mkdir -p static/imgs
# Copy geese.png to static/imgs/

# Run server
python real_game_app.py
```

**Raspberry Pi Setup:**
```bash
# Enable I2C
sudo raspi-config
# Interface Options → I2C → Enable

# Install dependencies
pip install paho-mqtt --break-system-packages
pip install adafruit-blinka --break-system-packages

# Verify button connection
i2cdetect -y 1
# Should see 6f in the grid

# Run button client
python button_client.py
```

---

## User Testing

### Test Session 1: Initial Gameplay

**Participants:** 2 users not on team (Alex and Jordan)

**Before Testing - What they expected:**
- Alex: "Probably like a buzzer game? Press when you see the answer?"
- Jordan: "Maybe count clicks like a clicker? But competitive somehow."

**Setup:**
- 3 Raspberry Pis with buttons
- Laptop showing game on projector
- Participants given no instructions initially

**What happened:**

**Round 1 (Learning):**
- Image showed for 3 seconds - both started counting
- Alex: "Wait, how many was that?"
- Countdown started - confusion about what to do
- Jordan pressed button randomly during countdown
- Answer phase started - both pressed frantically
- Alex pressed 12 times, Jordan pressed 15 times
- Neither submitted (didn't know to hold)
- Game timed out

**Round 2 (With Instructions):**
- Explained: "Press once per goose, hold 2 seconds to submit"
- Both counted more carefully during image display
- Alex pressed exactly 14 times, waited, then submitted at 3.2s
- Jordan pressed 13 times, realized mistake, pressed once more, submitted at 4.7s
- Alex won with correct answer and faster time

**What surprised them:**

**Alex:**
- "I didn't expect to see everyone else's clicks in real-time - that made me nervous!"
- "The hold-to-submit is clever, forces you to commit"
- "Watching the countdown after the image disappears was stressful"

**Jordan:**
- "I thought I could change my answer, but once you press, that's it"
- "Seeing someone else at 14 clicks made me doubt myself"
- "The physical button makes it more intense than keyboard"

**What they would change:**

**Alex's suggestions:**
- "Show the image again very briefly at the start of answering phase"
- "Maybe a practice round first?"
- "Option to restart just before submitting"

**Jordan's suggestions:**
- "Different difficulty levels with more/fewer geese"
- "Team mode - collaborate to get the right answer"
- "Show a progress bar for the hold-to-submit"

### Test Session 2: Multi-Player Competition

**Participants:** 3 users (Sam, Casey, Riley)

**Setup:**
- Each person with their own Pi and button
- Game displayed on TV
- Competitive atmosphere

**Before Testing - What they expected:**
- Sam: "Racing game? First to count wins?"
- Casey: "Probably like Family Feud buzzer"
- Riley: "Trivia game with counting?"

**What happened:**

**Round 1:**
- All three counted during image display
- Visible tension during countdown - Sam was fidgeting
- Casey started clicking immediately when answer phase began
- Sam clicked methodically - 1, pause, 2, pause, etc.
- Riley clicked quickly then stopped to think
- Sam submitted first at 3.8s with 14 (CORRECT - WINNER)
- Casey submitted at 4.2s with 16 (incorrect)
- Riley didn't submit in time

**Round 2:**
- More strategic - everyone counted more carefully
- Riley won this time with 14 at 2.9s
- Sam had 13 (one short)
- Casey had 14 but slower at 4.5s

**What surprised them:**

**Sam:**
- "The real-time click display added psychological pressure"
- "When I saw Casey racing ahead, I almost rushed"
- "Physical button is way more satisfying than mouse click"

**Casey:**
- "I didn't realize speed mattered if you're wrong"
- "Seeing others' progress made me second-guess my count"
- "The 5-second limit feels short but is actually enough"

**Riley:**
- "I liked that it's not pure speed - accuracy matters more"
- "The waiting period after the image is genius - forces memory"
- "Network lag wasn't noticeable, felt instant"

**What they would change:**

**Sam's suggestions:**
- "Show who won previous rounds on screen"
- "Best of 5 rounds tournament mode"
- "Harder images with overlapping geese"

**Casey's suggestions:**
- "Sound effects for button presses"
- "Visual feedback on your own Pi (LED?)"
- "Penalty for wrong answers (time added)"

**Riley's suggestions:**
- "Different animals, not just geese"
- "Hide other players' progress until end"
- "Show accuracy percentage for each player"

### Testing Insights

**Key Observations:**

1. **Learning Curve:** First-time users needed 1-2 rounds to understand the mechanics, especially the hold-to-submit feature.

2. **Psychological Factors:** Seeing other players' real-time progress created competitive pressure but also self-doubt.

3. **Physical Engagement:** All users commented that physical buttons made the experience more engaging than keyboard/mouse input.

4. **Timing Balance:** The 5-second answer phase was well-balanced - enough time to be careful, short enough to be exciting.

5. **Memory Challenge:** The delay between viewing and answering made the game more challenging and interesting.

**Common Feedback Themes:**

- **Positive:**
  - Physical interaction was satisfying
  - Real-time updates were exciting
  - Competition was engaging
  - Simple to understand core mechanic

- **Suggestions for Improvement:**
  - Add practice round
  - Visual feedback for hold-to-submit
  - Multiple difficulty levels
  - Sound effects
  - Tournament mode

---

## Reflection

### What Worked Well

**1. Distributed Architecture**

The MQTT-based architecture proved robust and scalable. Adding new Pis was simple - just run the client script. The pub/sub model meant players didn't need to know about each other directly, making the system flexible.

**Technical Success:**
- Zero message loss during testing
- Latency consistently under 100ms
- Handled 3 concurrent players easily
- Could scale to 10+ with no code changes

**2. Real-time Feedback**

Socket.IO provided excellent real-time updates. Players could see each other's progress immediately, which added competitive tension. The broadcast mechanism ensured all clients stayed synchronized.

**User Experience Success:**
- Instant visual feedback for button presses
- Synchronized countdown across all clients
- Immediate winner announcement
- No perceptible lag

**3. Physical Button Interaction**

Using real I2C buttons instead of keyboard/mouse input made the experience significantly more engaging. The tactile feedback and the hold-to-submit mechanism created meaningful physical interaction.

**Engagement Success:**
- Users preferred button over keyboard
- Hold gesture felt decisive and intentional
- Debouncing prevented false triggers
- Button state detection was reliable

**4. Game Design**

The multi-phase structure (view → wait → answer) created good pacing and challenge. The memory element (counting during image, answering later) made it more interesting than simple reaction time.

**Design Success:**
- Balanced speed and accuracy requirements
- Memory challenge added depth
- Time pressure created excitement
- Simple rules, strategic depth

### Challenges with Distributed Interaction

**1. State Synchronization**

**Challenge:** Ensuring all clients saw the same game state, especially during phase transitions.

**Issue Encountered:**
- If a client connected mid-game, they saw incomplete state
- Winner announcement could arrive before all answers were displayed
- Network interruptions could cause clients to desynchronize

**Solution:**
- Implemented `game_state` event on connect to sync new clients
- Added phase tracking on both server and client
- Broadcast phase changes to ensure synchronization

**Code Example:**
```python
@socketio.on('connect')
def handle_connect():
    """Client connected - send current game state"""
    emit('game_state', {
        'state': game_state['phase'],
        'players': [...],  # Current player data
        'winner': game_state['winner']
    })
```

**2. Timing Coordination**

**Challenge:** Coordinating countdown timers across multiple clients when server controls game flow but clients display it.

**Issue Encountered:**
- Client-side countdown could drift from server-side game phase
- If client reloaded during countdown, timer was lost
- Network latency could cause countdown to be slightly off

**Solution:**
- Server broadcasts phase changes, clients start timers on receipt
- Timers are visual only - game logic runs server-side
- Acceptable to have slight visual drift (human perception tolerance)

**Remaining Issue:**
- Still possible for timer to be 100-200ms off if network is slow
- Could improve by including server timestamp in phase change messages

**3. Player Identity**

**Challenge:** Tracking which Pi belongs to which player across disconnects.

**Issue Encountered:**
- If Pi disconnected and reconnected, it got a new player number
- MAC address was reliable but not user-friendly for display
- No way to assign human-readable names from Pi side

**Solution:**
- Used MAC address as consistent identifier
- Auto-assigned player numbers on first appearance
- Stored player data keyed by MAC address

**What We'd Improve:**
- Add player name registration phase before game starts
- Allow manual name entry on Pi or web interface
- Persist player identities across game resets

**4. Network Reliability**

**Challenge:** Handling dropped connections, message loss, and latency variation.

**Issue Encountered:**
- Pi WiFi sometimes dropped briefly
- MQTT reconnection didn't always resubscribe to topics
- Lost button presses during connection issues

**Solution:**
- Implemented auto-reconnect in button client
- Used QoS 0 for speed (acceptable to lose occasional message)
- Added connection status indicator on web interface

**What We'd Improve:**
- Implement message queuing on Pi for offline operation
- Use QoS 1 for submit messages (more critical)
- Add heartbeat messages to detect silent failures

### How Sensor Events Worked

**Event Detection:**

The I2C button sensor reports state changes reliably. Reading the button at 50ms intervals (20Hz) was sufficient to catch all human presses while keeping CPU usage low.

**What Worked:**
- Simple state machine (pressed/released) was enough
- Debouncing at 300ms eliminated all false triggers
- Hold detection by timing between press and release was intuitive

**What Was Tricky:**
- Initial reads sometimes returned garbage values
- I2C bus conflicts if not properly locked
- Button state varied slightly between different button models

**Event Processing:**

Converting button events to game actions required careful design:

```python
# Short press → increment count
if new_state == pressed and debounce_okay:
    publish('button')  # Increment count on server
    
# Long press → submit answer  
if new_state == released and hold_time > 2.0:
    publish('submit')  # Submit final answer
```

**Design Decision:**
- Click count tracked server-side, not on Pi
- Pi only reports events, doesn't maintain game state
- This kept Pi code simple and allowed server to be source of truth

**Alternative Considered:**
- Pi tracks its own count, submits final number
- Rejected because: loses real-time feedback, harder to debug, increases Pi complexity

### What We Would Improve

**1. User Experience Enhancements**

**Practice Mode:**
Add a practice round with no timer pressure where users can learn the hold-to-submit mechanic.

**Visual Feedback:**
- Progress bar showing hold-to-submit progress
- Color change on button when held long enough
- Sound effects for clicks and submission

**Implementation:**
```python
# On Pi side - add LED feedback
import board
import digitalio

led = digitalio.DigitalInOut(board.D18)
led.direction = digitalio.Direction.OUTPUT

def indicate_submission():
    for _ in range(3):
        led.value = True
        time.sleep(0.1)
        led.value = False
        time.sleep(0.1)
```

**2. Game Variations**

**Difficulty Levels:**
- Easy: 5-7 geese, 7 seconds to answer
- Medium: 10-15 geese, 5 seconds (current)
- Hard: 20+ geese, 3 seconds

**Multiple Rounds:**
Track scores across multiple rounds, crown overall winner.

**Team Mode:**
Players collaborate - game only accepts answer if all team members agree (all submit same number).

**3. Technical Improvements**

**Better State Management:**
Use a proper state machine library on server:
```python
from transitions import Machine

states = ['waiting', 'image_display', 'countdown', 'answering', 'finished']
transitions = [
    {'trigger': 'start', 'source': 'waiting', 'dest': 'image_display'},
    {'trigger': 'hide_image', 'source': 'image_display', 'dest': 'countdown'},
    # ...
]
```

**Improved Networking:**
- Add message acknowledgment for critical events
- Implement client-side message queue for offline resilience
- Use Redis for distributed state instead of in-memory dict

**Data Logging:**
Log all game events for analysis:
```python
import json
from datetime import datetime

def log_event(event_type, data):
    with open('game_log.jsonl', 'a') as f:
        f.write(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        }) + '\n')
```

**4. Accessibility**

**Multi-sensory Feedback:**
- Audio cues for countdown
- Haptic feedback via button vibration (if supported)
- High-contrast visual mode

**Difficulty Adjustments:**
- Slower countdown for users who need more time
- Larger images
- Adjustable answer time limits

**5. Spectator Experience**

**Large Display Mode:**
Create a fullscreen view optimized for projection:
- Bigger player displays
- More dramatic winner announcement
- Replay of winning moment
- Leaderboard across multiple games

**Implementation:**
```javascript
// game.html - add fullscreen mode
function enterFullscreen() {
    document.documentElement.requestFullscreen();
    document.body.classList.add('fullscreen-mode');
}
```

### Lessons Learned

**Distributed Systems:**
- Keep game logic centralized, distribute only input/output
- Always include connection status indicators
- Design for graceful degradation when components fail

**Physical Computing:**
- Physical interaction creates engagement digital can't match
- Debouncing and state management are critical
- Test with actual users - button feel matters

**Real-time Systems:**
- Visual feedback should be immediate even if game logic is deferred
- Broadcast important state changes, not just deltas
- Time synchronization is hard - embrace approximate timing

**Game Design:**
- Simple mechanics can create emergent complexity
- Real-time competition needs visible progress
- Physical actions should feel meaningful

---

## Conclusion

The Distributed Goose Counting Game successfully demonstrates key principles of distributed sensing and networked interaction. By combining physical buttons, MQTT messaging, and real-time web visualization, we created an engaging experience that highlights both the possibilities and challenges of distributed systems.

The project shows that meaningful collaborative experiences can emerge from simple sensor inputs when combined with good architecture and thoughtful game design. The real-time nature of the interaction created competitive excitement, while the distributed architecture allowed easy scaling to multiple players.

Testing revealed that physical interaction significantly enhances engagement compared to traditional keyboard/mouse input, and that real-time feedback creates psychological dynamics that make the experience more compelling.

Future work could expand this foundation into more complex collaborative games, explore team-based variants, or use the architecture for entirely different applications beyond gaming.