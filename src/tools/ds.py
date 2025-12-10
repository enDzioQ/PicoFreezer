import time
from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20

class DS:
    """Handles DS18X20 temperature sensor operations."""

    def __init__(self, data_pin=22):
        """Initialize the DS18X20 temperature sensor"""
        self.ds_pin = Pin(data_pin)
        self.ds_sensor = DS18X20(OneWire(self.ds_pin))
        self.roms = self.ds_sensor.scan()  # Scan for DS18X20 devices
        
    def get_temperature(self):
        """Read temperature from the sensor
        Returns:
            float: Temperature in Celsius or None if no sensor found
        """
        if not self.roms:
            return None
        
        try:
            # Start temperature conversion
            self.ds_sensor.convert_temp()
            # Wait for conversion to complete (required by DS18X20 protocol)
            time.sleep_ms(750)
            
            # Read the temperature from the first sensor found
            temperature = self.ds_sensor.read_temp(self.roms[0])
            
            # Round to 1 decimal place
            return round(temperature, 1)
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return None
        
    def get_formatted_temp(self):
        """Get temperature as a formatted string
        Returns:
            str: Formatted temperature string or error message
        """
        temp = self.get_temperature()
        if temp is not None:
            return f"{temp:.1f}"
        return "Error"
