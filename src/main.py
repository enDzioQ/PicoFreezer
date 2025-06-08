import utime
from machine import Pin
from tools.lcd import LCD
from tools.ds import DS
from tools.wifi import WiFi
from gui.gui import GUI
from monitor.temperature_monitor import TemperatureMonitor

def main():
    # Initialize components
    print("Initializing DS temperature sensor...")
    ds_sensor = DS(data_pin=2)
    
    # Display firmware information
    print("PicoFreezer starting up...")
    
    # Initialize WiFi module
    print("Initializing WiFi module...")
    wifi_manager = WiFi()

    # Create the temperature monitor (will run on core 1)
    print("Creating temperature monitor...")
    temp_monitor = TemperatureMonitor(ds_sensor=ds_sensor, led_pin=16, wifi_manager=wifi_manager)

    # Initialize the LCD display
    print("Initializing LCD...")
    lcd_display = LCD(
        i2c_id=0, 
        i2c_addr=39, 
        sda_pin=0, 
        scl_pin=1, 
        num_rows=2, 
        num_cols=16
    )
    
    # Display startup message
    lcd_display.clear()
    lcd_display.center_text("PicoFreezer", 0)
    lcd_display.center_text("Starting...", 1)
    utime.sleep(1)

    try:
        # Start temperature monitoring on core 1
        print("Starting temperature monitor thread...")
        temp_monitor.start_monitoring()
        
        # Give the temperature monitor time to get the first reading
        print("Waiting for initial temperature reading...")
        utime.sleep(2)
        
        # Create and run GUI (on core 0)
        print("Starting GUI...")
        gui = GUI(lcd=lcd_display, temp_monitor=temp_monitor, wifi_manager=wifi_manager)
        gui.run()
        
    except KeyboardInterrupt:
        print("Program interrupted. Cleaning up...")
    finally:
        # Always stop the monitoring thread when exiting
        temp_monitor.stop_monitoring()
        
        # Wait briefly to ensure thread has time to exit
        utime.sleep(0.5)
        
        # Disconnect WiFi if connected
        if wifi_manager.is_connected():
            wifi_manager.disconnect()
        
        # Display shutdown message
        lcd_display.clear()
        lcd_display.center_text("Shutting down", 0)
        lcd_display.center_text("Goodbye!", 1)
        utime.sleep(1)
        lcd_display.clear()
        
        print("Program terminated cleanly.")

# Run the main function
if __name__ == "__main__":
    main()




