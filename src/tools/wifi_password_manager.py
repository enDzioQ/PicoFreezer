class WiFiPasswordManager:
    """Manages saved WiFi passwords"""
    
    def __init__(self, password_file='storage/passwords.txt'):
        """Initialize with a password file"""
        self.password_file = password_file
        self.passwords = {}
        self.load_passwords()
    
    def load_passwords(self):
        """Load saved passwords from file"""
        try:
            with open(self.password_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and ',' in line:
                        parts = line.split(',', 1)  # Split only on first comma
                        if len(parts) == 2:
                            ssid, password = parts
                            self.passwords[ssid] = password
            print(f"Loaded {len(self.passwords)} WiFi passwords")
        except OSError:
            # File might not exist yet
            print("No saved passwords found or couldn't read password file")
            self.passwords = {}
    
    def get_password(self, ssid):
        """Get the saved password for a SSID if it exists"""
        return self.passwords.get(ssid)
    
    def save_password(self, ssid, password):
        """Save a new password or update existing one"""
        # Update the in-memory dictionary
        self.passwords[ssid] = password
        
        # Write all passwords back to file
        try:
            with open(self.password_file, 'w') as f:
                for network, pwd in self.passwords.items():
                    f.write(f"{network},{pwd}\n")
            print(f"Saved password for network: {ssid}")
            return True
        except OSError as e:
            print(f"Failed to save password: {e}")
            return False
