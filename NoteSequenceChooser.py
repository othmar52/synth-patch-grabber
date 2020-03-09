 
#!/bin/env python3

import time
import asyncio
import random

'''
    todo: improve choosed notes
    maybe soundPatch properties should affect the notes like "bass" in patch name or category names
'''
class NoteSequenceChooser:
    def __init__(self, midiOutWrapper, soundPatch):
        self.midiOutWrapper = midiOutWrapper
        self.soundPatch = soundPatch
        self.finishedAllSequences = False

    async def sendSequences(self):
        seqs = self.generateSequence()
        for sequence in seqs:
            for note in sequence["notes"]:
                self.midiOutWrapper.note_on(note)
            time.sleep(sequence["duration"])
            for note in sequence["notes"]:
                self.midiOutWrapper.note_off(note)
            time.sleep(sequence["pause"])
            self.midiOutWrapper.send_all_sound_off()
        self.finishedAllSequences = True

    def generateSequence(self):

        startNote = random.randint(40,55)
        chordChoice = random.randint(0,4)
        reverse = random.randint(0,1)
        noteLength = 0.1 + random.randint(0,1) + random.random()
        pause = random.random()/4
        maxSeqDuration = random.randint(3,5)
        noteStep = random.randint(2,8)
        increase = random.randint(2,7)

        seq = []
        seqDuration = 0
        loop = 0
        
        while True:
            trig = { "notes": [startNote + loop*increase], "duration": noteLength, "pause": pause }
            if chordChoice > 0:
                trig["notes"].append( startNote + loop*increase + noteStep)
                trig["notes"].append( startNote + loop*increase + noteStep*2)
            seq.append(trig)
            seqDuration += noteLength
            seqDuration += pause
            if seqDuration > maxSeqDuration:
                break
            loop += 1
        if reverse > 0:
            seq.reverse()
        return seq
