#!/bin/env python3


import logging
import subprocess
import time

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
        'normalize', '--peak', str(inputFilePath)
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
