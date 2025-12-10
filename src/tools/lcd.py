from machine import Pin, I2C
import utime
from pico_i2c_lcd import I2cLcd

class LCD(I2cLcd):
    """Extended LCD class with custom display methods for PicoFreezer."""

    def __init__(self, i2c_id=0, i2c_addr=39, sda_pin=0, scl_pin=1, num_rows=2, num_cols=16):
        """Initialize the LCD display with customizable parameters"""
        self.i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
        super().__init__(self.i2c, i2c_addr, num_rows, num_cols)
        self.num_rows = num_rows
        self.num_cols = num_cols
        
        self.define_custom_chars()
    
    def display_text(self, text, row=0, col=0):
        """Display text at specified position"""
        self.move_to(col, row)
        self.putstr(text)
    
    def center_text(self, text, row):
        """Center text on specified row"""
        col = max(0, (self.num_cols - len(text)) // 2)
        self.display_text(text, row, col)
    
    def define_custom_chars(self):
        """Define custom characters including Celsius symbol"""
        # Celsius symbol
        self.custom_char(1, bytearray([
            0x07, 0x05, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00
        ]))
    
    def display_temperature_screen(self, temp_value, indicator=None):
        """Display temperature on the LCD"""
        # Clear the display
        self.clear()
        
        # Display "Temperature:" on the first line
        self.center_text("Temperature:", 0)
        
        # Display the temperature with Celsius symbol on the second line
        temp_str = f"{temp_value}\1C"
        self.center_text(temp_str, 1)
        
        # Display optional indicator in the bottom right corner
        if indicator:
            self.move_to(15, 1)
            self.putchar(indicator)
    
    def display_target_temp_screen(self, target_value):
        """Display target temperature setting screen"""
        self.clear()
        self.center_text("Target Temp:", 0)
        temp_str = f"{target_value:.1f}\1C"
        self.center_text(temp_str, 1)
    
    def display_option_screen(self, message, submessage="Returning..."):
        """Display an option screen with message"""
        self.clear()
        self.center_text(message, 0)
        self.center_text(submessage, 1)

