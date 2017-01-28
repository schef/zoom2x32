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

