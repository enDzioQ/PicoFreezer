import utime
from machine import Pin
from gui.base_gui import BaseGUI
from tools.wifi_password_manager import WiFiPasswordManager

class WiFiGUI(BaseGUI):
    """WiFi connection GUI"""
    
    # Character sets for password entry
    LOWERCASE_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789_-."
    UPPERCASE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-."
    
    def __init__(self, lcd, wifi_manager, select_button, up_button, down_button, left_pin=11, right_pin=12):
        """Initialize the WiFi GUI"""
        super().__init__(lcd, up_button, down_button, select_button)
        
        self.left_button = Pin(left_pin, Pin.IN, Pin.PULL_UP) 
        self.right_button = Pin(right_pin, Pin.IN, Pin.PULL_UP)
        self.last_left_state = 1
        self.last_right_state = 1
        
        self.wifi = wifi_manager
        
        self.password_manager = WiFiPasswordManager()
        
        self.state = "initial"
        
        self.networks = []
        self.current_network_index = 0
        self.top_network_index = 0
        
        self.selected_network = ""
        self.password = ""
        self.cursor_pos = 0
        self.char_set = self.LOWERCASE_CHARS
        self.current_char_index = 0
        self.caps_lock = False
    
    def is_left_pressed(self):
        """Detect rising edge on the left button"""
        current_state = self.left_button.value()
        if current_state == 0 and self.last_left_state == 1:
            self.last_left_state = 0
            utime.sleep(0.2)  # Debounce
            return True
        elif current_state == 1 and self.last_left_state == 0:
            self.last_left_state = 1
        return False
    
    def is_right_pressed(self):
        """Detect rising edge on the right button"""
        current_state = self.right_button.value()
        if current_state == 0 and self.last_right_state == 1:
            self.last_right_state = 0
            utime.sleep(0.2)  # Debounce
            return True
        elif current_state == 1 and self.last_right_state == 0:
            self.last_right_state = 1
        return False
    
    def is_left_right_pressed(self):
        """Check if both left and right buttons are pressed simultaneously"""
        return self.left_button.value() == 0 and self.right_button.value() == 0
    
    def update_additional_button_states(self):
        """Update the states of the additional buttons"""
        self.last_left_state = self.left_button.value()
        self.last_right_state = self.right_button.value()
    
    def run(self):
        """Run the WiFi GUI"""
        # Check if already connected to WiFi
        if self.wifi.is_connected():
            self.state = "connected"
            self.display_connected_state()
        else:
            self.state = "scanning"
            self.scan_networks()
        
        while True:
            # Common exit condition for all states - press up+down to exit
            if self.is_up_down_pressed():
                utime.sleep(0.2)  # Debounce
                return  # Exit the WiFi screen (keeping connection if established)
            
            # Handle different states
            if self.state == "scanning":
                self.handle_scanning_state()
            elif self.state == "network_list":
                self.handle_network_list_state()
            elif self.state == "password_entry":
                self.handle_password_entry_state()
            elif self.state == "connecting":
                self.handle_connecting_state()
            elif self.state == "connected":
                self.handle_connected_state()
            
            # Update all button states
            self.update_button_states()
            self.update_additional_button_states()
            utime.sleep(0.05)  # Small delay to prevent CPU overload
    
    def scan_networks(self):
        """Scan for available WiFi networks"""
        self.state = "scanning"
        self.lcd.clear()
        self.lcd.center_text("Scanning for", 0)
        self.lcd.center_text("WiFi networks...", 1)
        
        # Perform the scan
        utime.sleep(1)
        try:
            self.networks = self.wifi.scan_networks()
            self.current_network_index = 0
            self.top_network_index = 0
            self.state = "network_list"
            self.display_network_list()
        except Exception as e:
            self.lcd.clear()
            self.lcd.center_text("Scan failed!", 0)
            self.lcd.center_text(str(e), 1)
            utime.sleep(2)
            self.state = "network_list"
            self.networks = []
            self.display_network_list()
    
    def display_network_list(self):
        """Display the list of available networks"""
        self.lcd.clear()
        
        if not self.networks:
            self.lcd.center_text("No networks", 0)
            self.lcd.center_text("found", 1)
            return
        
        # Display up to 2 networks starting from top_network_index
        for i in range(2):
            if self.top_network_index + i < len(self.networks):
                index = self.top_network_index + i
                network = self.networks[index]
                
                # Mark the currently selected network with an arrow
                if index == self.current_network_index:
                    self.lcd.move_to(0, i)
                    self.lcd.putchar(">");
                    # Truncate SSID if too long for display
                    display_ssid = network[:14] if len(network) > 14 else network
                    self.lcd.move_to(2, i)
                    self.lcd.putstr(display_ssid)
                else:
                    # Truncate SSID if too long for display
                    display_ssid = network[:15] if len(network) > 15 else network
                    self.lcd.move_to(1, i)
                    self.lcd.putstr(display_ssid)
    
    def move_network_selection_up(self):
        """Move the network selection up with wraparound"""
        if not self.networks:
            return
            
        self.current_network_index = (self.current_network_index - 1) % len(self.networks)
        
        # Adjust the view if necessary
        if self.current_network_index < self.top_network_index:
            self.top_network_index = self.current_network_index
        elif (self.current_network_index == len(self.networks) - 1 and 
              self.top_network_index == 0):
            self.top_network_index = len(self.networks) - 2 if len(self.networks) > 1 else 0
            
        self.display_network_list()
        
    def move_network_selection_down(self):
        """Move the network selection down with wraparound"""
        if not self.networks:
            return
            
        self.current_network_index = (self.current_network_index + 1) % len(self.networks)
        
        # Adjust the view if necessary
        if (self.current_network_index >= self.top_network_index + 2):
            self.top_network_index = self.current_network_index - 1
        elif (self.current_network_index == 0 and 
              self.top_network_index > 0):
            self.top_network_index = 0
            
        self.display_network_list()
    
    def select_network(self):
        """Select a network and proceed to password entry"""
        if not self.networks:
            return
            
        self.selected_network = self.networks[self.current_network_index]
        self.state = "password_entry"
        self.start_password_entry()
    
    def start_password_entry(self):
        """Initialize the password entry screen"""
        # Check if there's a saved password for this network
        saved_password = self.password_manager.get_password(self.selected_network)
        
        if saved_password:
            # Pre-fill with saved password
            self.password = saved_password
            self.cursor_pos = len(saved_password)
            
            # Display a message about using saved password
            self.lcd.clear()
            self.lcd.center_text("Using saved", 0)
            self.lcd.center_text("password", 1)
            utime.sleep(1)
        else:
            # No saved password, start with empty field
            self.password = ""
            self.cursor_pos = 0
            
        self.char_set = self.LOWERCASE_CHARS
        self.current_char_index = 0
        self.caps_lock = False
        self.display_password_entry()
    
    def display_password_entry(self):
        """Display the password entry screen"""
        self.lcd.clear()
        
        # Display truncated network name if needed
        ssid_display = self.selected_network[:10] if len(self.selected_network) > 10 else self.selected_network
        self.lcd.center_text(f"Pass: {ssid_display}", 0)
        
        # Display current password with cursor position
        password_display = self.password
        if len(password_display) < 16:
            password_display += "_" * (16 - len(password_display))
        
        self.lcd.move_to(0, 1)
        for i, char in enumerate(password_display):
            if i == self.cursor_pos:
                # Highlight cursor position
                if i < len(self.password):
                    # We're on an existing character
                    self.lcd.putchar(char)
                else:
                    # We're at the end adding a new character
                    current_char = self.char_set[self.current_char_index]
                    self.lcd.putchar(current_char)
            else:
                self.lcd.putchar(char)
    
    def toggle_character_set(self):
        """Toggle between uppercase and lowercase character sets"""
        self.caps_lock = not self.caps_lock
        if self.caps_lock:
            self.char_set = self.UPPERCASE_CHARS
            self.lcd.clear()
            self.lcd.center_text("CAPS LOCK ON", 0)
            utime.sleep(0.5)
        else:
            self.char_set = self.LOWERCASE_CHARS
            self.lcd.clear()
            self.lcd.center_text("caps lock off", 0)
            utime.sleep(0.5)
        
        # Reset character index to avoid out-of-range
        self.current_char_index = min(self.current_char_index, len(self.char_set) - 1)
        self.display_password_entry()
    
    def backspace(self):
        """Delete the character to the left of the cursor"""
        if self.cursor_pos > 0:
            # Remove character
            self.password = self.password[:self.cursor_pos-1] + self.password[self.cursor_pos:]
            self.cursor_pos -= 1
            self.display_password_entry()
    
    def increment_character(self):
        """Increment the current character in the password"""
        self.current_char_index = (self.current_char_index + 1) % len(self.char_set)
        self.display_password_entry()
    
    def decrement_character(self):
        """Decrement the current character in the password"""
        self.current_char_index = (self.current_char_index - 1) % len(self.char_set)
        self.display_password_entry()
    
    def select_character(self):
        """Select the current character and add it to password"""
        # If we're at the end of the password, append the new character
        if self.cursor_pos == len(self.password):
            self.password += self.char_set[self.current_char_index]
        # If we're within the password, replace the character
        else:
            self.password = self.password[:self.cursor_pos] + self.char_set[self.current_char_index] + self.password[self.cursor_pos+1:]
        
        # Move cursor right
        self.cursor_pos += 1
        self.display_password_entry()
    
    def submit_password(self):
        """Connect using the entered password"""
        self.state = "connecting"
        self.lcd.clear()
        self.lcd.center_text(f"Connecting to", 0)
        self.lcd.center_text(self.selected_network, 1)
        
        # Attempt to connect
        success = self.wifi.connect(self.selected_network, self.password)
        
        if success:
            # Save the successful password
            self.password_manager.save_password(self.selected_network, self.password)
            
            self.state = "connected"
            self.display_connected_state()
        else:
            self.lcd.clear()
            self.lcd.center_text("Connection failed", 0)
            self.lcd.center_text("Try again", 1)
            utime.sleep(2)
            self.state = "network_list"
            self.display_network_list()
    
    def display_connected_state(self):
        """Display the connected state"""
        self.lcd.clear()
        
        # Get the current connection details
        ssid = self.wifi.get_current_ssid()
        ip = self.wifi.get_ip()
        
        # Display connection information
        if ssid:
            self.lcd.move_to(0, 0)
            self.lcd.putstr(f"WiFi: {ssid}")
            self.lcd.move_to(0, 1)
            if ip:
                self.lcd.putstr(f"IP: {ip}")
            else:
                self.lcd.putstr("No IP address")
        else:
            self.lcd.center_text("WiFi Connected", 0)
            self.lcd.center_text("Unknown SSID", 1)
    
    def disconnect_wifi(self):
        """Disconnect from WiFi and return to network list"""
        self.lcd.clear()
        self.lcd.center_text("Disconnecting", 0)
        self.lcd.center_text("from WiFi...", 1)
        
        self.wifi.disconnect()
        utime.sleep(1)
        
        # Return to network scanning
        self.state = "scanning"
        self.scan_networks()
    
    def handle_scanning_state(self):
        """Handle UI while in scanning state"""
        # Nothing to do here, we're waiting for scan to complete
        pass
    
    def handle_network_list_state(self):
        """Handle UI while showing network list"""
        if self.is_up_pressed():
            self.move_network_selection_up()
        
        if self.is_down_pressed():
            self.move_network_selection_down()
        
        if self.is_select_pressed():
            self.select_network()
    
    def handle_password_entry_state(self):
        """Handle UI while entering password"""
        # Check for special key combination
        if self.is_left_right_pressed():
            # Submit password
            self.submit_password()
            return
        
        # Handle individual buttons
        if self.is_up_pressed():
            self.increment_character()
        
        if self.is_down_pressed():
            self.decrement_character()
        
        if self.is_left_pressed():
            self.backspace()  # Changed to backspace functionality
        
        if self.is_right_pressed():
            self.select_character()  # Changed to confirm character functionality
        
        if self.is_select_pressed():
            self.toggle_character_set()  # Changed to caps lock functionality
    
    def handle_connecting_state(self):
        """Handle UI while connecting to WiFi"""
        # Nothing to do here, connection attempt is ongoing
        pass
    
    def handle_connected_state(self):
        """Handle UI while connected to WiFi"""
        if self.is_select_pressed():
            # Disconnect and return to network list
            self.disconnect_wifi()
