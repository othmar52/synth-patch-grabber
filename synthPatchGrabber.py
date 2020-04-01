#!/bin/env python3


import logging
import time
import rtmidi
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
    limitPatchesPerDevice = 0

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
    terminalWidth, terminalHeight = os.get_terminal_size()
    for deviceConfig in deviceConfigs:
        device = MidiControllableSoundDevice(deviceConfig)
        device.persistJson()
        if device.patchConfType != "csv" and device.patchConfType != "video-csv":
            # only csv based sample properties makes sense here
            continue

        for soundPatch in device.soundPatches:
            try:
                with open(soundPatch.jsonPath, 'r') as jsonFile:
                    oldJsonData = json.loads(jsonFile.read().replace('var sampleData = ', ''))
            except FileNotFoundError:
                continue

            print(soundPatch.whoAreYou(terminalWidth), end='\r', flush=True)

            # copy only properties that does not exist in the csv file
            soundPatch.samplepath = oldJsonData['samplepath']
            soundPatch.duration = oldJsonData['duration']
            soundPatch.wavPeaks = oldJsonData['wavPeaks']
            soundPatch.persistJson()
    print("done")


'''
    currently only jsons gets generated
    because there is no webgui yet
'''
def updateWebGui():
    preCollect = {
        'categories': {},
        'devices': []
    }

    bigData = {
        'jsonPaths': {},
        'categories': {},
        'devices': {},
        'devicConf': {}
    }
    deviceConfigs = getDeviceConfigs()

    # first run: collect all available 
    for deviceConfig in deviceConfigs:
        device = MidiControllableSoundDevice(deviceConfig)

        preCollect['devices'].append(device.uniquePrefix)

        for soundPatch in device.soundPatches:
            try:
                with open(soundPatch.jsonPath, 'r') as jsonFile:
                    oldJsonData = json.loads(jsonFile.read().replace('var sampleData = ', ''))
            except FileNotFoundError:
                continue

            bigData['jsonPaths'][oldJsonData['uniqueIdentifier']] = soundPatch.jsonPath
            for cat in oldJsonData['categories']:
                cat = normalizeCategory(cat)
                preCollect['categories'][cat] = True


    # 2nd run: create blacklist and whitelist vor everything

    terminalWidth, terminalHeight = os.get_terminal_size()

    for deviceConfig in deviceConfigs:
        device = MidiControllableSoundDevice(deviceConfig)

        try:
            with open(device.jsonPath, 'r') as jsonFile:
                deviceJsonData = json.load(jsonFile)
                deviceJsonData['sampleJsonPaths'] = {}
                bigData['devicConf'][ device.uniquePrefix ] = deviceJsonData
        except FileNotFoundError:
            continue

        for soundPatch in device.soundPatches:
            try:
                with open(soundPatch.jsonPath, 'r') as jsonFile:
                    oldJsonData = json.loads(jsonFile.read().replace('var sampleData = ', ''))
            except FileNotFoundError:
                continue
            print(soundPatch.whoAreYou(terminalWidth), end='\r', flush=True)
            sampleId = oldJsonData['uniqueIdentifier']

            for key in preCollect['devices']:
                if key not in bigData['devices']:
                    bigData['devices'][key] = {
                        'lengths': {
                            'black': 0,
                            'white': 0,
                        },
                        'black' : [],
                        'white' : [],
                        'all': {}
                    }

                if key == device.uniquePrefix:
                    bigData['devices'][key]['white'].append(sampleId)
                    bigData['devices'][key]['all'][sampleId] = "white"
                    bigData['devices'][key]['lengths']['white'] += 1
                else:
                    bigData['devices'][key]['black'].append(sampleId)
                    bigData['devices'][key]['all'][sampleId] = "black"
                    bigData['devices'][key]['lengths']['black'] += 1


            for value,key in enumerate(preCollect['categories']):
                blackOrWhite = "black"
                if key not in bigData['categories']:
                    bigData['categories'][key] = {
                        'lengths': {
                            'black': 0,
                            'white': 0,
                        },
                        'black' : [],
                        'white' : [],
                        'all': {}
                    }
                if len(oldJsonData['categories']) == 0:
                    oldJsonData['categories'] = ['']

                for cat in oldJsonData['categories']:
                    if key == normalizeCategory(cat):
                        blackOrWhite = "white"
    
                bigData['categories'][key][blackOrWhite].append(sampleId)
                bigData['categories'][key]['all'][sampleId] = blackOrWhite
                bigData['categories'][key]['lengths'][blackOrWhite] += 1


    bigData['categories'] = resortCategories(bigData['categories'])


    with open('output/bigData.json', 'w') as jsonFile:
        jsonFile.write("let bigData = ")
        json.dump(bigData, jsonFile, indent=2)

    print("")
    print("done")


''' order by amount '''
def resortCategories(inputDict):
    totals = {}
    for key,value in inputDict.items():
        totals[key] = value['lengths']['white']

    ordered = {k: v for k, v in sorted(totals.items(), key=lambda item: item[1], reverse=True)}

    result = {}
    for key,value in ordered.items():
        result[key] = inputDict[key]

    return result

def normalizeCategory(inputString):
    if inputString == '':
        return 'None'
    norm = {
        'Keyboard': ['KBD', 'Keyboards', 'Keys'],
        'Arpeggio': ['Arp'],
        'Atmo': ['Background'],
        'Input/Vocoder': ['Vocoder', 'Voice Like', 'Mic Input'],
        'Lead': ['Synth Lead'],
        'Pad': ['Pads'],
        'None': ['Other']
    }
    for key, values in norm.items():
        for value in values:
            if inputString.lower() == value.lower():
                return key

    return inputString
    

if __name__ == "__main__":
    #main()
    updateFromCsv()
    updateWebGui()
    #asyncio.run(main())