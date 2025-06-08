import _thread
import utime
from machine import Pin

class TemperatureMonitor:
    def __init__(self, ds_sensor, led_pin=16):
        """Initialize the temperature monitor"""
        self.ds_sensor = ds_sensor
        self.led = Pin(led_pin, Pin.OUT)
        
        # Get initial temperature right away instead of starting at 0.0
        initial_temp = self.ds_sensor.get_temperature()
        self.current_temp = initial_temp if initial_temp is not None else 0.0
        
        self.target_temp = 20.0
        
        # Lock for thread-safe access to shared data
        self.lock = _thread.allocate_lock()
        
        # Flag to control the monitoring thread
        self.running = True
        
        # Thread identifier for better control
        self.thread_id = None
        
        print(f"Temperature monitor initialized with temperature: {self.current_temp}°C")
    
    def start_monitoring(self):
        """Start the monitoring thread on the second core"""
        if self.thread_id is None:  # Only start if not already running
            self.running = True
            self.thread_id = _thread.start_new_thread(self._monitor_loop, ())
            print("Temperature monitoring thread started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        print("Stopping temperature monitoring...")
        self.running = False
        
        # Turn off the LED when stopping
        with self.lock:
            self.led.value(0)
    
    def _monitor_loop(self):
        """Continuous monitoring loop (runs on second core)"""
        print("Temperature monitoring started on Core 1")
        
        while self.running:
            try:
                # Measure temperature
                temp = self.ds_sensor.get_temperature()
                
                # Update current temperature (thread-safe)
                with self.lock:
                    if temp is not None:
                        self.current_temp = temp
                        print(f"Temperature update: {self.current_temp}°C")
                    else:
                        print("Temperature sensor returned None")
                    
                    # Control LED based on temperature threshold
                    if self.current_temp > self.target_temp:
                        self.led.value(1)  # Turn on cooling
                    else:
                        self.led.value(0)  # Turn off cooling
                
                # Sleep to avoid excessive readings
                utime.sleep(1)
                
                # Check if we should exit more frequently
                if not self.running:
                    break
                    
            except Exception as e:
                print(f"Error in temperature monitor: {e}")
                utime.sleep(5)  # Wait a bit longer if there's an error
                
        print("Temperature monitoring stopped on Core 1")
    
    def get_current_temp(self):
        """Get the current temperature (thread-safe)"""
        with self.lock:
            return self.current_temp
    
    def set_target_temp(self, target):
        """Set the target temperature (thread-safe)"""
        with self.lock:
            self.target_temp = target
    
    def get_target_temp(self):
        """Get the target temperature (thread-safe)"""
        with self.lock:
            return self.target_temp
