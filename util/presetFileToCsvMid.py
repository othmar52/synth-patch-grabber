#!/usr/bin/env python3
# coding=utf-8

"""

    Dirty approach to extract preset/patch names from a Waldorf Blofeld Soundset file `blofeld_fact_201200.mid`
    Downloadable via https://support.waldorfmusic.com/files/Blofeld/Sounds/Blofeld_Factory_Soundset_2012.zip

    thanks to https://github.com/francoisgeorgy/midi-file-tools/blob/master/midi-dump.py
    thanks to https://github.com/MaurizioB/Bigglesworth/blob/master/bigglesworth/classes.py [class Sound]
    thanks to https://github.com/MaurizioB/Bigglesworth/blob/master/bigglesworth/const.py [categories]

"""
import argparse
import mido
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="*")
args = parser.parse_args()

blofeldCategories = [
   'Init',
   'Arp',
   'Atmo',
   'Bass',
   'Drum',
   'FX',
   'Keys',
   'Lead',
   'Mono',
   'Pad',
   'Perc',
   'Poly',
   'Seq'
]

limitOutputTo = None
dumpAllChars = False




presets = [
    {
        "midiFile": "presets/waldorf/blofeld/blofeld_fact_201200.mid",
        "vendor": "Waldorf",
        "device": "Blofeld",
        "title": "Factory Presets 2012",
        "idx": {
            "msb": 4,
            "pc": 5,
            "titleBegin": 369,
            "titleEnd": 384,
            "cat": 385
        },
        "categories": blofeldCategories
    },
    {
        "midiFile": "presets/access/virus_a/factory-presets/a.mid",
        "vendor": "Access",
        "device": "Virus A",
        "title": "Factory Presets Bank A",
        "idx": {
            "msb": 6,
            "pc": 7,
            "titleBegin": 248,
            "titleEnd": 257,
            "cat": -1
        }
    },
    {
        "midiFile": "presets/korg/microkorg/microKORG_KorgUSA_Bank/SysEx/microKORG_KorgUSA.syx",
        "vendor": "KORG",
        "device": "Microkorg",
        "title": "USA Bank",
        "idx": {
            "msb": 6,
            "pc": 7,
            "titleBegin": 248,
            "titleEnd": 257,
            "cat": -1
        },
        "categories": []
    },
    {
        "midiFile": "presets/dsi/prophet08/Prophet_08_Programs_v1.0.syx",
        "vendor": "DSI",
        "device": "Prophet 08",
        "title": "sxdhftrjfz",
        "idx": {
            "msb": 6,
            "pc": 7,
            "titleBegin": 248,
            "titleEnd": 257,
            "cat": -1
        },
        "categories": []
    },
    {
        "midiFile": "presets/korg/microkorg/microCuckoo Pack for microKORG/02 All in one Sysex File/MicroCuckoo_FULL_PACK.syx",
        "vendor": "DSI",
        "device": "MicroCoockoo FULL",
        "title": "sxdhftrjfz",
        "idx": {
            "msb": 6,
            "pc": 7,
            "titleBegin": 248,
            "titleEnd": 257,
            "cat": -1
        },
        "categories": []
    },
    {
        #"midiFile": "/mnt/hurewww/mpd/patchgrabber/presets/korg/microkorg/microCuckoo Pack for microKORG/03 Individual Sysex Files/01 Favourites/07 Boston.syx",
        "midiFile": "/mnt/hurewww/mpd/patchgrabber/presets/korg/microkorg/microCuckoo Pack for microKORG/03 Individual Sysex Files/01 Favourites/03 Thunderfat.syx",
        "vendor": "DSI",
        "device": "MicroCoockoo single",
        "title": "sxdhftrjfz",
        "idx": {
            "msb": 6,
            "pc": 7,
            "titleBegin": 248,
            "titleEnd": 257,
            "cat": -1
        },
        "categories": []
    },
    {
        "midiFile": "/mnt/hurewww/mpd/patchgrabber/presets/behringer/deepmind/deepmind_bank-c-4to23.sysex",
        "vendor": "DSI",
        "device": "MicroCoockoo single",
        "title": "sxdhftrjfz",
        "idx": {
            "msb": 6,
            "pc": 7,
            "titleBegin": 248,
            "titleEnd": 257,
            "cat": -1
        },
        "categories": []
    },
    {
        #"midiFile": "presets/novation/nova/Novation Nova OS2 Banks/OS 2.0 Program bank/pbankc.mid",
        "midiFile": "presets/novation/nova/Novation Nova OS2 Banks/OS 2.0 MIDI file/SIIKos2.MID",
        "vendor": "Novation",
        "device": "Nova OS 2.0",
        "title": "sxdhftrjfz",
        "idx": {
            "msb": 9,
            "pc": 8,
            #"titleBegin": 9,
            #"titleEnd": 26,
            "titleBegin": 9,
            "titleEnd": 826,
            "cat": -1
        },
        'skip': 1, # there are twice amount of messages
        "categories": []
    }
]


def main():
    presetToCsv(presets[5])

def presetToCsv(preset):

    mid = mido.read_syx_file(preset["midiFile"])
    mido.write_syx_file('patch.txt', mid, plaintext=True)
    mid = mido.MidiFile(preset["midiFile"])
    #print(mid)

    try:
        skip =  preset["skip"]
    except KeyError:
        skip = 0

    for i, track in enumerate(mid.tracks):
        counter = 0
        for m,msg in enumerate(track):


            #if skip != 0 and not m % 2:
            #    continue
            #print("--------------------------------", m)
            try:
                print("--------------------------------", m,  msg.data[3], msg.data[4], msg.data[5], msg.data[6], msg.data[7], msg.data[8], msg.data[9], msg.data[10], msg.data[11], msg.data[12])
                allChars = []
                patchNameChars = []
                for idx,chrOrd in enumerate(msg.data):
                    allChars.append(chr(chrOrd))

                    if idx < preset["idx"]["titleBegin"] or idx > preset["idx"]["titleEnd"]:
                        continue
                    patchNameChars.append(chr(chrOrd))

                try:
                    categoryString = preset["categories"][msg.data[preset["idx"]["cat"]]]
                except IndexError:
                    categoryString = ""

                patchName = ''.join(patchNameChars).strip()

                msb = str(msg.data[preset["idx"]["msb"]])
                pc = str(msg.data[preset["idx"]["pc"]])

                if dumpAllChars:
                    print(''.join(allChars).strip() )
                else:
                    print('"' + '","'. join([msb,pc,patchName,categoryString]) + '"' )


                counter += 1
                if limitOutputTo == None:
                    continue
                if counter > limitOutputTo:
                    sys.exit()
            except AttributeError:
                continue


if __name__ == "__main__":
    main()
