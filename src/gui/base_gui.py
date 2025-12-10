from machine import Pin
import utime

class BaseGUI:
    """Base class for all GUI screens with common button handling"""
    
    def __init__(self, lcd, up_pin=13, down_pin=15, select_pin=14):
        """Initialize the base GUI with LCD and button pins"""
        self.lcd = lcd
        
        if isinstance(up_pin, Pin):
            self.up_button = up_pin
        else:
            self.up_button = Pin(up_pin, Pin.IN, Pin.PULL_UP)
            
        if isinstance(down_pin, Pin):
            self.down_button = down_pin
        else:
            self.down_button = Pin(down_pin, Pin.IN, Pin.PULL_UP)
            
        if isinstance(select_pin, Pin):
            self.select_button = select_pin
        else:
            self.select_button = Pin(select_pin, Pin.IN, Pin.PULL_UP)
        
        # Button state tracking for edge detection
        self.last_up_state = 1
        self.last_down_state = 1
        self.last_select_state = 1
    
    def is_up_pressed(self):
        """Detect rising edge on the up button"""
        current_state = self.up_button.value()
        if current_state == 0 and self.last_up_state == 1:
            self.last_up_state = 0
            utime.sleep(0.2)  # Debounce
            return True
        elif current_state == 1 and self.last_up_state == 0:
            self.last_up_state = 1
        return False
    
    def is_down_pressed(self):
        """Detect rising edge on the down button"""
        current_state = self.down_button.value()
        if current_state == 0 and self.last_down_state == 1:
            self.last_down_state = 0
            utime.sleep(0.2)  # Debounce
            return True
        elif current_state == 1 and self.last_down_state == 0:
            self.last_down_state = 1
        return False
    
    def is_select_pressed(self):
        """Detect rising edge on the select button"""
        current_state = self.select_button.value()
        if current_state == 0 and self.last_select_state == 1:
            self.last_select_state = 0
            utime.sleep(0.2)  # Debounce
            return True
        elif current_state == 1 and self.last_select_state == 0:
            self.last_select_state = 1
        return False
    
    def is_up_down_pressed(self):
        """Check if both up and down buttons are pressed simultaneously"""
        return self.up_button.value() == 0 and self.down_button.value() == 0
    
    def update_button_states(self):
        """Update the last button states"""
        self.last_up_state = self.up_button.value()
        self.last_down_state = self.down_button.value()
        self.last_select_state = self.select_button.value()
    
    def run(self):
        """Main loop for GUI operation (to be overridden by subclasses)"""
        raise NotImplementedError("Subclasses must implement run()")
