import network
import time

class WiFi:
    def __init__(self):
        """Initialize the WiFi module"""
        # Create a WLAN interface
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # Track connection state
        self.connected = False
        self.current_ssid = None
    
    def scan_networks(self):
        """Scan for available WiFi networks
        Returns:
            list: List of network SSIDs
        """
        # Ensure the interface is active
        if not self.wlan.active():
            self.wlan.active(True)
        
        # Scan for networks
        networks = self.wlan.scan()
        # Format the results - extract SSIDs
        results = []
        for net in networks:
            ssid = net[0].decode('utf-8') if isinstance(net[0], bytes) else net[0]
            results.append(ssid)
        return results
    
    def connect(self, ssid, password):
        """Connect to a WiFi network
        Args:
            ssid (str): Network SSID
            password (str): Network password
        Returns:
            bool: True if connected successfully, False otherwise
        """
        # Connect to the network
        self.wlan.connect(ssid, password)
        
        # Wait for connection (with timeout)
        max_wait = 10
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            max_wait -= 1
            print("Waiting for connection...")
            time.sleep(1)
        
        # Check if connection was successful
        if self.wlan.status() == 3:
            self.connected = True
            self.current_ssid = ssid
            print(f"Connected to {ssid}")
            print(f"IP: {self.wlan.ifconfig()[0]}")
            return True
        else:
            self.connected = False
            self.current_ssid = None
            print(f"Failed to connect to {ssid}")
            print(f"Status: {self.wlan.status()}")
            return False
    
    def disconnect(self):
        """Disconnect from the current WiFi network"""
        if self.connected:
            self.wlan.disconnect()
            self.connected = False
            self.current_ssid = None
            print("Disconnected from WiFi")
    
    def is_connected(self):
        """Check if connected to a WiFi network
        Returns:
            bool: True if connected, False otherwise
        """
        # Update the connection state based on actual status
        self.connected = self.wlan.isconnected()
        return self.connected
    
    def get_current_ssid(self):
        """Get the SSID of the currently connected network
        Returns:
            str: SSID of the connected network, or None if not connected
        """
        if self.is_connected():
            return self.current_ssid
        return None
    
    def get_ip(self):
        """Get the IP address
        Returns:
            str: IP address, or None if not connected
        """
        if self.is_connected():
            return self.wlan.ifconfig()[0]
        return None
