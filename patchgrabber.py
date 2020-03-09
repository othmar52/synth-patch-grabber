#!/bin/env python3

# pip install websocket-client
# pip install ffmpeg-normalize
# pip install pyaudio


import logging
import time
import rtmidi
import subprocess
import sys
import re
import os
import asyncio
import threading

from pathlib import Path
from shutil import copyfile, move, rmtree

from MidiControllableSoundDevice import MidiControllableSoundDevice
from MidiOutWrapper import MidiOutWrapper
from NoteSequenceChooser import NoteSequenceChooser
from Recorder import Recorder

async def main():
    logging.basicConfig(level=logging.DEBUG)


    deviceConfigs = [
        #{
        #    "patchConfType": "csv",
        #    "name": "Roland - JD-Xi ana",
        #    "midiPort": 3,
        #    "midiChannel": 3,
        #    "csvPath": "csv/patchlist/Roland - JD-Xi ana.csv"
        #},
        {
            "patchConfType": "csv",
            "name": "Roland - JD-Xi digi",
            "midiPort": 3,
            "midiChannel": 1,
            "csvPath": "csv/patchlist/Roland - JD-Xi dig.csv"
        },
        {
            "patchConfType": "csv",
            "name": "GEM - rp-x",
            "midiPort": 2,
            "midiChannel": 4,
            "csvPath": "csv/patchlist/GEM - rp-x.csv"
        },
        {
            "patchConfType": "csv",
            "name": "Virus",
            "midiPort": 3,
            "midiChannel": 7,
            "csvPath": "csv/patchlist/Access - VirusA.csv"
        },
        {
            "patchConfType": "csv",
            "name": "System1",
            "midiPort": 3,
            "midiChannel": 5,
            "csvPath": "csv/patchlist/Roland - System1.csv"
        },
        {
            "patchConfType": "csv",
            "name": "Roland - TB-3",
            "midiPort": 3,
            "midiChannel": 9,
            "csvPath": "csv/patchlist/Roland - TB-3.csv"
        },
        {
            "patchConfType": "csv",
            "name": "MicroKORG",
            "midiPort": 3,
            "midiChannel": 6,
            "csvPath": "csv/patchlist/KORG - MicroKORG.csv"
        },
        {
            "patchConfType": "csv",
            "name": "MFB - Synth2",
            "midiPort": 3,
            "midiChannel": 8,
            "csvPath": "csv/patchlist/MFB - Synth2.csv"
        },
        {
            "patchConfType": "csv",
            "name": "KORG - MS2000",
            "midiPort": 3,
            "midiChannel": 15,
            "csvPath": "csv/patchlist/KORG - MS2000.csv"
        },
        #{
        #    "patchConfType": "generic",
        #    "name": "Example of generic device withou csv sounds list",
        #    "msb": [0],
        #    "lsb": [],
        #    "patchRange": range(0,127), # will create [0,1,2,...,125,126]
        #    "midiPort": 3,
        #    "midiChannel": 7
        #}
    ]




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
            "name": "Generic Virus",
            "msb": [1],
            "lsb": [],
            "patchRange": range(40,41),
            "midiPort": 3,
            "midiChannel": 7
        }
    ]

    midiout = rtmidi.MidiOut()

    rec = Recorder()

    #yyy = asyncio.create_task(
    #    rec.listen()
    #)
    #await asyncio.gather(yyy)

    # start recorder thread
    recorderThread = threading.Thread(target=rec.listen)
    recorderThread.start()

    for deviceConfig in deviceConfigs:
        device = MidiControllableSoundDevice(deviceConfig)

        audioSampleDir = Path("./output/%s" % device.name)
        rmtree(audioSampleDir, ignore_errors=True)
        audioSampleDir.mkdir(parents=True, exist_ok=True)


        midiout.open_port(int(device.midiPort))
        mWrapper = MidiOutWrapper(midiout, ch=int(device.midiChannel))
        for soundPatch in device.soundPatches:
            print( '%s %s %s %s %s' % (device.name, soundPatch.displayname, soundPatch.patchname, str(soundPatch.msb), str(soundPatch.programchange)))
            # fire MIDI bank select and program change
            bankSelectArgs = { 'msb': int(soundPatch.msb) }
            if soundPatch.lsb:
                bankSelectArgs['lsb'] = lsb=int(soundPatch.lsb)

            mWrapper.send_bank_select(**bankSelectArgs)
            mWrapper.program_change(program=int(soundPatch.programchange))
            time.sleep(0.2)

            noteSender = NoteSequenceChooser(mWrapper, soundPatch)

            # the async challenge:
            # note sender can have multiple sequences which have to be recorded separately
            # we don't know how long (seconds) the recording will be
            # so we have to use coroutines (thanks to https://realpython.com/async-io-python/ )
            # further we have to tell the notesender if we had been able to capture any audio
            # because some soundpatches require different note length or key number to really produce sound


            #task1 = asyncio.create_task(
            #    rec.listen()
            #)
            #task2 = asyncio.create_task(
            #    noteSender.sendSequences()
            #)
            
            results = await asyncio.gather(
                rec.arm(),
                noteSender.sendSequences(),
                rec.getRecordingResultAsync()
            )

            #xx = await task2
            #yy = await task1
            
            if rec.getRecordingResult() == None or not os.path.isfile(rec.getRecordingResult()):
                print( "TODO log failed recording of %s %s %s" % ( device.name, soundPatch.displayname, soundPatch.patchname))
            else:
                targetFilePath = "%s/%s.wav" % ( str(audioSampleDir), soundPatch.fileName )
                await awaitMoveFile(rec.getRecordingResult(), targetFilePath )
                normalizeWav(str(targetFilePath))
                convertWavToMp3(targetFilePath, "%s/%s.mp3" % ( str(audioSampleDir), soundPatch.fileName ), 320)
                os.unlink(str(targetFilePath))

            rec.unarm()
            del noteSender
        midiout.close_port()

    #recorderThread.exit()
    print ( "yeah")
    sys.exit()
    sys.exit()
    sys.exit()
    sys.exit()
    sys.exit()


    #rec = Recorder()
    #resultFile = rec.listen()
    #if resultFile == None:
    #    print( "TODO log failed recording")

    #normalizeWav(resultFile)
    #print(resultFile)


    #print ( "finished recording" )


#async def audioRecording(rec):
#    return rec.listen()



async def awaitMoveFile(sourcePath, targetPath):
    move(str(sourcePath), str(targetPath))


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

def convertWavToMp3(inputPath, outputPath, bitrate):
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-v', 'quiet', '-stats',
        '-i', str(inputPath),
        '-c:a', 'libmp3lame',
        '-ab', ('%sk'%bitrate),
        str(outputPath)
    ]
    generalCmd(cmd, 'wav to mp3 conversion')

def normalizeWav(inputFilePath):
    cmd = [
        'normalize', '--peak', inputFilePath
    ]
    generalCmd(cmd, 'normalize wav (peak)')



if __name__ == "__main__":
    #main()
    asyncio.run(main())