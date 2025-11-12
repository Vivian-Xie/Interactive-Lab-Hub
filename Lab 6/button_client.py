#!/usr/bin/env python3
"""
Goose Game Button Client for Raspberry Pi
Reads I2C button and publishes to MQTT
"""

import board
import busio
import time
import paho.mqtt.client as mqtt
import json
import uuid
import subprocess

# MQTT Configuration
MQTT_BROKER = 'farlab.infosci.cornell.edu'
MQTT_PORT = 1883
MQTT_TOPIC_BUTTON = 'IDD/goose/button'
MQTT_USERNAME = 'idd'
MQTT_PASSWORD = 'device@theFarm'

# Button I2C address
BUTTON_ADDRESS = 0x6f

# Debounce settings
DEBOUNCE_TIME = 0.3  # seconds
last_press_time = 0


def get_mac_address():
    """Get MAC address of the Pi"""
    try:
        result = subprocess.run(['cat', '/sys/class/net/eth0/address'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        
        result = subprocess.run(['cat', '/sys/class/net/wlan0/address'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"Error getting MAC: {e}")
    
    return str(uuid.uuid1())


def get_ip_address():
    """Get IP address of the Pi"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


def on_connect(client, userdata, flags, rc):
    """MQTT connected"""
    if rc == 0:
        print(f'✓ Connected to MQTT broker')
    else:
        print(f'✗ Connection failed: {rc}')


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


def main():
    print("=" * 60)
    print("  Goose Game Button Client")
    print("=" * 60)
    
    # Get device info
    mac = get_mac_address()
    ip = get_ip_address()
    
    print(f"MAC: {mac}")
    print(f"IP: {ip}")
    print()
    
    # Setup I2C
    print("Initializing I2C button...")
    i2c = busio.I2C(board.SCL, board.SDA)
    print("✓ I2C ready")
    
    # Setup MQTT
    print("Connecting to MQTT broker...")
    client = mqtt.Client(str(uuid.uuid1()))
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    
    try:
        client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=60)
        client.loop_start()
        time.sleep(2)
        print("✓ MQTT connected")
    except Exception as e:
        print(f"✗ MQTT connection failed: {e}")
        return
    
    print("=" * 60)
    print("Press button to count geese!")
    print("Each press counts as one goose")
    print("After 5 seconds, your answer is automatically submitted")
    print("=" * 60)
    print()
    
    global last_press_time
    button_state = None
    
    # Main loop
    while True:
        try:
            # Read button
            new_state = read_button(i2c)
            
            if new_state is not None and new_state != button_state:
                current_time = time.time()
                
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
                
                button_state = new_state
            
            time.sleep(0.05)  # 50ms polling
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.1)
    
    # Cleanup
    client.loop_stop()
    client.disconnect()
    print("Goodbye!")


if __name__ == '__main__':
    main()