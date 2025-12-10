import utime
from machine import Pin
from tools.lcd import LCD
from tools.ds import DS
from tools.wifi import WiFi
from gui.gui import GUI
from monitor.temperature_monitor import TemperatureMonitor

def main():
    """Main entry point for the PicoFreezer application.

    Initializes all components including sensors, WiFi, LCD, temperature monitor,
    and GUI, then starts the main loop.
    """
    print("Initializing DS temperature sensor...")
    ds_sensor = DS(data_pin=2)

    print("PicoFreezer starting up...")

    print("Initializing WiFi module...")
    wifi_manager = WiFi()

    print("Creating temperature monitor...")
    temp_monitor = TemperatureMonitor(ds_sensor=ds_sensor, led_pin=16, wifi_manager=wifi_manager)

    print("Initializing LCD...")
    lcd_display = LCD(
        i2c_id=0,
        i2c_addr=39,
        sda_pin=0,
        scl_pin=1,
        num_rows=2,
        num_cols=16
    )

    lcd_display.clear()
    lcd_display.center_text("PicoFreezer", 0)
    lcd_display.center_text("Starting...", 1)
    utime.sleep(1)

    try:
        print("Starting temperature monitor thread...")
        temp_monitor.start_monitoring()

        print("Waiting for initial temperature reading...")
        utime.sleep(2)

        print("Starting GUI...")
        gui = GUI(lcd=lcd_display, temp_monitor=temp_monitor, wifi_manager=wifi_manager)
        gui.run()

    except KeyboardInterrupt:
        print("Program interrupted. Cleaning up...")
    finally:
        temp_monitor.stop_monitoring()

        utime.sleep(0.5)

        if wifi_manager.is_connected():
            wifi_manager.disconnect()

        lcd_display.clear()
        lcd_display.center_text("Shutting down", 0)
        lcd_display.center_text("Goodbye!", 1)
        utime.sleep(1)
        lcd_display.clear()

        print("Program terminated cleanly.")

# Run the main function
if __name__ == "__main__":
    main()




