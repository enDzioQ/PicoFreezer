import utime

class TemperatureGUI:
    def __init__(self, lcd, select_button):
        """Initialize the Temperature GUI with LCD and select button"""
        self.lcd = lcd
        self.select_button = select_button
    
    def show_temperature(self):
        """Display temperature measurement with return option"""
        # Show temperature until button is pressed
        while True:
            self.lcd.display_temp()
            
            # Check if select button is pressed to return to menu
            if self.select_button.value() == 0:  # Button pressed (active low with pull-up)
                utime.sleep(0.2)  # Debounce
                break
