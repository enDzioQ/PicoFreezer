import _thread
import utime
from machine import Pin
from web.server import WebServer

class TemperatureMonitor:
    """Manages temperature monitoring and control using a DS sensor and LED indicator."""

    def __init__(self, ds_sensor, led_pin=16, wifi_manager=None):
        """Initialize the temperature monitor"""
        self.ds_sensor = ds_sensor
        self.led = Pin(led_pin, Pin.OUT)
        
        self.wifi_manager = wifi_manager
        self.web_server = None
        
        self.wifi_connected = False if wifi_manager is None else wifi_manager.is_connected()
        
        initial_temp = self.ds_sensor.get_temperature()
        self.current_temp = initial_temp if initial_temp is not None else 0.0
        
        self.target_temp = 20.0
        
        self.lock = _thread.allocate_lock()
        
        self.running = True
        
        self.thread_id = None
        
    
    def set_web_server(self, web_server):
        """Set reference to web server"""
        self.web_server = web_server
    
    def start_monitoring(self):
        """Start the monitoring thread on the second core"""
        if self.thread_id is None:  # Only start if not already running
            self.running = True
            self.thread_id = _thread.start_new_thread(self._monitor_loop, ())
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.running = False
        
        # Turn off the LED when stopping
        with self.lock:
            self.led.value(0)
    
    def _monitor_loop(self):
        """Continuous monitoring loop (runs on second core)"""
        while self.running:
            try:
                # Measure temperature
                temp = self.ds_sensor.get_temperature()
                
                # Update current temperature (thread-safe)
                with self.lock:
                    if temp is not None:
                        self.current_temp = temp
                    
                    # Control LED based on temperature threshold
                    if self.current_temp > self.target_temp:
                        self.led.value(1)  # Turn on cooling
                    else:
                        self.led.value(0)  # Turn off cooling
                
                # Check WiFi status and manage web server
                self._manage_web_server()
                
                # Sleep to avoid excessive readings
                utime.sleep(1)
                
                # Check if we should exit more frequently
                if not self.running:
                    break
                    
            except Exception as e:
                print(f"Error in temperature monitor: {e}")
                utime.sleep(5)  # Wait a bit longer if there's an error
    
    def _manage_web_server(self):
        """Manage the web server based on WiFi connection status"""
        if not self.wifi_manager:
            return
        
        # Get current WiFi connection status
        current_status = self.wifi_manager.is_connected()
        
        # Check for status changes
        if current_status != self.wifi_connected:
            if current_status:
                # WiFi connected - start server
                print("WiFi connection detected - starting web server")
                self._start_web_server()
            else:
                # WiFi disconnected - stop server
                print("WiFi disconnection detected - stopping web server")
                self._stop_web_server()
            
            # Update tracked status
            self.wifi_connected = current_status
        
        # If server is running, process client requests
        if self.web_server and self.web_server.is_running:
            self.web_server.update()
    
    def _start_web_server(self):
        """Start the web server if not already running"""
        if self.web_server is None:
            # Create new web server instance
            self.web_server = WebServer(self.wifi_manager, self)
            
        # Start the server if created successfully
        if self.web_server and not self.web_server.is_running:
            self.web_server.start()
    
    def _stop_web_server(self):
        """Stop the web server if running"""
        if self.web_server and self.web_server.is_running:
            self.web_server.stop()
    
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
