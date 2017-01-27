#!/usr/bin/env python

import logging
import sys
import time

import rtmidi
from rtmidi.midiutil import open_midiport

client_name = "zoom2x32"
zoom_channel_offset = 224
buttonArray = [0, 0, 0, 0, 0, 0, 0, 0]
reverbArray = [0, 0, 0, 0, 0, 0, 0, 0]

midiout = rtmidi.MidiOut(name=client_name)
midiout.open_virtual_port("out")
log = logging.getLogger('test_midiin_callback')

logging.basicConfig(level=logging.DEBUG)

def midiSolver(message):
  print(message)
  #faders
  if zoom_channel_offset <= message[0] < zoom_channel_offset + 9:
      channel = message[0]-zoom_channel_offset
      if (channel == 8):
        channel = 70
      #print("176", channel, message[2])
      midiout.send_message([176,channel,message[2]])
  #buttons => select reverb channel
  elif message[0] == 144:
      if message[2] == 127:
          buttonArray[message[1]-8] = 1
      else:
          buttonArray[message[1]-8] = 0
      print(buttonArray)
  #rotator => add reverb by +5
  if message[0] == 176:
      if message[2] == 1:
          print("gore")
          for e,i in enumerate(buttonArray):
              if (i == 1):
                  if(reverbArray[e] < 122):
                      reverbArray[e] += 5
                  else:
                      reverbArray[e] = 127
                  midiout.send_message([176, e+8, reverbArray[e]])
      elif message[2] == 65:
          print("dole")
          for e,i in enumerate(buttonArray):
              if (i == 1):
                  if (reverbArray[e] > 5):
                    reverbArray[e] -= 5
                  else:
                    reverbArray[e] = 0
                  midiout.send_message([176, e+8, reverbArray[e]])
      print(reverbArray)

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
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin
