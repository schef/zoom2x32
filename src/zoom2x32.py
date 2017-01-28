#!/usr/bin/env python

import logging
import sys
import time

import rtmidi
from rtmidi.midiutil import open_midiport

client_name = "zoom2x32"
zoom_channel_offset = 224
buttonArray = [0, 0, 0, 0, 0, 0, 0, 0, 0]
reverbArray = [0, 0, 0, 0, 0, 0, 0, 0, 0]
binaryDisplayArray = [0, 0, 0, 0, 0, 0, 0, 0]
lastButtonPressed = [0]
reverbButton = [0]
sysExStart = [0xF0, 0x00, 0x20, 0x32, 0x32]
sysExEnd = [0xF7]

def generateSysEx(channel, volume):
    sysEx = []
    hex_data = "/ch/" + str(channel).zfill(2) + "/mix/14/level " + str(volume)
    print(hex_data)
    hex_array = [int(hex(ord(i)), 16) for i in hex_data]
    return(hex_array)

def binaryDisplay(number):
    binaryDisplayArray[7] = number & int('10000000', 2)
    binaryDisplayArray[6] = number & int('01000000', 2)
    binaryDisplayArray[5] = number & int('00100000', 2)
    binaryDisplayArray[4] = number & int('00010000', 2)
    binaryDisplayArray[3] = number & int('00001000', 2)
    binaryDisplayArray[2] = number & int('00000100', 2)
    binaryDisplayArray[1] = number & int('00000010', 2)
    binaryDisplayArray[0] = number & int('00000001', 2)
    for e,i in enumerate(binaryDisplayArray):
        if binaryDisplayArray[e] != 0:
            midiout.send_message([144, e+8, 127])
        else:
            midiout.send_message([144, e+8, 0])
    

midiout = rtmidi.MidiOut(name=client_name)
midiout.open_virtual_port("out")
log = logging.getLogger('test_midiin_callback')

logging.basicConfig(level=logging.DEBUG)

def midiSolver(message):
  print(message)
  print(lastButtonPressed[0])
  #faders
  if zoom_channel_offset <= message[0] < zoom_channel_offset + 9:
      channel = message[0]-zoom_channel_offset
      if (channel == 8):
        channel = 70
      #print("176", channel, message[2])
      midiout.send_message([176,channel,message[2]])
  #buttons => select reverb channel
  elif message[0] == 144:
      if 8 <= message[1] <= 15:
          if message[2] == 127:
              buttonArray[message[1]-8] = 1
              lastButtonPressed[0] = message[1]-8
              binaryDisplay(reverbArray[message[1]-8])
          else:
              buttonArray[message[1]-8] = 0
              binaryDisplay(0)
      if message[1] == 91:
          if message[2] == 127:
              buttonArray[8] = 1
              lastButtonPressed[0] = 8
              binaryDisplay(reverbArray[8])
          else:
              buttonArray[8] = 0
              lastButtonPressed[0] = 8
              binaryDisplay(0)
      print(buttonArray)
  #rotator => add reverb by +5
  if message[0] == 176:
      if message[2] == 1:
          print("gore")
          for e,i in enumerate(buttonArray):
              if (i == 1):
                  if(reverbArray[e] < 127):
                      reverbArray[e] += 1
                  if e == 8:
                      midiout.send_message([176, 61, reverbArray[e]])
                  else:
                      midiout.send_message(sysExStart + generateSysEx(e, reverbArray[e]-90) + sysExEnd)
      elif message[2] == 65:
          print("dole")
          for e,i in enumerate(buttonArray):
              if (i == 1):
                  if (reverbArray[e] > 0):
                    reverbArray[e] -= 1
                  if e == 8:
                      midiout.send_message([176, 61, reverbArray[e]])
                  else:
                      midiout.send_message(sysExStart + generateSysEx(e, reverbArray[e]-90) + sysExEnd)
      print(reverbArray)
      binaryDisplay(reverbArray[lastButtonPressed[0]])

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
