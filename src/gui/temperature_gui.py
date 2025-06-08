import utime
from machine import Pin
from gui.base_gui import BaseGUI

class TemperatureGUI(BaseGUI):
    """Temperature monitor and control GUI"""
    
    def __init__(self, lcd, select_button, up_button, down_button, led_pin=16):
        """Initialize the Temperature GUI"""
        # Pass the button objects to the parent class
        super().__init__(lcd, up_button, down_button, select_button)
        
        # Configure LED pin as output
        self.led = Pin(led_pin, Pin.OUT)
        
        # Default target temperature
        self.target_temp = 20.0
        
        # Flag to track if we're in temperature setting mode
        self.setting_mode = False
    
    def run(self):
        """Run the temperature GUI"""
        current_temp = 0.0
        last_display_update = 0
        
        # Initially display the current temperature
        current_temp = self.lcd.display_temp()
        self.update_temperature_indicators(current_temp)
        
        while True:
            # Check for simultaneous UP+DOWN press to exit
            if self.is_up_down_pressed():
                utime.sleep(0.2)  # Debounce
                return  # Exit the temperature screen
            
            # Toggle setting mode with SELECT
            if self.is_select_pressed():
                self.setting_mode = not self.setting_mode
                
                if self.setting_mode:
                    # Enter setting mode - display target temperature screen
                    self.display_target_temp()
                else:
                    # Exit setting mode - return to temperature display
                    current_temp = self.lcd.display_temp()
                    self.update_temperature_indicators(current_temp)
            
            # Handle actions based on current mode
            if self.setting_mode:
                # In target temperature setting mode
                if self.is_up_pressed():
                    # UP button pressed - increase target temp
                    self.target_temp += 0.5
                    self.display_target_temp()
                
                elif self.is_down_pressed():
                    # DOWN button pressed - decrease target temp
                    self.target_temp -= 0.5
                    self.display_target_temp()
            else:
                # In temperature display mode - periodically update reading
                current_time = utime.ticks_ms()
                if utime.ticks_diff(current_time, last_display_update) > 2000:  # Update every 2 seconds
                    current_temp = self.lcd.display_temp()
                    self.update_temperature_indicators(current_temp)
                    last_display_update = current_time
            
            # Update button states for next iteration
            self.update_button_states()
            utime.sleep(0.05)  # Small delay to prevent CPU overload
    
    def update_temperature_indicators(self, current_temp):
        """Update LED and temperature indicator based on current vs target temp"""
        # Control LED based on temperature threshold
        if current_temp > self.target_temp:
            # Turn on LED if temperature is above target (cooling needed)
            self.led.value(1)
            # Display cooling indicator
            self.lcd.move_to(15, 1)  # Bottom right corner
            self.lcd.putchar("-")
        else:
            # Turn off LED if temperature is at or below target
            self.led.value(0)
            # Display heating indicator
            self.lcd.move_to(15, 1)  # Bottom right corner
            self.lcd.putchar("+")
    
    def display_target_temp(self):
        """Display the target temperature setting screen"""
        self.lcd.clear()
        self.lcd.center_text("Target Temp:", 0)
        temp_str = f"{self.target_temp:.1f}\1C"
        self.lcd.center_text(temp_str, 1)
