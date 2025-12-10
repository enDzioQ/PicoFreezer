import utime
from machine import Pin
from gui.base_gui import BaseGUI

class TemperatureGUI(BaseGUI):
    """Temperature monitor and control GUI"""
    
    def __init__(self, lcd, select_button, up_button, down_button, temp_monitor):
        """Initialize the Temperature GUI"""
        super().__init__(lcd, up_button, down_button, select_button)
        
        self.temp_monitor = temp_monitor
        
        self.setting_mode = False
    
    def run(self):
        """Run the temperature GUI"""
        current_temp = 0.0
        last_display_update = 0
        
        current_temp = self.temp_monitor.get_current_temp()
        self.display_temperature(current_temp)
        
        while True:
            if self.is_up_down_pressed():
                utime.sleep(0.2)  # Debounce
                return
            
            if self.is_select_pressed():
                self.setting_mode = not self.setting_mode
                
                if self.setting_mode:
                    self.display_target_temp()
                else:
                    current_temp = self.temp_monitor.get_current_temp()
                    self.display_temperature(current_temp)
            
            if self.setting_mode:
                if self.is_up_pressed():
                    new_target = self.temp_monitor.get_target_temp() + 0.5
                    self.temp_monitor.set_target_temp(new_target)
                    self.display_target_temp()
                
                elif self.is_down_pressed():
                    new_target = self.temp_monitor.get_target_temp() - 0.5
                    self.temp_monitor.set_target_temp(new_target)
                    self.display_target_temp()
            else:
                current_time = utime.ticks_ms()
                if utime.ticks_diff(current_time, last_display_update) > 2000:  # Update every 2 seconds
                    current_temp = self.temp_monitor.get_current_temp()
                    self.display_temperature(current_temp)
                    last_display_update = current_time
            
            self.update_button_states()
            utime.sleep(0.05)  # Small delay to prevent CPU overload
    
    def display_temperature(self, current_temp):
        """Display current temperature with appropriate indicator"""
        target_temp = self.temp_monitor.get_target_temp()
        
        indicator = "-" if current_temp > target_temp else "+"
        
        self.lcd.display_temperature_screen(f"{current_temp:.1f}", indicator)
    
    def display_target_temp(self):
        """Display the target temperature setting screen"""
        target_temp = self.temp_monitor.get_target_temp()
        self.lcd.display_target_temp_screen(target_temp)
