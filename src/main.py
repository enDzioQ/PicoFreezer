import utime
from tools.lcd import LCD
from gui.gui import GUI

# Initialize the LCD display with temperature sensor pin
lcd_display = LCD(i2c_id=0, i2c_addr=39, sda_pin=0, scl_pin=1, num_rows=2, num_cols=16, temp_pin=2)

# Create and run GUI
gui = GUI(lcd=lcd_display)
gui.run()




