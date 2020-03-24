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
import wave
import numpy as np

from pathlib import Path
from shutil import copyfile, move, rmtree

from MidiControllableSoundDevice import MidiControllableSoundDevice
from MidiOutWrapper import MidiOutWrapper
from NoteSequenceChooser import NoteSequenceChooser
from Recorder import Recorder


def getDeviceConfigs(deviceIdentifier=""):
    # TODO read from separate yaml file
    # TODO validate configuration for missing/invalid values and for uniqueness property "uniquePrefix"
    deviceConfigs = [
        {
            "uniquePrefix": "tb3",
            "vendor": "Roland",
            "model": "TB-3",
            "yearOfConstruction": 2014,
            "patchConfType": "csv",
            "patchSetName": "Factory",
            "midiPort": 3,
            "midiChannel": 9,
            "csvPath": "csv/patchlist/Roland - TB-3.csv"
        },
        {
            "uniquePrefix": "xia",
            "vendor": "Roland",
            "model": "JD-Xi",
            "yearOfConstruction": 2015,
            "patchConfType": "csv",
            "patchSetName": "Factory Analog",
            "midiPort": 3,
            "midiChannel": 3,
            "csvPath": "csv/patchlist/Roland - JD-Xi ana.csv"
        },
        {
            "uniquePrefix": "xid",
            "vendor": "Roland",
            "model": "JD-Xi",
            "yearOfConstruction": 2015,
            "patchConfType": "csv",
            "patchSetName": "Factory Digital",
            "midiPort": 3,
            "midiChannel": 1,
            "csvPath": "csv/patchlist/Roland - JD-Xi dig.csv"
        },
        {
            "uniquePrefix": "rpx",
            "vendor": "GEM",
            "model": "rp-x",
            "yearOfConstruction": 2006,
            "patchConfType": "csv",
            "patchSetName": "Factory",
            "midiPort": 2,
            "midiChannel": 4,
            "csvPath": "csv/patchlist/GEM - rp-x.csv"
        },
        {
            "uniquePrefix": "vir",
            "vendor": "Access",
            "model": "Virus A",
            "yearOfConstruction": 1997,
            "patchConfType": "csv",
            "patchSetName": "Factory",
            "midiPort": 3,
            "midiChannel": 7,
            "csvPath": "csv/patchlist/Access - VirusA.csv"
        },
        {
            "uniquePrefix": "s1f",
            "vendor": "Roland",
            "model": "System-1m",
            "yearOfConstruction": 2014,
            "patchConfType": "csv",
            "patchSetName": "Factory",
            "midiPort": 3,
            "midiChannel": 5,
            "csvPath": "csv/patchlist/Roland - System1.csv"
        },
        {
            "uniquePrefix": "mkf",
            "vendor": "KORG",
            "model": "MicroKORG",
            "yearOfConstruction": 2000,
            "patchConfType": "csv",
            "patchSetName": "Factory",
            "midiPort": 3,
            "midiChannel": 6,
            "csvPath": "csv/patchlist/KORG - MicroKORG.csv"
        },
        {
            "uniquePrefix": "ms2",
            "vendor": "MFB",
            "model": "Synth II",
            "yearOfConstruction": 2004,
            "patchConfType": "csv",
            "patchSetName": "Factory",
            "midiPort": 3,
            "midiChannel": 8,
            "csvPath": "csv/patchlist/MFB - Synth2.csv"
        },
        {
            "uniquePrefix": "mkc",
            "vendor": "KORG",
            "model": "MicroKORG",
            "yearOfConstruction": 2000,
            "patchConfType": "video-csv",
            "patchSetName": "Cuckoo",
            "midiPort": 3,
            "midiChannel": 6,
            "csvPath": "csv/patchlist/KORG - MicroKORG (Cuckoo Patches).csv",
            "video": {
                "path": "util/MicroKORG-Cuckoo-Patches/128 NEW microKorg patches-UeiKJdvcync.webm",
                "col-start": "yt-startsecond",
                "col-end": "yt-endsecond",
                "delta-start": 0.2
            }
        },
        {
            "patchConfType": "csv",
            "uniquePrefix": "wb12",
            "vendor": "Waldorf",
            "model": "Blofeld",
            "yearOfConstruction": 2007,
            "patchSetName": "Factory 2012",
            "midiPort": 3,
            "midiChannel": 11,
            "csvPath": "csv/patchlist/Waldorf - Blofeld (Factory Presets 2012).csv"
        }
        #,
        #{
        #    "patchConfType": "csv",
        #    "patchSetName": "KORG - MS2000",
        #    "midiPort": 3,
        #    "midiChannel": 15,
        #    "csvPath": "csv/patchlist/KORG - MS2000.csv"
        #},
        #{
        #    "patchConfType": "generic",
        #    "patchSetName": "Example of generic device withou csv sounds list",
        #    "msb": [0],
        #    "lsb": [],
        #    "patchRange": range(0,127), # will create [0,1,2,...,125,126]
        #    "midiPort": 3,
        #    "midiChannel": 7
        #}
    ]

    if deviceIdentifier == "":
        return deviceConfigs

    foundIdentifiers = []
    for deviceConfig in deviceConfigs:
        if deviceConfig["uniquePrefix"] == deviceIdentifier:
            return [deviceConfig]
        foundIdentifiers.append(deviceConfig["uniquePrefix"])

    raise ValueError(
        'configuration for "%s" not found.\n valid identifiers are %s' % (
            deviceIdentifier,
            ', '.join(foundIdentifiers)
        )
    )

