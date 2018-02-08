#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Elvis Yu-Jing Lin <elvisyjlin@gmail.com>
# Licensed under the MIT License - https://opensource.org/licenses/MIT

try:
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer as BaseHTTPServer
except ImportError:
    from http.server import SimpleHTTPRequestHandler, HTTPServer as BaseHTTPServer

import os
from os.path import join
# from os import chdir
from threading import Thread
from time import sleep

IP = ''
PORT = 8000
PATH = 'F.LF'

class HTTPHandler(SimpleHTTPRequestHandler):
    """ This handler uses server.base_path instead of always using os.getcwd() """
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath
    """ This overrided method mute all server logs """
    def log_message(self, format, *args):
        return

class HTTPServer(BaseHTTPServer):
    """ The main server, you pass in base_path which is the path you want to serve requests from """
    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)

class LF2Server():
    def __init__(self, path='.', ip=IP, port=PORT):
        '''Constructor'''
        path = join(path, PATH)
        self.server_address = (ip, port)
        self.httpd = HTTPServer(path, self.server_address)
        self.thread = Thread(target = self.serve)
        self.thread.setDaemon(True)

    def serve(self):
        # chdir('F.LF')
        self.httpd.serve_forever()

    def start(self):
        '''Starts the LF2 server in the background'''
        print('Starting LF2 server on {0}...'.format(self.server_address))
        self.thread.start()
        print('LF2 server started.')

    def close(self):
        '''Closes the server daemon and join the running thread'''
        self.httpd.shutdown()
        self.thread.join()

### 
# Example: run the LF2 server and stop by key interupting
###

# server = LF2Server()
# try:
#     server.start()
#     while True: pass
# finally:
#     server.close()
