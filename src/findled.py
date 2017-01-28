#!/usr/bin/env python

import logging
import sys
import time

import rtmidi
from rtmidi.midiutil import open_midiport

client_name = "testall"

midiout = rtmidi.MidiOut(name=client_name)
midiout.open_virtual_port("out")
log = logging.getLogger('test_midiin_callback')

logging.basicConfig(level=logging.DEBUG)

def midiSolver(message):
  print(message)

def testAll():
    time.sleep(10)
    for y in range(0, 127):
        message = [144, y, 127]
        #time.sleep(0.1)
        input()
        midiout.send_message(message)
        print(message)

class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        global g_toggle
        message, deltatime = event
        self._wallclock += deltatime
        midiSolver(message)
        #print("@%0.6f %r" % (deltatime, message))

port = sys.argv[1] if len(sys.argv) > 1 else None
try:
    midiin, port_name = open_midiport(port, use_virtual = True, client_name=client_name, port_name="in")
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler(port_name))

print("Entering main loop. Press Control-C to exit.")
try:
    # just wait for keyboard interrupt in main thread
    testAll()
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin

