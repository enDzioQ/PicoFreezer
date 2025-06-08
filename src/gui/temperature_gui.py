import utime
from machine import Pin
from gui.base_gui import BaseGUI

class TemperatureGUI(BaseGUI):
    """Temperature monitor and control GUI"""
    
    def __init__(self, lcd, select_button, up_button, down_button, temp_monitor):
        """Initialize the Temperature GUI"""
        # Pass the button objects to the parent class
        super().__init__(lcd, up_button, down_button, select_button)
        
        # Link to the temperature monitor
        self.temp_monitor = temp_monitor
        
        # Flag to track if we're in temperature setting mode
        self.setting_mode = False
    
    def run(self):
        """Run the temperature GUI"""
        current_temp = 0.0
        last_display_update = 0
        
        # Initially display the current temperature
        current_temp = self.temp_monitor.get_current_temp()
        self.display_temperature(current_temp)
        
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
                    current_temp = self.temp_monitor.get_current_temp()
                    self.display_temperature(current_temp)
            
            # Handle actions based on current mode
            if self.setting_mode:
                # In target temperature setting mode
                if self.is_up_pressed():
                    # UP button pressed - increase target temp
                    new_target = self.temp_monitor.get_target_temp() + 0.5
                    self.temp_monitor.set_target_temp(new_target)
                    self.display_target_temp()
                
                elif self.is_down_pressed():
                    # DOWN button pressed - decrease target temp
                    new_target = self.temp_monitor.get_target_temp() - 0.5
                    self.temp_monitor.set_target_temp(new_target)
                    self.display_target_temp()
            else:
                # In temperature display mode - periodically update reading
                current_time = utime.ticks_ms()
                if utime.ticks_diff(current_time, last_display_update) > 2000:  # Update every 2 seconds
                    current_temp = self.temp_monitor.get_current_temp()
                    self.display_temperature(current_temp)
                    last_display_update = current_time
            
            # Update button states for next iteration
            self.update_button_states()
            utime.sleep(0.05)  # Small delay to prevent CPU overload
    
    def display_temperature(self, current_temp):
        """Display current temperature with appropriate indicator"""
        # Get target temperature from monitor
        target_temp = self.temp_monitor.get_target_temp()
        
        # Determine indicator based on temperature comparison
        indicator = "-" if current_temp > target_temp else "+"
        
        # Use LCD to display temperature with indicator
        self.lcd.display_temperature_screen(f"{current_temp:.1f}", indicator)
    
    def display_target_temp(self):
        """Display the target temperature setting screen"""
        target_temp = self.temp_monitor.get_target_temp()
        self.lcd.display_target_temp_screen(target_temp)
