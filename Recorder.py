#!/bin/env python3

# thanks to https://stackoverflow.com/questions/18406570/python-record-audio-on-detected-sound#50340723

import pyaudio
import math
import struct
import wave
import time
import os

Threshold = 0.5

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
swidth = 2


# seconds of silence after audio signal to trigger stop()
TIMEOUT_LENGTH = 1

EXIT_AFTER_SECONDS = 20

f_name_directory = r'./'

class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.startTime = time.time()
        self.jobDone = False
        self.resultFile = ""
        self.armed = False
        self.recorderReady = False
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)

    def record(self):
        self.jobDone = False
        print('Noise detected, recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold: end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        self.write(b''.join(rec))

    def write(self, recording):
        n_files = len(os.listdir(f_name_directory))
        filename = os.path.join(f_name_directory, '{}.wav'.format(n_files))

        filename = os.path.join(f_name_directory, 'current.wav')
        self.resultFile = filename

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        print('Written to file: {}'.format(filename))
        self.jobDone = True
        self.unarm()



    def getRecordingResult(self):
        return self.resultFile

    async def getRecordingResultAsync(self):
        while not self.jobDone:
            continue

        return self.resultFile

    def unarm(self):
        print('unarming...')
        self.armed = False

    async def arm(self):
        while True:
            if self.recorderReady == True:
                print('arming...')
                self.startTime = time.time()
                self.armed = True
                return
        

    def listen(self):
        print('setting up recorder. waiting for arming...')
        self.armed = False
        self.recorderReady = True
        
        while True:
            if self.armed == False:
                input = None
                continue

            input = self.stream.read(chunk)
            rms_val = self.rms(input)
            if rms_val > Threshold:
                #print("still in record loop")
                self.record()

            if self.jobDone == True:
                input = None
                #return self.resultFile

            if time.time() - self.startTime > EXIT_AFTER_SECONDS:
                input = None
                self.resultFile = None
                print(" unable to detect audio. aborting....")
                self.unarm()
                #return None

#a = Recorder()
#a.listen()