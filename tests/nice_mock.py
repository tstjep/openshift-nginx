#!/usr/bin/python3
#
# Micro web server whose status code is based on the path. Path /200 returns status code 200,
# /404 code 400 and so on.
#
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import time
import os
import uuid


class S(BaseHTTPRequestHandler):
    def do_GET(self):
        body = ''
        if self.path == '/cache':
            body = str(uuid.uuid4())
            self.send_response(200)
            self.send_header('Cache-Control', 'public, max-age=86400')
        elif self.path.startswith('/time='):
            time.sleep(int(self.path[6:]))
            self.send_response(200)
        elif self.path == '/status-tocco':
            self.send_response(200)
        elif self.path == '/websocket':
            if self.headers['Upgrade'].lower() == 'websocket' \
                    and self.headers['Connection'].lower() == 'upgrade':
                status = 101
            else:
                status = 500

            self.send_response(status)
        elif self.path == '/no-websocket':
            if 'Upgrade' not in self.headers \
                    and 'Connection' not in self.headers:
                status = 200
            else:
                status = 500

            self.send_response(status)
        else:
            code = int(self.path[1:])
            self.send_response(code)

        self.end_headers()
        self.wfile.write(body.encode())


def run(server_class=HTTPServer, handler_class=S):
    server_address = ('localhost', 8080)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
