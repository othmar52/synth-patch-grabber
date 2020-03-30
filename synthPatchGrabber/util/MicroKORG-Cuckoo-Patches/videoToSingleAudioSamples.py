#!/bin/env python3
# -*- coding:utf-8 -*-

import sys
import csv
import re
import random
import json
import logging
import subprocess
import time

from pathlib import Path
from shutil import copyfile, move, rmtree


videoPath = "128 NEW microKorg patches-UeiKJdvcync.webm"
csvPathWithStartEndSecond = "../../csv/patchlist/KORG - MicroKORG (Cuckoo Patches).csv"

targetDir = "../../output/MicroKORG/CuckooPatches2018"

# avoid very short noize from previous patch
applyOffsetSeconds = 0.2

def main():
    logging.basicConfig(level=logging.DEBUG)
    prepareTargetDir()
    with open(csvPathWithStartEndSecond, newline='') as csvfile:
        dictReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for patchDict in dictReader:
            extractAudioFromTo(
                videoPath,
                patchDict['yt-startsecond'],
                patchDict['yt-endsecond'],
                '%s/%s-%s.mp3' % ( targetDir, patchDict['displayname'], patchDict['patchname'])
            )
            #print(patchDict)


def prepareTargetDir():
    directory = Path(targetDir)
    rmtree(directory, ignore_errors=True)
    directory.mkdir(parents=True, exist_ok=True)

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

def extractAudioFromTo(inputVideoPath, startSecond, endSecond, outputPath):

    cmd = [
        'ffmpeg',
        '-y', '-hide_banner', '-v', 'quiet', '-stats',
        '-i', str(inputVideoPath),
        '-ss', str(float(startSecond) + applyOffsetSeconds),
        '-to', str(endSecond),
        '-q:a', '0',
        '-map', 'a',
        str(outputPath)
    ]
    generalCmd(cmd, 'extract mp3 portion of video')
    #print(cmd)
    #generalCmd(cmd, 'wav to mp3 conversion')

if __name__ == "__main__":
    main()
