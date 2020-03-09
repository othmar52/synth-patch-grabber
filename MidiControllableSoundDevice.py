#!/bin/env python3

import sys
import csv
import re
import random

class SoundPatch:
    def __init__(self, csvDict=None):
        self.msb = None
        self.lsb = None
        self.programchange = None
        self.displayname = None
        self.patchname = None
        self.fileName = None
        self.samplePath = ""
        self.seconds = 0
        self.polyphonic = False
        self.categories = []
        self.wavPeaks = []
        self.notes = []

        if not csvDict:
            return
        for key,value in csvDict.items():
            if hasattr(self, key):
                self.__dict__[key] = value

        self.fileName = self.cleanFileName()

    def cleanFileName(self):
        return re.sub('[^A-Za-z0-9.\-_]', '_', '%s-%s' % (self.displayname , self.patchname))


class MidiControllableSoundDevice:
    def __init__(self, deviceConfig, limitPatchesPerDevice=0):
        self.name = ""
        self.patchConfType = "generic"
        self.msb = [0]
        self.lsb = []
        self.patchRange = []
        self.midiPort = 0
        self.midiChannel = 0
        self.csvPath = ""
        self.soundPatches = []

        for key,value in deviceConfig.items():
            if hasattr(self, key):
                self.__dict__[key] = value

        self.createSoundPatchList()

        if limitPatchesPerDevice > 0:
            self.reduceSoundPatchesToLimit(limitPatchesPerDevice)
        # TODO validate
        # name required for directory
        # add vendor for sub sub directories?
        # soundpatches.displayName has to be unique and length > 0
        # midiChannel positive int

    def createSoundPatchList(self):
        if self.patchConfType == "generic":
            self.createSoundPatchListGeneric()
            return
        if self.patchConfType == "csv":
            self.createSoundPatchListCsv()
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
