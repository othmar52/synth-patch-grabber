#!/bin/env python3

# pip install websocket-client
# pip install ffmpeg-normalize
# pip install pyaudio


import logging
import time
import subprocess

import sys

#import Recorder
from Recorder import Recorder

def main():
    logging.basicConfig(level=logging.DEBUG)


    rec = Recorder()
    resultFile = rec.listen()
    if resultFile == None:
        print( "TODO log failed recording")

    normalizeWav(resultFile)
    print(resultFile)



    print ( "finished recording" )






def generalCmd(cmdArgsList, description, readStdError = False):
    logging.info("starting %s" % description)    
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
        print ( "ERROR: %s did not complete successfully (error code is %s)" % (description, retcode) )

    logging.info("finished %s in %s seconds" % ( description, '{0:.3g}'.format(time.time() - startTime) ) )
    return processStdOut.decode('utf-8')



def normalizeWav(inputFilePath):
    cmd = [
        'normalize', '--peak', inputFilePath
    ]
    generalCmd(cmd, 'normalize wav (peak)')



if __name__ == "__main__":
    main()