async def main():
    logging.basicConfig(level=logging.INFO)

    # for debugging purposes
    limitPatchesPerDevice = 2

    deviceConfigs = getDeviceConfigs()


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
        device = MidiControllableSoundDevice(deviceConfig, limitPatchesPerDevice)

        patchJsonPaths = {}

        audioSampleDir = Path("./output/%s/%s/%s" % (device.vendor, device.model, device.patchSetName))
        rmtree(audioSampleDir, ignore_errors=True)
        audioSampleDir.mkdir(parents=True, exist_ok=True)


        midiout.open_port(int(device.midiPort))
        mWrapper = MidiOutWrapper(midiout, ch=int(device.midiChannel))
        for soundPatch in device.soundPatches:
            if device.patchConfType == "video-csv":

                print(
                    device.vendor,
                    device.model,
                    device.patchSetName,
                    soundPatch.displayname,
                    soundPatch.patchname,
                    soundPatch.video['startSecond'],
                    soundPatch.video['endSecond'],
                    device.video["path"]
                )
                targetFilePath = "%s/%s.mp3" % ( str(audioSampleDir), soundPatch.fileName )

                extractAudioFromTo(
                    device.video["path"],
                    soundPatch.video['startSecond'],
                    soundPatch.video['endSecond'],
                    targetFilePath
                )

                soundPatch.samplePath = targetFilePath
                soundPatch.duration = detectDuration(targetFilePath)

                # we temporary need a wav file to create a waveform
                tmpWav = targetFilePath + '.wav'
                convertMp3ToWav(targetFilePath, tmpWav)
                soundPatch.wavPeaks = getWaveformValues(tmpWav)
                os.unlink(tmpWav)

                soundPatch.persistJson(audioSampleDir)
                patchJsonPaths['%s-%s' % ( device.uniquePrefix, soundPatch.displayname)] = targetFilePath + '.json'
            else:
                print(
                    device.vendor,
                    device.model,
                    device.patchSetName,
                    soundPatch.displayname,
                    soundPatch.patchname,
                    str(soundPatch.msb),
                    str(soundPatch.programchange)
                )
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
                    logging.warning( "TODO: log failed recording of %s %s %s" % ( device.model, soundPatch.displayname, soundPatch.patchname))
                else:
                    targetFilePathWav = "%s/%s.wav" % ( str(audioSampleDir), soundPatch.fileName )
                    targetFilePathMp3 = "%s/%s.mp3" % ( str(audioSampleDir), soundPatch.fileName )
                    await awaitMoveFile(rec.getRecordingResult(), targetFilePathWav )
                    normalizeWav(str(targetFilePathWav))
                    convertWavToMp3(targetFilePathWav, targetFilePathMp3, 320)
                    soundPatch.wavPeaks = getWaveformValues(targetFilePathWav)
                    os.unlink(str(targetFilePathWav))
                    soundPatch.samplePath = targetFilePathMp3
                    soundPatch.duration = detectDuration(targetFilePathMp3)
                    soundPatch.persistJson(audioSampleDir)
                    patchJsonPaths['%s-%s' % ( device.uniquePrefix, soundPatch.displayname)] = targetFilePathMp3 + '.json'

                rec.unarm()
                del noteSender
        device.persistJson('%s/00-device.json' % str(audioSampleDir),  patchJsonPaths)
        midiout.close_port()

    #recorderThread.exit()
    print ( "finished!\nhit Ctrl+C to stop")
    sys.exit()


