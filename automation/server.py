#!/usr/bin/env python3
"""
Endpoints para Tasker/MacroDroid via HTTP local.
"""
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

COMMANDS = {
    "open_browser": "com.android.browser",
    "open_whatsapp": "com.whatsapp",
    "open_telegram": "org.telegram.messenger",
    "open_settings": "com.android.settings",
}

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/command":
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode()) if length > 0 else {}
            
            cmd = data.get("command", "")
            args = data.get("args", "")
            
            if cmd in COMMANDS:
                app = COMMANDS[cmd]
                subprocess.run(["am", "start", "-n", f"{app}/.MainActivity"], 
                    capture_output=True)
                self.send_json({"success": True, "output": app})
            else:
                self.send_json({"error": f"Comando desconhecido: {cmd}"})
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path == "/commands":
            self.send_json({"commands": list(COMMANDS.keys())})
        else:
            self.send_error(404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        pass

def main():
    print("Automation rodando em http://0.0.0.0:5001")
    server = HTTPServer(("0.0.0.0", 5001), Handler)
    server.serve_forever()

if __name__ == "__main__":
    main()