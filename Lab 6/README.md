# Distributed Interaction

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

**Requirements:**
- 3+ people, 3+ Pis
- Each Pi contributes sensor input via MQTT
- Meaningful or fun interaction

**Ideas:**

**Sensor Fortune Teller**
- Each Pi sends 0-255 from different sensor
- Server generates fortunes from combined values

**Frankenstories**
- Sensor events → story elements (not text!)
- Red = danger, gesture up = climbed, distance <10cm = suddenly

**Distributed Instrument**
- Each Pi = one musical parameter
- Only works together

**Others:** Games, presence display, mood ring

### Deliverables

Replace this README with your documentation:

**1. Project Description**
- What does it do? Why interesting? User experience?

**2. Architecture Diagram**

<img width="616" height="629" alt="c2de4accd94229364e73879a1c5d8e3" src="https://github.com/user-attachments/assets/2b12516e-def2-4525-939b-60f521e4e87c" />


**3. Build Documentation**
- Photos of each Pi + sensors
- MQTT topics used
- Code snippets with explanations

**4. User Testing**
- **Test with 2+ people NOT on your team**
- Photos/video of use
- What did they think before trying?
- What surprised them?
- What would they change?

**5. Reflection**
- What worked well?
- Challenges with distributed interaction?
- How did sensor events work?
- What would you improve?


### Testing 1
https://github.com/user-attachments/assets/a9d74778-893c-4d91-8b11-2e72ff25f5da

### User Testing 1
https://github.com/user-attachments/assets/2b5bb2d8-72ad-48e9-819f-fdd2e0fd6321

### User Testing 2
https://github.com/user-attachments/assets/b0d23fea-0d8a-4a87-b16d-be9ef3f5b92b




---

## Code Files

**Server files:**
- `app.py` - Pixel grid server (Flask + WebSocket + MQTT)
- `mqtt_viewer.py` - MQTT message viewer for debugging
- `mqtt_bridge.py` - MQTT → WebSocket bridge
- `requirements-server.txt` - Server dependencies

**Pi files:**
- `pixel_grid_publisher.py` - Example (RGB sensor → MQTT)
- `requirements-pi.txt` - Pi dependencies

**Web interface:**
- `templates/grid.html` - Pixel grid display
- `templates/controller.html` - Color picker
- `templates/mqtt_viewer.html` - Message viewer

---

## Debugging Tools

**MQTT Message Viewer:** `http://farlab.infosci.cornell.edu:5001`
- See all MQTT messages in real-time
- View topics and payloads
- Helpful for debugging your own projects

**Command line:**
```bash
# See all IDD messages
mosquitto_sub -h farlab.infosci.cornell.edu -p 1883 -t "IDD/#" -u idd -P "device@theFarm"
```

---

## Troubleshooting

**MQTT:** Broker `farlab.infosci.cornell.edu:1883`, user `idd`, pass `device@theFarm`

**Sensor:** Check `i2cdetect -y 1`, APDS-9960 at `0x39`

**Grid:** Verify server running, check MQTT in console, test with web controller

**Pi venv:** Make sure to activate: `source .venv/bin/activate`


---

## Submission Checklist

Before submitting:
- [ ] Delete prep/instructions above
- [ ] Add YOUR project documentation
- [ ] Include photos/videos/diagrams  
- [ ] Document user testing with non-team members
- [ ] Add reflection on learnings
- [ ] List team names at top

**Your README = story of what YOU built!**

---

Resources: [MQTT Guide](https://www.hivemq.com/mqtt-essentials/) | [Paho Python](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php) | [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