async def awaitMoveFile(sourcePath, targetPath):
    move(str(sourcePath), str(targetPath))


def generalCmd(cmdArgsList, description, readStdError = False):
    logging.debug("starting %s" % description)
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
        logging.critical( "ERROR: %s did not complete successfully (error code is %s)" % (description, retcode) )

    logging.debug("finished %s in %s seconds" % ( description, '{0:.3g}'.format(time.time() - startTime) ) )
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

def convertMp3ToWav(inputPath, outputPath):
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-v', 'quiet', '-stats',
        '-i', str(inputPath),
        '-acodec', 'pcm_s16le',
        '-ar', '44100',
        str(outputPath)
    ]
    generalCmd(cmd, 'mp3 to wav conversion')


def normalizeWav(inputFilePath):
    cmd = [
        'normalize', '--peak', inputFilePath
    ]
    generalCmd(cmd, 'normalize wav (peak)')


def extractAudioFromTo(inputVideoPath, startSecond, endSecond, outputPath):

    cmd = [
        'ffmpeg',
        '-y', '-hide_banner', '-v', 'quiet', '-stats',
        '-i', str(inputVideoPath),
        '-ss', str(startSecond),
        '-to', str(endSecond),
        '-q:a', '0',
        '-map', 'a',
        str(outputPath)
    ]
    generalCmd(cmd, 'extract mp3 portion of video')

def detectDuration(filePath):
    cmd = [
        'ffprobe', '-i', str(filePath),
        '-show_entries', 'format=duration',
        '-v', 'quiet', '-of', 'csv=p=0'
    ]
    processStdOut = generalCmd(cmd, 'detect duration')
    return float(processStdOut.strip())


'''
    dirty/simplyfied approach to get values for drawing a waveform
    thanks to https://stackoverflow.com/questions/18625085/how-to-plot-a-wav-file/18625294#answer-42352826
'''
def getWaveformValues(inputWavFile, resolution=2048):

    with wave.open(str(inputWavFile),'r') as wav_file:
        #Extract Raw Audio from Wav File
        signal = wav_file.readframes(-1)
        signal = np.frombuffer(signal, dtype='int16')

        #Split the data into channels
        channels = [[] for channel in range(wav_file.getnchannels())]
        for index, datum in enumerate(signal):
            channels[index%len(channels)].append(datum)

        return recalculateToRange(
            createWavPeakList(channels)
        )


'''
    reduces total values of the 2 channel arrays to limit
    within value iteration the highest value is kept
'''
def createWavPeakList(channelPeaks, limit=1024):

    totalValues = len(channelPeaks[0])
    chunkSize = totalValues/limit

    finalPeaks = []
    chunkPeaks = []
    for idx, chValue in enumerate(channelPeaks[0]):
        if len(chunkPeaks) >= chunkSize:
            finalPeaks.append( max( chunkPeaks ) )
            chunkPeaks = []
        chunkPeaks.append( abs(chValue) )
        chunkPeaks.append( abs(channelPeaks[0][idx]) )

    try:
        finalPeaks.append( max( chunkPeaks ) )
    except ValueError:
        pass

    return finalPeaks


'''
    this forces all list values to be lower than limit
    all values get linear proportionally modified according to highest input value
'''
def recalculateToRange(inputList, limit=640):
    maxValue = max(inputList)
    result = []
    for val in inputList:
        percent = val / (maxValue/100)
        result.append( int(percent * (limit/100)) )

    return result


if __name__ == "__main__":
    #main()
    asyncio.run(main())