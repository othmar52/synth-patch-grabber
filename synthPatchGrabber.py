#!/bin/env python3


import logging
import time
import rtmidi
import subprocess
import sys
import re
import os
import asyncio
import threading

import json

from pathlib import Path
from shutil import copyfile, move, rmtree

from synthPatchGrabber.AudioProcessing import *
from synthPatchGrabber.AudioWaveform import *
from synthPatchGrabber.Config import *
from synthPatchGrabber.MidiOutWrapper import MidiOutWrapper
from synthPatchGrabber.NoteSequenceChooser import NoteSequenceChooser
from synthPatchGrabber.Recorder import Recorder
from synthPatchGrabber.MidiControllableSoundDevice import MidiControllableSoundDevice


async def main():
    logging.basicConfig(level=logging.INFO)

    # for debugging purposes
    limitPatchesPerDevice = 2

    deviceConfigs = getDeviceConfigs()

    midiout = rtmidi.MidiOut()
    rec = Recorder()

    # start recorder thread
    recorderThread = threading.Thread(target=rec.listen)
    recorderThread.start()

    
    for deviceConfig in deviceConfigs:
        device = MidiControllableSoundDevice(deviceConfig, limitPatchesPerDevice)

        rmtree(device.audioSampleDir, ignore_errors=True)
        device.audioSampleDir.mkdir(parents=True, exist_ok=True)

        midiout.open_port(int(device.midiPort))
        mWrapper = MidiOutWrapper(midiout, ch=int(device.midiChannel))

        success = False
        wav2Mp3 = True
        for soundPatch in device.soundPatches:
            print(soundPatch.whoAreYou())
            if device.patchConfType == "video-csv":
                extractAudioFromTo(
                    device.video["path"],
                    soundPatch.video['startSecond'],
                    soundPatch.video['endSecond'],
                    soundPatch.samplePath
                )

                # we temporary need a wav file to create a waveform
                convertMp3ToWav(soundPatch.samplePath, soundPatch.tempWavPath)
                # but will not reconvert it back to mp3 as we already have a mp3
                wav2Mp3 = False

                success = True

            else:
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
                
                if rec.getRecordingResult() == None or not os.path.isfile(rec.getRecordingResult()):
                    success = False
                else:
                    await awaitMoveFile(rec.getRecordingResult(), soundPatch.tempWavPath )
                    success = True

                rec.unarm()
                del noteSender

            if not success:
                logging.warning( "TODO: log failed recording of %s %s %s" % ( device.model, soundPatch.displayname, soundPatch.patchname))
                continue

            if wav2Mp3:
                normalizeWav(soundPatch.tempWavPath)
                convertWavToMp3(soundPatch.tempWavPath, soundPatch.samplePath, 320)

            soundPatch.duration = detectDuration(soundPatch.samplePath)
            soundPatch.wavPeaks = getWaveformValues(soundPatch.tempWavPath)

            os.unlink(str(soundPatch.tempWavPath))
            soundPatch.persistJson()
            device.patchJsonPaths[soundPatch.uniqueIdentifier] = str(soundPatch.jsonPath)

        device.persistJson()
        midiout.close_port()

    #recorderThread.exit()
    print ( "finished!\nhit Ctrl+C to stop")
    sys.exit()


async def awaitMoveFile(sourcePath, targetPath):
    move(str(sourcePath), str(targetPath))


'''
    this function does not record any samples but checks all csv based properties
    and updates the json with metadata in case it exists
'''
def updateFromCsv():
    deviceConfigs = getDeviceConfigs()
    for deviceConfig in deviceConfigs:
        device = MidiControllableSoundDevice(deviceConfig)
        if device.patchConfType != "csv" and device.patchConfType != "video-csv":
            # only csv based sample properties makes sense here
            continue

        for soundPatch in device.soundPatches:
            try:
                with open(soundPatch.jsonPath, 'r') as jsonFile:
                    oldJsonData = json.load(jsonFile)
            except FileNotFoundError:
                continue

            # copy only properties that does not exist in the csv file
            soundPatch.samplepath = oldJsonData['samplepath']
            soundPatch.duration = oldJsonData['duration']
            soundPatch.wavPeaks = oldJsonData['wavPeaks']
            soundPatch.persistJson()
    print("done")


if __name__ == "__main__":
    #main()
    #updateFromCsv()
    asyncio.run(main())