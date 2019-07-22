import io
import picamera
import logging
import socketserver
import threading
from threading import Condition
from http import server

PAGE="""\
<html>
<head>
<title>Rainwater Printer Live View</title>
</head>
<body>
<h1>Rainwater Printer Live View</h1>
<img style="margin-left: auto; margin-right: auto;" src="stream.mjpg"/>
</body>
</html>
"""

global output

class LiveCamera(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.resolution = (1280,720)
        self.framerate = 60
        self.camera = picamera.PiCamera(resolution=self.resolution, framerate=self.framerate)
        self.camera.annotate_background = picamera.color.Color('#000')
        
    # Run camera in it's own thread
    def run(self):
        print("Camera started")
        self.startCamera()
        
        
    def startCamera(self):
        """
        Starts the Pi camera, for the live feed
        """
        global output
        output = StreamingOutput()
        self.camera.start_recording(output, format='mjpeg', bitrate=25000000, quality=100)
        try:
            address = ('', 8000)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()

    
class StreamingOutput():
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
                
    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        global output
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/base.html')
            self.end_headers()
        elif self.path == '/base.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
