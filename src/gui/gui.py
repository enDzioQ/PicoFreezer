from machine import Pin
import utime
from gui.temperature_gui import TemperatureGUI

class GUI:
    def __init__(self, lcd, up_pin=13, down_pin=15, select_pin=14):
        """Initialize the GUI with LCD and button pins"""
        self.lcd = lcd
        
        # Configure buttons with internal pull-up resistors
        self.up_button = Pin(up_pin, Pin.IN, Pin.PULL_UP)
        self.down_button = Pin(down_pin, Pin.IN, Pin.PULL_UP)
        self.select_button = Pin(select_pin, Pin.IN, Pin.PULL_UP)
        
        # Menu options
        self.menu_options = ["Temperature", "Option1", "Option2"]
        self.current_position = 0
        self.top_item_index = 0
        
        # Initialize sub-GUIs
        self.temperature_gui = TemperatureGUI(lcd, self.select_button)
        
        # Setup display
        self.refresh_menu()
        
    def refresh_menu(self):
        """Update the LCD display with current menu items"""
        self.lcd.clear()
        
        # Display up to 2 items starting from top_item_index
        for i in range(2):
            if self.top_item_index + i < len(self.menu_options):
                index = (self.top_item_index + i) % len(self.menu_options)
                item = self.menu_options[index]
                
                # Mark the currently selected item with an arrow
                if index == self.current_position:
                    self.lcd.move_to(0, i)
                    self.lcd.putchar(">")
                    self.lcd.move_to(2, i)
                    self.lcd.putstr(item)
                else:
                    self.lcd.move_to(1, i)
                    self.lcd.putstr(item)
    
    def move_up(self):
        """Move the selection up with wraparound"""
        self.current_position = (self.current_position - 1) % len(self.menu_options)
        
        # Adjust the view if necessary
        if self.current_position < self.top_item_index:
            self.top_item_index = self.current_position
        elif (self.current_position == len(self.menu_options) - 1 and 
              self.top_item_index == 0):
            self.top_item_index = len(self.menu_options) - 2 if len(self.menu_options) > 1 else 0
            
        self.refresh_menu()
        
    def move_down(self):
        """Move the selection down with wraparound"""
        self.current_position = (self.current_position + 1) % len(self.menu_options)
        
        # Adjust the view if necessary
        if (self.current_position >= self.top_item_index + 2):
            self.top_item_index = self.current_position - 1
        elif (self.current_position == 0 and 
              self.top_item_index > 0):
            self.top_item_index = 0
            
        self.refresh_menu()
    
    def select_option(self):
        """Execute action for selected menu item"""
        selected = self.menu_options[self.current_position]
        
        if selected == "Temperature":
            self.temperature_gui.show_temperature()
            self.refresh_menu()
        elif selected == "Option1":
            self.show_option("Option 1 selected")
        elif selected == "Option2":
            self.show_option("Option 2 selected")
    
    def show_option(self, message):
        """Display generic option message with timeout"""
        self.lcd.clear()
        self.lcd.center_text(message, 0)
        self.lcd.center_text("Returning...", 1)
        utime.sleep(2)
        self.refresh_menu()
    
    def run(self):
        """Main loop for GUI operation"""
        while True:
            # Check buttons - now looking for LOW (0) state when pressed (pull-up mode)
            if self.up_button.value() == 0:  # Button pressed (active low)
                self.move_up()
                utime.sleep(0.2)  # Debounce
            
            if self.down_button.value() == 0:  # Button pressed
                self.move_down()
                utime.sleep(0.2)  # Debounce
            
            if self.select_button.value() == 0:  # Button pressed
                self.select_option()
                utime.sleep(0.2)  # Debounce

            utime.sleep(0.05)  # Small delay to prevent high CPU usage
