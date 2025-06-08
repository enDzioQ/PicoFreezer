import socket
import time
import gc
import json

class WebServer:
    def __init__(self, wifi_manager, temp_monitor):
        """Initialize the web server"""
        self.wifi = wifi_manager
        self.temp_monitor = temp_monitor
        self.server_socket = None
        self.is_running = False
        self.last_update_time = 0
        
        # HTML template - load from file
        self._html = self._load_html_template()
        
    def start(self):
        """Start the web server if WiFi is connected"""
        if not self.wifi.is_connected():
            print("Cannot start web server: WiFi not connected")
            return False
            
        try:
            # Create socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to address and port
            self.server_socket.bind(('', 80))
            
            # Listen for connections
            self.server_socket.listen(5)
            self.server_socket.settimeout(0.5)  # Non-blocking with timeout
            
            self.is_running = True
            print(f"Web server started at http://{self.wifi.get_ip()}")
            return True
            
        except Exception as e:
            print(f"Error starting server: {e}")
            if self.server_socket:
                self.server_socket.close()
            self.is_running = False
            return False
            
    def stop(self):
        """Stop the web server"""
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        self.is_running = False
        print("Web server stopped")
        
    def update(self):
        """Check for client connections and handle requests"""
        if not self.is_running or not self.server_socket:
            return
            
        # Accept connections with timeout
        try:
            client, addr = self.server_socket.accept()
            print(f"Client connected from: {addr}")
            self._handle_client(client)
        except OSError as e:
            # Timeout or other socket error, just continue
            pass
            
        # Free memory
        gc.collect()
        
    def _load_html_template(self):
        """Load HTML template from index.html file"""
        try:
            with open('/src/web/index.html', 'r') as f:
                print("Successfully loaded index.html")
                return f.read()
        except OSError as e:
            print(f"Error loading index.html: {e}")
            return "<html><body><h1>Error loading template</h1><p>Could not load index.html</p></body></html>"
    
    def _handle_client(self, client):
        """Handle an HTTP client connection"""
        try:
            client.settimeout(3.0)  # Set timeout for client socket operations
            
            # Receive data
            request = client.recv(1024).decode()
            
            # Process the request
            if request.find('GET / ') >= 0 or request.find('GET /index.html') >= 0:
                # Main page request
                self._send_html_response(client)
            elif request.find('GET /style.css') >= 0:
                # CSS file request
                self._send_css_response(client)
            elif request.find('GET /api/data') >= 0:
                # API request for current data
                self._send_data_response(client)
            elif request.find('POST /api/target') >= 0:
                # API request to update target temperature
                self._handle_target_update(client, request)
            else:
                # Unknown request, send 404
                self._send_404_response(client)
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client.close()
    
    def _send_html_response(self, client):
        """Send the main HTML page"""
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: text/html\r\n\r\n"
        response += self._html
        client.send(response.encode())
        
    def _send_css_response(self, client):
        """Send the CSS file"""
        try:
            with open('/src/web/style.css', 'r') as f:
                css_content = f.read()
                
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: text/css\r\n\r\n"
            response += css_content
            client.send(response.encode())
        except OSError as e:
            print(f"Error loading style.css: {e}")
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            client.send(response.encode())
        
    def _send_data_response(self, client):
        """Send current data as JSON"""
        # Get current data
        current_temp = self.temp_monitor.get_current_temp()
        target_temp = self.temp_monitor.get_target_temp()
        is_cooling = current_temp > target_temp
        
        # Create JSON response
        data = {
            "temperature": round(current_temp, 1),
            "target_temperature": round(target_temp, 1),
            "state": "cooling" if is_cooling else "heating"
        }
        
        json_data = json.dumps(data)
        
        # Send response
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Type: application/json\r\n"
        response += "Access-Control-Allow-Origin: *\r\n\r\n"
        response += json_data
        client.send(response.encode())
        
    def _handle_target_update(self, client, request):
        """Handle target temperature update request"""
        try:
            # Extract the new target temperature value
            import re
            match = re.search(r'target=([0-9.]+)', request)
            if match:
                new_target = float(match.group(1))
                
                # Update the target temperature
                self.temp_monitor.set_target_temp(new_target)
                
                # Send success response
                response = "HTTP/1.1 200 OK\r\n"
                response += "Content-Type: application/json\r\n\r\n"
                response += json.dumps({"success": True, "target": new_target})
                client.send(response.encode())
            else:
                # Bad request
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"
                client.send(response.encode())
        except Exception as e:
            print(f"Error updating target: {e}")
            response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
            client.send(response.encode())
            
    def _send_404_response(self, client):
        """Send a 404 Not Found response"""
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        response += "<html><body><h1>404 Not Found</h1></body></html>"
        client.send(response.encode())
