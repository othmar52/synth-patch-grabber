#!/bin/env python3

# pip install websocket-client
# pip install ffmpeg-normalize
# pip install pyaudio


import logging
import time
import rtmidi
import subprocess
import sys

from MidiControllableSoundDevice import MidiControllableSoundDevice
from MidiOutWrapper import MidiOutWrapper
from NoteSequenceChooser import NoteSequenceChooser
from Recorder import Recorder

def main():
    logging.basicConfig(level=logging.DEBUG)

    deviceConfigs = [
        {
            "patchConfType": "csv",
            "name": "MicroKORG",
            "midiPort": 3,
            "midiChannel": 6,
            "csvPath": "csv/patchlist/KORG - MicroKORG.csv"
        },
        {
            "patchConfType": "generic",
            "name": "Example of generic device withou csv sounds list",
            "msb": [0],
            "lsb": [],
            "patchRange": range(0,127),
            "midiPort": 3,
            "midiChannel": 7
        }
    ]

    midiout = rtmidi.MidiOut()

    for deviceConfig in deviceConfigs:
        device = MidiControllableSoundDevice(deviceConfig)

        midiout.open_port(int(device.midiPort))
        mWrapper = MidiOutWrapper(midiout, ch=int(device.midiChannel))

        for soundPatch in device.soundPatches:
            print( '%s %s %s %s %s' % (device.name, soundPatch.displayname, soundPatch.patchname, str(soundPatch.msb), str(soundPatch.programchange)))
            if soundPatch.lsb:
                mWrapper.send_bank_select(msb=int(soundPatch.msb), lsb=int(soundPatch.lsb))
            else:
                mWrapper.send_bank_select(msb=int(soundPatch.msb))
            mWrapper.program_change(program=int(soundPatch.programchange))  # programs counted from zero too!
            time.sleep(0.2)
            noteSender = NoteSequenceChooser(mWrapper, soundPatch)
            noteSender.sendSequences()
            del noteSender

        midiout.close_port()

    print ( "yeah")
    sys.exit()


    rec = Recorder()
    resultFile = rec.listen()
    if resultFile == None:
        print( "TODO log failed recording")

    normalizeWav(resultFile)
    print(resultFile)


    print ( "finished recording" )



def generalCmd(cmdArgsList, description, readStdError = False):
    logging.info("starting %s" % description)    
    logging.debug(' '.join(cmdArgsList))
    startTime = time.time()
    if readStdError:
        process = subprocess.Popen(cmdArgsList, stderr=subprocess.PIPE)
        processStdOut = process.stderr.read()
    else:
        process = subprocess.Popen(cmdArgsList, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        processStdOut = process.stdout.read()
    retcode = process.wait()
    if retcode != 0:
        print ( "ERROR: %s did not complete successfully (error code is %s)" % (description, retcode) )

    logging.info("finished %s in %s seconds" % ( description, '{0:.3g}'.format(time.time() - startTime) ) )
    return processStdOut.decode('utf-8')



def normalizeWav(inputFilePath):
    cmd = [
        'normalize', '--peak', inputFilePath
    ]
    generalCmd(cmd, 'normalize wav (peak)')



if __name__ == "__main__":
    main()