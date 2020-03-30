#!/bin/env python3
# -*- coding:utf-8 -*-

import csv
import shutil
from tempfile import NamedTemporaryFile


csvPathWithoutEndSecond = "lcdDisplayChange.csv"

tempfile = NamedTemporaryFile(mode='w', delete=False)

def main():
    with open(csvPathWithoutEndSecond, newline='') as csvfile, tempfile:

        dictReader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        headers = dictReader.fieldnames
        headers.extend(["yt-endsecond"])
        headers.extend(["yt-link"])
        writer = csv.DictWriter(tempfile, delimiter=',', quotechar='"', fieldnames=headers)
        writer.writeheader()

        prevPatch = None
        for patchDict in dictReader:
            if prevPatch == None:
                prevPatch = patchDict
                continue
            prevPatch["yt-endsecond"] = patchDict["yt-startsecond"]
            prevPatch["yt-link"] = "https://www.youtube.com/watch?v=UeiKJdvcync#t=" + prevPatch["yt-startsecond"]

            # a single endtime has to be corrected manually to not include non-patchaudio
            if prevPatch["patchnumber"] == "B78":
                prevPatch["yt-endsecond"] = "1808.00"

            print(prevPatch)
            writer.writerow(prevPatch)
            prevPatch = patchDict

    shutil.move(tempfile.name, csvPathWithoutEndSecond + ".withEndsecond.csv")


if __name__ == "__main__":
    main()
