from flask import Flask, render_template
from flask_socketio import SocketIO
import os
import random
import time
import threading
import math
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app)

class DroneTelemetry:
    def __init__(self):
        self.altitude = 0
        self.speed = 0
        self.vspeed = 0
        self.accel = 0
        self.heading = 0
        self.gps = {'lat': 0, 'lon': 0}
        self.satellites = 0
        self.running = False
        self.altitude_history = []

    def update_telemetry(self):
        self.running = True
        start_time = time.time()
        
        while self.running:
            current_time = time.time() - start_time
            self.altitude = 100 + 50 * math.sin(current_time * 0.5)
            self.speed = 50 + 20 * math.sin(current_time * 0.3)
            self.vspeed = 2 * math.sin(current_time * 0.4)
            self.accel = 1 + 0.5 * math.sin(current_time * 0.2)
            self.heading = (self.heading + 0.5) % 360
            self.gps = {
                'lat': 40.7128 + 0.1 * math.sin(current_time * 0.1),
                'lon': -74.0060 + 0.1 * math.cos(current_time * 0.1)
            }
            self.satellites = random.randint(8, 12)
            
            self.altitude_history.append(self.altitude)
            if len(self.altitude_history) > 50:
                self.altitude_history.pop(0)
            
            telemetry_data = {
                'time': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                'altitude': self.altitude,
                'speed': self.speed,
                'vspeed': self.vspeed,
                'accel': self.accel,
                'heading': self.heading,
                'gps_lat': self.gps['lat'],
                'gps_lon': self.gps['lon'],
                'satellites': self.satellites,
                'altitude_history': self.altitude_history.copy()
            }
            
            socketio.emit('telemetry_update', telemetry_data)
            time.sleep(0.1)

drone = DroneTelemetry()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    if not hasattr(drone, 'running') or not drone.running:
        thread = threading.Thread(target=drone.update_telemetry)
        thread.daemon = True
        thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)