# Distributed Goose Counting Game

**NAMES OF COLLABORATORS**

Maggie Liang(ml2927) Xueer Zhang(xz946) Xinwei Xie(xx2185)

---

**💡 Brainstorm 5 ideas for messaging between devices**
1) Shared Message Board

- Multiple devices in the same space can post short messages that are shown on every other device.
 This allows everyone to share thoughts or updates at the same time without needing direct replies.

2) Group Status Display

- Each device can send its current status, such as “working,” “break,” or “done.”
All devices display the group’s statuses together, so everyone can see what others are doing in the moment.

3) Synchronized Light Signals

- When one device changes its light color, all other devices change to the same color.
This creates a shared mood or environment across the space without needing any response.

4) Collective Timer

- One device can start a timer, and all devices show the same countdown.
Everyone in the room can keep time together without needing to interact individually.

5) Group Sound Cue

- Any device can send a signal that makes all devices play a short tone at the same time.
This works as a gentle way to signal transitions such as “begin,” “pause,” or “end.”
---

**📸 Screenshot of grid + photo of Pi setup**

https://github.com/user-attachments/assets/9430ed60-e22d-404a-9e72-f01f6ef819d6

https://github.com/user-attachments/assets/17feb416-5044-4a50-8106-d620ce534241

![7cb740ab2d2a78396c3e6b404f05435](https://github.com/user-attachments/assets/9dba8302-3326-4b44-a338-0cc8bba03b22)


---

## Part C: Make Your Own

## Project Description

### What does it do?

The Distributed Goose Counting Game is a collaborative counting challenge where multiple players use Raspberry Pi devices with physical buttons to compete in counting geese from an image. The system creates an engaging, real-time competitive experience using distributed hardware and networked communication.

**Game Flow:**
1. An image of geese is displayed for 5 seconds
2. After the image disappears, players wait through a 5-second countdown
3. When the countdown ends, players have 5 seconds to answer
4. Players press their button once for each goose they counted
5. After 5 seconds, the system automatically calculates each player's answer based on their total button presses
6. The first player with the correct answer wins

### Why is it interesting?

This project demonstrates distributed sensing and real-time collaboration in several ways:

**Real-time Feedback:** After the 5-second answer period, all players' answers are revealed simultaneously on the web interface, creating anticipation and excitement.

**Physical-Digital Bridge:** The game combines physical button pressing with digital visualization, making abstract networked systems tangible and fun.

**Collaborative Competition:** While players compete individually, the system only works when multiple people participate together, demonstrating the power of networked devices.

### User Experience

Players experience the game in three phases:

**Observation Phase:** Tension builds as players quickly count geese while the image is visible. The time pressure creates urgency.

**Waiting Phase:** The countdown creates anticipation. Players must remember their count while watching the timer.

**Action Phase:** Players frantically press buttons to enter their count within the 5-second window. They cannot see other players' progress during this time, adding tension. When time expires, all answers are revealed simultaneously, creating a dramatic moment of truth.

The physical button creates a more engaging experience than keyboard input - each press feels meaningful and the pressure of the ticking clock creates urgency.

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

The system tracks all button presses during the 5-second answer window and automatically calculates each player's final answer when time expires.

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

**Press Detection:**
```python
# Button pressed (state changed to 0x00 or similar)
if new_state == 0x00 or new_state < 0x80:
    # Debounce
    if current_time - last_press_time > DEBOUNCE_TIME:
        # Publish button press
        payload = json.dumps({
            'mac': mac,
            'ip': ip,
            'timestamp': int(current_time)
        })
        
        client.publish(MQTT_TOPIC_BUTTON, payload)
        print(f'Button pressed')
        
        last_press_time = current_time
```

**Explanation:** Each button press is immediately published to MQTT. The server tracks all presses during the 5-second answer window and counts them to determine the final answer. Debouncing prevents multiple triggers from mechanical bounce.

#### 2. MQTT Bridge (mqtt_game_bridge.py)

**Message Forwarding:**
```python
def on_message(client, userdata, msg):
    """MQTT message received - forward to WebSocket"""
      socketio = userdata['socketio']
      game_state = userdata['game_state']
        
      data = json.loads(msg.payload.decode('UTF-8'))

      if msg.topic.endswith('/button'):
         mac = data.get('mac')
         ip = data.get('ip', 'unknown')
            
         print(f'Button press from {mac[:17]}')
            
            # Forward to Socket.IO
         socketio.emit('button_press', {
            'mac': mac,
            'ip': ip,
            'timestamp': datetime.now().isoformat()
         }, namespace='/')

```

**Explanation:** This bridge converts MQTT messages to Socket.IO events. It maintains the game state and routes button press messages to the game server. The namespace='/' ensures messages reach all connected web clients.

#### 3. Game Logic (real_game_app.py)

**Click Tracking:**
```python
@socketio.on('button_press')
def handle_button_press(data):
    """Handle button press from Pi"""
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
        
        
   game_state['players'][mac]['clicks'] += 1
   clicks = game_state['players'][mac]['clicks']
        
   emit('player_click', {
      'mac': mac,
      'name': game_state['players'][mac]['name'],
      'ip': ip,
      'clicks': clicks
      }, broadcast=True)
        
   print(f'{game_state["players"][mac]["name"]}: Click {clicks}')
        
```

**Explanation:** Tracks each button press per player. Only counts clicks during the 'answering' phase. Click counts are stored server-side but NOT broadcast in real-time - they remain hidden until the answer phase ends.


#### 4. Real-time Display (game.html)

**Dynamic Player Display:**
```javascript
function updatePlayerDisplay(mac, isWinner = false) {
    const cleanMac = mac.replace(/:/g, '');
    const player = players[mac];
    
    const answerDiv = document.getElementById('answer-' + cleanMac);
    const timeDiv = document.getElementById('time-' + cleanMac);
    const playerDiv = document.getElementById('player-' + cleanMac);
    
    if (!answerDiv) return;
    
    // Only show results after answer phase ends
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
        // During answer phase, show waiting status
        answerDiv.textContent = 'Answering...';
    }
}
```

**Explanation:** Updates player display only after the answer phase ends. Results are revealed all at once when time expires and calculation is processed.

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

**What happened:**  
Both participants counted the objects shown on the screen and pressed their buttons to submit answers.  
Participant 1 pressed 14 times(around 4+s).  
Participant 2 pressed 14 times and finished faster (around 3.9s). 
Participant 3 pressed 13 times and hesitated near the end.  
Participant 2’s answer was correct and won the round.

**What surprised them:**  
- **Participant 2:** “Not knowing the other player’s progress made it intense.”  
- **Participant 3:** “It was easy to lose count under pressure.”  

**What they would change:**  
- **Participant 2:** Suggested adding a short practice round first.  
- **Participant 3:** Suggested showing a small indicator light to confirm each button press.

### Testing 1

https://github.com/user-attachments/assets/7646f039-6b00-4ae2-8e54-1c73d6dce203

### User Testing 1

https://github.com/user-attachments/assets/aa9c5ec4-bc55-48c8-9350-8526f325dfd6

### User Testing 2

https://github.com/user-attachments/assets/660b6aed-262f-4fb2-8c41-6d66e4e6a725


### Testing Insights

**Key Observations:**

1. **Learning Curve:** First-time users needed 1-2 rounds to understand the mechanics, especially the importance of counting accurately while pressing.

2. **Psychological Factors:** NOT seeing other players' progress created different kind of tension - uncertainty about relative performance rather than direct comparison.

3. **Physical Engagement:** All users commented that physical buttons made the experience more engaging than keyboard/mouse input.

4. **Timing Balance:** The 5-second answer phase was well-balanced - enough time to be careful, short enough to be exciting.

5. **Memory Challenge:** The delay between viewing and answering made the game more challenging and interesting.

**Common Feedback Themes:**

- **Positive:**
  - Physical interaction was satisfying
  - Hidden progress increased suspense
  - Simultaneous reveal was exciting
  - Simple to understand core mechanic

- **Suggestions for Improvement:**
  - Add practice round
  - Audio feedback for button presses
  - Multiple difficulty levels
  - Optional modes (hidden vs visible progress)
  - Tournament mode

---

## Reflection

### What Worked Well

**1. Distributed Architecture**

The MQTT-based architecture proved robust and scalable. Adding new Pis was simple - just run the client script. The pub/sub model meant players didn't need to know about each other directly, making the system flexible.

**Technical Success:**
- No message loss during testing
- Handled 3 concurrent players easily
- Could scale to 10+ with no code changes

**2. Delayed Result Reveal**

Socket.IO enabled synchronized result display across all clients. After the 5-second answer period, results were revealed simultaneously to all players, creating a dramatic moment.

**User Experience Success:**
- Hidden progress increased tension and focus
- Simultaneous reveal created excitement
- Synchronized countdown across all clients

**3. Physical Button Interaction**

Using real I2C buttons instead of keyboard/mouse input made the experience significantly more engaging. The tactile feedback and the need to count accurately while pressing created meaningful physical interaction.

**Engagement Success:**
- Each press felt tangible and meaningful
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

**1. Timing Coordination**

**Challenge:** Coordinating countdown timers across multiple clients when server controls game flow but clients display it.

**Issue Encountered:**
- Client-side countdown could drift from server-side game phase
- Network latency could cause countdown to be slightly off

**Solution:**
- Server broadcasts phase changes, clients start timers on receipt
- Timers are visual only - game logic runs server-side
- Acceptable to have slight visual drift (human perception tolerance)

**Remaining Issue:**
- Could be more accurate for time counting

**2. Player Identity**

**Challenge:** Tracking which Pi belongs to which player across disconnects.

**Issue Encountered:**
- If Pi disconnected and reconnected, it got a new player number
- IP address was reliable but not user-friendly for display
- No way to assign human-readable names from Pi side

**Solution:**
- Used MAC address as consistent identifier
- Auto-assigned player numbers on first appearance
- Stored player data keyed by MAC address

**What We'd Improve:**
- Add player name registration phase before game starts
- Allow manual name entry on Pi or web interface
- Persist player identities across game resets


### How Sensor Events Worked

**Event Detection:**

The I2C button sensor reports state changes reliably. 

**What Worked:**
- Simple state machine (pressed/released) was enough
- Hold detection by timing between press and release was intuitive

**What Was Tricky:**
- Initial reads sometimes returned garbage values
- I2C bus conflicts if not properly locked
- Button state varied slightly between different button models

**Event Processing:**

Converting button events to game actions was straightforward:

```python
# Each press → increment count
if new_state == pressed and debounce_okay:
    publish('button')  # Server tracks count
    
# After 5 seconds → calculate final answer from total presses
```

**Design Decision:**
- Click count tracked server-side, not on Pi
- Pi only reports press events
- Results hidden until answer phase ends
- This kept Pi code simple and allowed server to control reveal timing

**Alternative Considered:**
- Show real-time click progress to all players
- Rejected because: reduces suspense, creates pressure to rush, eliminates strategic element

### What We Would Improve

**1. User Experience Enhancements**

**Practice Mode:**
Add a practice round with no timer pressure where users can learn the button mechanics.

**Audio Feedback:**
- Beep sound for each button press to help count
- Different tone for invalid presses (during wrong phase)
- Dramatic reveal sound when results display

**Visual Feedback on Pi:**
```python
# On Pi side - add LED feedback
import board
import digitalio

led = digitalio.DigitalInOut(board.D18)
led.direction = digitalio.Direction.OUTPUT

def indicate_press():
    led.value = True
    time.sleep(0.05)
    led.value = False
```

**2. Game Variations**

**Difficulty Levels:**
- Easy: 5-7 geese, 3 seconds to answer
- Medium: 10-15 geese, 5 seconds (current)
- Hard: 20+ geese, 7 seconds

**Multiple Rounds:**
Track scores across multiple rounds, crown overall winner.


### Lessons Learned

From a game design perspective, the project demonstrated how simple mechanics can generate emergent complexity. The basic interaction - pressing a button to count - became strategically rich through the addition of time pressure and memory challenges. 

---

Resources: [MQTT Guide](https://www.hivemq.com/mqtt-essentials/) | [Paho Python](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php) | [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
