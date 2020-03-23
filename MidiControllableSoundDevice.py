#!/bin/env python3

import sys
import csv
import re
import random
import json

class SoundPatch:
    def __init__(self, csvDict=None):
        self.msb = None
        self.lsb = None
        self.programchange = None
        self.displayname = None
        self.patchname = None
        self.fileName = None
        self.samplePath = ""
        self.creator = ""
        self.duration = 0
        self.polyphonic = False
        self.categories = []
        self.wavPeaks = []
        self.notes = []
        self.video = {
            'startSecond': 0,
            'endSecond': 0
        }
        self.digitakt = {
            'bank': "",
            'sbnk': "",
            'programchange': ""
        }

        if not csvDict:
            return
        for key,value in csvDict.items():
            if hasattr(self, key):
                self.__dict__[key] = value

            if key == 'digitakt-bank':
                self.digitakt['bank'] = value
            if key == 'digitakt-sbnk':
                self.digitakt['sbnk'] = value
            if key == 'digitakt-programchange':
                self.digitakt['programchange'] = value

        # split chars ar '/' and ','
        self.categories = re.split(r"[\/,]+", self.categories)

        self.fileName = self.cleanFileName()

    def cleanFileName(self):
        return re.sub('[^A-Za-z0-9.\-_]', '_', '%s-%s' % (self.displayname , self.patchname))

    # TODO persist fired note sequences in sound sample json. but how?
    # maybe its better to have a pool of MIDI-note files and persist just the reference!?
    def persistJson(self, noteSequence=[]):
        patchDict = {
            'patchname': self.patchname,
            'displayname': self.displayname,
            'msb': self.msb,
            'lsb': self.lsb,
            'programchange': self.programchange,
            'samplepath': self.samplePath,
            'categories': self.categories,
            'creator': self.creator,
            'duration': self.duration,
            'digitakt': self.digitakt,
            'wavPeaks': self.wavPeaks
        }
        with open(self.samplePath + '.json', 'w') as jsonFile:
            json.dump(patchDict, jsonFile, indent=2)
        


class MidiControllableSoundDevice:
    def __init__(self, deviceConfig, limitPatchesPerDevice=0):
        self.uniquePrefix = ""
        self.vendor = ""
        self.model = ""
        self.patchSetName = ""
        self.yearOfConstruction = 0

        
        self.patchConfType = "generic"
        self.msb = [0]
        self.lsb = []
        self.patchRange = []
        self.midiPort = 0
        self.midiChannel = 0
        self.csvPath = ""
        self.soundPatches = []
        self.video = {}

        for key,value in deviceConfig.items():
            if hasattr(self, key):
                self.__dict__[key] = value

        self.createSoundPatchList()

        if limitPatchesPerDevice > 0:
            self.reduceSoundPatchesToLimit(limitPatchesPerDevice)
        # TODO validate
        # vendor + model + patchSetName required for directory
        # add vendor for sub sub directories?
        # soundpatches.displayName has to be unique and length > 0
        # midiChannel positive int
        # all necessary additional config for type video-csv

    def createSoundPatchList(self):
        if self.patchConfType == "generic":
            self.createSoundPatchListGeneric()
            return
        if self.patchConfType == "csv":
            self.createSoundPatchListCsv()
            return
        if self.patchConfType == "video-csv":
            self.createSoundPatchListVideoCsv()
            return

        raise Exception('invalid config ' , self.patchConfType)

    def createSoundPatchListGeneric(self):
        for idx, bankNumber in enumerate(self.msb):
            for programNumber in self.patchRange:
                s = SoundPatch()
                s.msb = bankNumber
                s.programchange = programNumber
                s.displayname = chr(65+idx) + str(programNumber).zfill(3)
                self.soundPatches.append( s )

    def createSoundPatchListCsv(self):
        with open(self.csvPath, newline='') as csvfile:
            for rowDict in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
                s = SoundPatch(rowDict)
                self.soundPatches.append( s )

    def createSoundPatchListVideoCsv(self):
        with open(self.csvPath, newline='') as csvfile:
            for rowDict in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
                s = SoundPatch(rowDict)
                s.video['startSecond'] = float( rowDict[ self.video['col-start'] ]) + float(self.video['delta-start'])
                s.video['endSecond'] = float( rowDict[ self.video['col-end'] ] )
                self.soundPatches.append( s )

    '''
        the full list of soundpatches gets shuffled and reducet to <limit>
        this is for some kind of dry run/check if all devices produces capturable sound
    '''
    def reduceSoundPatchesToLimit(self, limit):
        reducedPatchList = []
        random.shuffle(self.soundPatches)
        for s in self.soundPatches:
            if len(reducedPatchList) >= limit:
                break
            reducedPatchList.append(s)
        self.soundPatches = reducedPatchList

    def persistJson(self, targetFilePath, sampleJsonPaths={}):
        deviceConf = {
            'uniquePrefix': self.uniquePrefix,
            'vendor': self.vendor,
            'model': self.model,
            'yearOfConstruction': self.yearOfConstruction,
            'patchSetName': self.patchSetName,
            'midiChannel': self.midiChannel,
            'sampleJsonPaths' : sampleJsonPaths
        }
        with open(targetFilePath, 'w') as jsonFile:
            json.dump(deviceConf, jsonFile, indent=2)
