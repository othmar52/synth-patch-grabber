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

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="*")
args = parser.parse_args()

categories = [
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

for f in args.files:
    mid = mido.MidiFile(f)
    for i, track in enumerate(mid.tracks):
        counter = 0
        for msg in track:
            try:
                patchNameChars = []
                for idx,chrOrd in enumerate(msg.data):
                    if idx < 369 or idx > 384:
                        continue
                    patchNameChars.append(chr(chrOrd))

                print(''.join(patchNameChars).strip(), categories[msg.data[385] ] )
                counter += 1
                if limitOutputTo == None:
                    continue
                if counter > limitOutputTo:
                    sys.exit()
            except (AttributeError, IndexError) as e:
                continue
