from http import server
import threading

class DogCamWebServer(server.SimpleHTTPRequestHandler):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, directory="web", **kwargs)

  def end_headers(self):
    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
    self.send_header("Pragma", "no-cache")
    self.send_header("Expires", "0")
    super().end_headers()

  def log_message(self, format, *args):
    pass

def StartWebserver():
  WebServer = server.ThreadingHTTPServer(("", 8080), DogCamWebServer)
  HttpHandle = threading.Thread(target=WebServer.serve_forever, daemon = True, name="WebServer")
  HttpHandle.start()
  print("Web server started")
