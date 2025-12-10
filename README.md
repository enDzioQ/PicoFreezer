# PicoFreezer Controller

A temperature control system for a freezer using Peltier cells, built for Raspberry Pi Pico.

## Description

PicoFreezer is a device that controls the temperature inside a freezer by managing Peltier cells through I/O operations. This project provides the software controller, including a GUI interface, temperature monitoring, web server, and various tools for managing WiFi and LCD display.

## Features

- **Temperature Monitoring**: Real-time temperature tracking and control.
- **GUI Interface**: User-friendly graphical interface for configuration and monitoring.
- **Web Server**: Access and control via web browser.
- **WiFi Management**: Tools for managing WiFi connections and passwords.
- **LCD Display**: Integration with I2C LCD for local display.
- **Storage**: Secure password management.

## Project Structure

```
PicoFreezer/
├── src/
│   ├── main.py                 # Main entry point
│   ├── gui/
│   │   ├── base_gui.py         # Base GUI components
│   │   ├── gui.py              # Main GUI
│   │   ├── temperature_gui.py  # Temperature control GUI
│   │   └── wifi_gui.py         # WiFi GUI
│   ├── lib/
│   │   ├── lcd_api.py          # LCD API
│   │   └── pico_i2c_lcd.py     # I2C LCD implementation
│   ├── monitor/
│   │   └── temperature_monitor.py # Temperature monitoring
│   ├── storage/
│   │   └── passwords.txt       # Password storage
│   ├── tools/
│   │   ├── ds.py               # DS sensor tools
│   │   ├── lcd.py              # LCD tools
│   │   ├── wifi_password_manager.py # WiFi password manager
│   │   └── wifi.py             # WiFi tools
│   └── web/
│       ├── index.html          # Web interface
│       ├── server.py           # Web server
│       └── style.css           # Web styles
└── README.md                   # This file
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/enDzioQ/PicoFreezer.git
   cd PicoFreezer
   ```

2. Ensure you have MicroPython installed on your Raspberry Pi Pico.

3. Upload the files to your Pico using your preferred method (e.g., Thonny IDE or rshell).

## Usage

- Run `main.py` on your Pico to start the controller.
- Access the web interface by connecting to the Pico's IP address in your browser.
- Use the GUI for local control and configuration.

## Requirements

- Raspberry Pi Pico
- MicroPython
- Peltier cells and necessary hardware for temperature control
- I2C LCD display (optional)
- WiFi module (optional)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This project is for educational and experimental purposes. Use at your own risk.
