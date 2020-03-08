#!/bin/env python3



# TODO send panic after device change, or after every program change?
# https://github.com/SpotlightKid/python-rtmidi/blob/master/examples/basic/panic.py

import rtmidi
import logging
import time
import sys
import csv

from MidiOutWrapper import MidiOutWrapper

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



def main():
    global midiout

    devices = [
        {
            "type": "csv",
            "name": "MicroKORG",
            "midiPort": 3,
            "midiChannel": 6,
            "csv": "csv/patchlist/KORG - MicroKORG.csv"
        },
        {
            "type": "csv",
            "name": "System1",
            "midiPort": 3,
            "midiChannel": 5,
            "csv": "csv/patchlist/Roland - System1.csv"
        },
        {
            "type": "csv",
            "name": "MFB Synth2",
            "midiPort": 3,
            "midiChannel": 8,
            "csv": "csv/patchlist/MFB - Synth2.csv"
        },
        {
            "type": "csv",
            "name": "Roland JD-Xi ana",
            "midiPort": 3,
            "midiChannel": 3,
            "csv": "csv/patchlist/Roland - JD-Xi ana.csv"
        },
        {
            "type": "csv",
            "name": "Roland JD-Xi digi",
            "midiPort": 3,
            "midiChannel": 1,
            "csv": "csv/patchlist/Roland - JD-Xi dig.csv"
        },
        {
            "type": "csv",
            "name": "Roland TB-3",
            "midiPort": 3,
            "midiChannel": 9,
            "csv": "csv/patchlist/Roland - TB-3.csv"
        },
        {
            "type": "csv",
            "name": "GEM rp-x",
            "midiPort": 2,
            "midiChannel": 4,
            "csv": "csv/patchlist/GEM - rp-x.csv"
        },
        {
            "type": "csv",
            "name": "Virus 1",
            "midiPort": 3,
            "midiChannel": 7,
            "csv": "csv/patchlist/Access - VirusA.csv"
        },
        {
            "type": "csv",
            "name": "KORG - MS2000",
            "midiPort": 3,
            "midiChannel": 15,
            "csv": "csv/patchlist/KORG - MS2000.csv"
        }
        #{
        #    "type": "generic",
        #    "name": "Example of generic device withou csv sounds list",
        #    "msb": [0],
        #    "lsb": [],
        #    "patches": range(0,127),
        #    "midiPort": 3,
        #    "midiChannel": 7
        #}
    ]
    logging.basicConfig(level=logging.DEBUG)
    
    midiout = rtmidi.MidiOut()

    #available_ports = midiout.get_ports()



    mWrapper = None
    for device in devices:
        #if device["midiChannel"] != 15:
        #    continue

        soundPatches = createSoundPatchList(device)

        midiout.open_port(device["midiPort"])
        mWrapper = MidiOutWrapper(midiout,ch=device["midiChannel"])

        for soundPatch in soundPatches:
            print( '%s %s %s %s %s' % (device["name"], soundPatch.displayname, soundPatch.patchname, str(soundPatch.msb), str(soundPatch.programchange)))
            if soundPatch.lsb:
                mWrapper.send_bank_select(msb=int(soundPatch.msb), lsb=int(soundPatch.lsb))
            else:
                mWrapper.send_bank_select(msb=int(soundPatch.msb))
            mWrapper.program_change(program=int(soundPatch.programchange))  # programs counted from zero too!
            time.sleep(0.2)
            sendSequences(mWrapper)


        midiout.close_port()




    del mWrapper
    del midiout



    print ( "finished midi send" )


def createSoundPatchList(device):
    if device["type"] == "generic":
        return createSoundPatchListGeneric(device)
    if device["type"] == "csv":
        return createSoundPatchListCsv(device)

    print("invalid config")
    sys.exit()

def createSoundPatchListGeneric(device):
    patchList = []

    for idx,bankNumber in enumerate(device["msb"]):
        for programNumber in device["patches"]:
            s = SoundPatch()
            s.msb = bankNumber
            s.programchange = programNumber
            s.displayname = chr(65+idx) + str(programNumber).zfill(3)
            patchList.append( s )

    return patchList


def createSoundPatchListCsv(device):
    patchList = []

    with open(device['csv'], newline='') as csvfile:
        for rowDict in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
            s = SoundPatch(rowDict)
            patchList.append( s )
            #print(', '.join(row))

    return patchList

def sendSequences(mo):
    seqs = [
        {
            "notes": [60,64,68],
            "duration": 0.2
        },
        {
            "notes": [45],
            "duration": 1
        }
    ]
    for sequence in seqs:
        for note in sequence["notes"]:
            mo.note_on(note)
        time.sleep(sequence["duration"])
        for note in sequence["notes"]:
            mo.note_off(note)
        mo.send_all_sound_off()
        time.sleep(1)
        #print( sequence )

if __name__ == "__main__":
    main()