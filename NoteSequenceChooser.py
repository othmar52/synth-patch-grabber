 
#!/bin/env python3

import time
import asyncio
from random import random,randint

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

        # sending sound off sounds pretty bad :/
        # but some sounds never stop playing
        # TODO how to deal with that?
        # maybe decrease device volume via midi CC7?
        self.midiOutWrapper.send_all_sound_off()
    
        self.finishedAllSequences = True

    def generateSequence(self):

        startNote = randint(40,55)
        chordChoice = randint(0,4)
        reverse = randint(0,1)
        noteLength = 0.1 + randint(0,1) + random()
        pause = random()/4
        maxSeqDuration = randint(3,5)
        noteStep = randint(2,8)
        increase = randint(2,7)

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
