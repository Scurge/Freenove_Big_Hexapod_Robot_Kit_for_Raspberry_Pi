# -*- coding: utf-8 -*-
import os
import sys
import getopt
import threading
from Server import Server
from Control import Control

class HeadlessServer:
    def __init__(self):
        self.user_ui = True
        self.start_tcp = False
        self.server = Server()
        self.parseOpt()
        if self.start_tcp:
            self.start_server()

    def parseOpt(self):
        self.opts, self.args = getopt.getopt(sys.argv[1:], "tn")
        for o, a in self.opts:
            if o == '-t':
                print("Open TCP")
                self.start_tcp = True
            elif o == '-n':
                self.user_ui = False

    def start_server(self):
        self.server.turn_on_server()
        self.server.tcp_flag = True
        self.video_thread = threading.Thread(target=self.server.transmission_video)
        self.video_thread.start()
        self.instruction_thread = threading.Thread(target=self.server.receive_instruction)
        self.instruction_thread.start()

    def stop_server(self):
        self.server.tcp_flag = False
        try:
            self.stop_thread(self.video_thread)
            self.stop_thread(self.instruction_thread)
        except Exception as e:
            print(e)
        self.server.turn_off_server()
        print("Server stopped")

    def stop_thread(self, thread):
        if thread.is_alive():
            thread.join(timeout=1)

    def run(self):
        try:
            if self.start_tcp:
                print("Server is running...")
                while True:
                    pass
        except KeyboardInterrupt:
            print("KeyboardInterrupt received. Stopping the server.")
            self.stop_server()
            sys.exit(0)

if __name__ == '__main__':
    headless_server = HeadlessServer()
    headless_server.run()

