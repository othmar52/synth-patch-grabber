 
#!/bin/env python3

import time
import re
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

    '''
        TODO improve decision which notes should be played
        by searching for phrases in patchName and categories
            "perc"    -> play very short notes as it often percussive
            "bs,bass" -> play notes from the lower half
            "poly"    -> play chords
            "pad"     -> play long notes (and chords?)
            ...
    '''
    def generateSequence(self):

        # the lowest note
        startNote = self.chooseStartNote()

        # time between noteOn and noteOff [seconds]
        noteLength = self.chooseNoteLength()

        # play 3 notes simultaneously
        chordChoice = self.chooseChord()

        # distance between chord notes ( only relevant if chordChoice > 0 )
        noteStep = self.chooseNoteStep()

        # time between noteOff and noteOn [seconds]
        pause = random()/4

        # reverse the sequence?
        reverse = randint(0,1)

        # distance between the played notes/chords when triggering again
        increase = randint(2,7)

        # maximum length [seconds] of fired notes
        # (some sounds with reverb/delay/release will cause a longer audio sample)
        maxSeqDuration = randint(3,5)


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

    def chooseStartNote(self):
        if self.findPhrase("bass") == True:
            return randint(30,40)

        return randint(40,55)

    def chooseNoteStep(self):
        if self.findPhrase("bass") == True:
            return randint(1,2)

        return randint(2,8)

    def chooseChord(self):
        if self.findPhrase("bass") == True:
            return 0

        return randint(0,4)

    def chooseNoteLength(self):
        if self.findPhrase("kick") == True:
            return 0.1 + randint(0,1)

        if self.findPhrase("pad") == True:
            return 1 + randint(1,2)

        return 0.1 + randint(0,1) + random()

    def findPhrase(self, term):
        searchList = self.soundPatch.categories[:]
        searchList.append(self.soundPatch.patchname)
        for strings in searchList:
            if re.match(r''+term, strings, re.IGNORECASE):
                return True

        return False
