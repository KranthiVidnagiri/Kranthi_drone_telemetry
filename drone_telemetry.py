import os
import time
import random
import math
import sys
from datetime import datetime
from collections import deque

class DroneTelemetry:
    def __init__(self):
        self.running = True
        self.start_time = time.time()
        
        self.altitude = 0.0  # meters
        self.speed = 0.0     # km/h
        self.battery = 100.0  # percentage
        self.latitude = -35.363261  # Coordinates from the image
        self.longitude = 149.165230
        self.heading = 0  # degrees
        self.vspeed = 0.0  # Vertical speed m/s
        self.satellites = 10  # Number of GPS satellites
        
        self.altitude_history = deque(maxlen=20)
        for _ in range(20):
            self.altitude_history.append(0)
            
        self.directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        
        if os.name == 'nt':
            import msvcrt
        
    def update_telemetry(self):
        elapsed = time.time() - self.start_time
        
        old_altitude = self.altitude
        self.altitude = 431.0 + random.uniform(-1, 1)  # From the image
        self.vspeed = (self.altitude - old_altitude) * 10  # Scale for better visibility
        self.speed = 161.0 + random.uniform(-1, 1)  # From the image
        self.battery = 100.0  # From the image
        
        self.heading = (self.heading + random.uniform(-5, 5)) % 360
        
        self.altitude_history.append(self.altitude)
        
        return elapsed < 30  # Run for 30 seconds
    
    def draw_altitude_graph(self, height=5):
        if len(self.altitude_history) < 2:
            return
            
        min_alt = min(self.altitude_history)
        max_alt = max(self.altitude_history)
        if max_alt == min_alt:
            max_alt += 1
            
        graph = []
        for i in range(height):
            level = max_alt - (max_alt - min_alt) * i / (height - 1)
            row = []
            for alt in self.altitude_history:
                if alt >= level:
                    row.append('*')
                else:
                    row.append(' ')
            graph.append(''.join(row))
            
        return graph
    
    def draw_compass(self, size=7):
        compass = []
        center = size // 2
        
        for _ in range(size):
            compass.append([' '] * size)
            
        compass[0][center] = 'N'
        compass[center][-1] = 'E'
        compass[-1][center] = 'S'
        compass[center][0] = 'W'
        
        rad = math.radians(self.heading)
        dx = int(round(math.sin(rad) * (center - 1)))
        dy = -int(round(math.cos(rad) * (center - 1)))
        compass[center + dy][center + dx] = 'o'
        
        return [''.join(row) for row in compass]
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def draw_display(self, elapsed):
        self.clear_screen()
        
        print(" " * 20 + "DRONE TELEMETRY")
        print("-" * 60)
        
        print(f"{'ALTITUDE':<15}{self.altitude:6.1f} m")
        print(" " * 10 + "^")
        
        graph = self.draw_altitude_graph(5)
        for line in graph:
            print(" " * 10 + "|" + line)
        print(" " * 10 + "|" + "-" * 20 + " Time")
        
        print(f"\n{'SPEED':<15}{self.speed:6.1f} km/h")
        print(f"{'VSI':<15}{self.vspeed:6.1f} m/s")
        
        print("\n" + " " * 25 + "N")
        print(" " * 25 + "|")
        
        compass = self.draw_compass(5)
        for line in compass:
            print(" " * 20 + line)
            
        print(f"{'GPS:':<15}{self.latitude:.6f}° N")
        print(f"{'':<15}{self.longitude:.6f}° E")
        
        print(f"\n{'BATTERY:':<15}{self.battery:3.0f}%")
        print(f"{'GPS SAT:':<15}{self.satellites}")
        
        print(f"\n{'TIME:':<15}{elapsed:5.1f}s / 30.0s")
        
        print("\nPress 'q' to quit")
    
    def check_key_press(self):
        if os.name == 'nt':
            return msvcrt.kbhit() and msvcrt.getch() in [b'q', b'Q']
        else:
            import select
            return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []) and sys.stdin.read(1) in ['q', 'Q']
    
    def run(self):
        try:
            if os.name != 'nt':
                import tty, termios
                old_settings = termios.tcgetattr(sys.stdin)
                tty.setcbreak(sys.stdin.fileno())
            
            while True:
                elapsed = time.time() - self.start_time
                
                if not self.update_telemetry():
                    break
                
                self.draw_display(elapsed)
                
                if self.check_key_press():
                    break
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            pass
        finally:
            if os.name != 'nt':
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print("\nDrone telemetry simulation ended.")

def main():
    try:
        telemetry = DroneTelemetry()
        telemetry.run()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
