#!/usr/bin/python3
#
# Micro web server whose status code is based on the path. Path /200 returns status code 200,
# /404 code 400 and so on.
#
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import os


class S(BaseHTTPRequestHandler):
    def do_GET(self):
        code = int(self.path[1:])
        self.send_response(code)
        self.end_headers()


def run(server_class=HTTPServer, handler_class=S):
    server_address = ('localhost', 8080)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
