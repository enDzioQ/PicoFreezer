from machine import Pin, I2C
import utime
from pico_i2c_lcd import I2cLcd
from tools.ds import DS

class LCD(I2cLcd):
    def __init__(self, i2c_id=0, i2c_addr=39, sda_pin=0, scl_pin=1, num_rows=2, num_cols=16, temp_pin=22):
        """Initialize the LCD display with customizable parameters"""
        self.i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=400000)
        # Call the parent class constructor
        super().__init__(self.i2c, i2c_addr, num_rows, num_cols)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.temp_sensor = DS(data_pin=temp_pin)
        
        # Define custom Celsius character
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
    
    def display_temp(self):
        """Display temperature on the LCD"""
        # Get temperature from the DS sensor
        temp_value = self.temp_sensor.get_formatted_temp()
        
        # Clear the display
        self.clear()
        
        # Display "Temperature:" on the first line
        self.center_text("Temperature:", 0)
        
        # Display the temperature with Celsius symbol on the second line
        temp_str = f"{temp_value}\1C"
        self.center_text(temp_str, 1)
        
        # Return temperature as a float for threshold comparison
        try:
            return float(temp_value)
        except ValueError:
            return 0.0

