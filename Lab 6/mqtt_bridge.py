"""
MQTT Bridge for Goose Game
Connects physical buttons to the game via MQTT
"""

import paho.mqtt.client as mqtt
import json
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = 'farlab.infosci.cornell.edu'
MQTT_PORT = 1883
MQTT_TOPIC = 'IDD/goose/#'  # Subscribe to all goose game topics
MQTT_USERNAME = 'idd'
MQTT_PASSWORD = 'device@theFarm'

mqtt_client = None


def on_connect(client, userdata, flags, rc):
    """MQTT connected"""
    if rc == 0:
        print(f'✓ MQTT connected to {MQTT_BROKER}:{MQTT_PORT}')
        client.subscribe(MQTT_TOPIC)
        print(f'✓ Subscribed to {MQTT_TOPIC}')
    else:
        print(f'✗ MQTT connection failed: {rc}')


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


def start_mqtt_bridge(socketio_instance, game_state_dict):
    """Start MQTT client that forwards to WebSocket"""
    global mqtt_client
    
    try:
        import uuid
        mqtt_client = mqtt.Client(str(uuid.uuid1()))
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.user_data_set({
            'socketio': socketio_instance,
            'game_state': game_state_dict
        })
        
        mqtt_client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
        
        print('MQTT bridge started')
        return True
        
    except Exception as e:
        print(f'⚠️  MQTT bridge failed: {e}')
        return False


def stop_mqtt_bridge():
    """Stop MQTT client"""
    global mqtt_client
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print('MQTT bridge stopped')