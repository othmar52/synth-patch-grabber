#!/bin/env python3

import sys
import csv

class SoundPatch:
    def __init__(self, csvDict=None):
        self.msb = None
        self.lsb = None
        self.programchange = None
        self.displayname = None
        self.patchname = None
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


class MidiControllableSoundDevice:
    def __init__(self, deviceConfig):
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

