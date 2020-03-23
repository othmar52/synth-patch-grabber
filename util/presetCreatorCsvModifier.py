#!/bin/env python3

'''
    this is a hacky script to extract patch creators from patch names
    some columns get added to the csv file: ["creator-short", "creator-name", "creator-proximity", "original-patchname"]
    and on found creator the column "patchname" gets modified
    the list with creators is "csv/patchlist/creator-shorties.csv"

    for example:
        Before:
            {
                'patchname': 'RingmodFart  SCD'
                ... other existing columns ...
            }
        After:
            {
                'patchname': 'RingmodFart',                # the modified patchname
                ... other existing columns ...
                'creator-short': 'SCD',
                'creator-name': 'Something Completely Different (Boele Gerkes)',
                'creator-proximity': '2',                  # distance in chars to next left charactar
                'original-patchname': 'RingmodFart  SCD'   # backup of unmidified patchname
            }
'''

import csv
import sys
import re
import shutil
from tempfile import NamedTemporaryFile

tempfile = NamedTemporaryFile(mode='w', delete=False)

vendorName = "Waldorf"
csvPathPatches = "csv/patchlist/Waldorf - Blofeld (Factory Presets 2012).csv"


vendorName = "Access"
csvPathPatches = "csv/patchlist/Access - VirusA.csv"

csvPathcreators = "csv/patchlist/creator-shorties.csv"
def main():

    creators = getCreatorsForVendor(vendorName)
    #print(creators)
    with open(csvPathPatches, newline='') as csvfile, tempfile:

        dictReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        headers = dictReader.fieldnames
        headers.extend(["creator-short", "creator-name", "creator-proximity", "original-patchname"])
        writer = csv.DictWriter(tempfile, delimiter=',', quotechar='"', fieldnames=headers)
        writer.writeheader()

        for patchDict in dictReader:
            proximity = -1
            for creator in creators:
                for short,name in creator.items():
                    for whiteSpaceLen in reversed(range(10)):
                        match = re.match(r"(.*)" +(" " * whiteSpaceLen) + short + "$", patchDict["patchname"])
                        if match:
                            proximity = whiteSpaceLen
                            patchDict["creator-short"] = short
                            patchDict["creator-name"] = name
                            patchDict["creator-proximity"] = proximity
                            patchDict["original-patchname"] = patchDict["patchname"]
                            patchDict["patchname"] = match[1].strip()
                            writer.writerow(patchDict)
                            break
                if proximity > -1:
                    break
            if proximity > -1:
                continue
            writer.writerow(patchDict)
    shutil.move(tempfile.name, csvPathPatches + ".creators.csv")


def getCreatorsForVendor(vendor):
    creators = []
    with open(csvPathcreators, newline='') as csvfile:
        for rowDict in csv.DictReader(csvfile, delimiter=',', quotechar='"'):
            vendors = rowDict["vendors"].split(",")
            if vendor in vendors:
                creators.append({ rowDict["short"]: rowDict["name"] })

    return creators

if __name__ == "__main__":
    main()
