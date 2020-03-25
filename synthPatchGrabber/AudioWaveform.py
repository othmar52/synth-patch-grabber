


import wave
import numpy as np


'''
    dirty/simplyfied approach to get values for drawing a waveform
    thanks to https://stackoverflow.com/questions/18625085/how-to-plot-a-wav-file/18625294#answer-42352826
'''
def getWaveformValues(inputWavFile, resolution=2048):

    with wave.open(str(inputWavFile),'r') as wav_file:
        #Extract Raw Audio from Wav File
        signal = wav_file.readframes(-1)
        signal = np.frombuffer(signal, dtype='int16')

        #Split the data into channels
        channels = [[] for channel in range(wav_file.getnchannels())]
        for index, datum in enumerate(signal):
            channels[index%len(channels)].append(datum)

        return recalculateToRange(
            createWavPeakList(channels)
        )


'''
    reduces total values of the 2 channel arrays to limit
    within value iteration the highest value is kept
'''
def createWavPeakList(channelPeaks, limit=1024):

    totalValues = len(channelPeaks[0])
    chunkSize = totalValues/limit

    finalPeaks = []
    chunkPeaks = []
    for idx, chValue in enumerate(channelPeaks[0]):
        if len(chunkPeaks) >= chunkSize:
            finalPeaks.append( max( chunkPeaks ) )
            chunkPeaks = []
        chunkPeaks.append( abs(chValue) )
        chunkPeaks.append( abs(channelPeaks[0][idx]) )

    try:
        finalPeaks.append( max( chunkPeaks ) )
    except ValueError:
        pass

    return finalPeaks


'''
    this forces all list values to be lower than limit
    all values get linear proportionally modified according to highest input value
'''
def recalculateToRange(inputList, limit=640):
    maxValue = max(inputList)
    result = []
    for val in inputList:
        percent = val / (maxValue/100)
        result.append( int(percent * (limit/100)) )

    return result
