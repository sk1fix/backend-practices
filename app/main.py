from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpeHTTPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello word')

httpd = HTTPServer(('localhost', 8080), SimpeHTTPServer)
httpd.serve_forever()