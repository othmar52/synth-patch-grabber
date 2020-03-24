# synth-patch-grabber
automatically create/record audio samples of all your synthesizer presets  

probably the best description is:  
**synth-patch-grabber** is a some kind of a bot that is looping through all your presets of all your midi controllable hardware synthesizers. Playing all kinds of notes (short, long, lower keys, upper keys, chords, etc.) and records each incoming sound to a single audio sample.  
the created database (`.mp3` & `.json` files) of probably ten thousands of audio samples is going to be the basis for https://github.com/othmar52/synthspiration  

## who is it for?
Owners of hardware synthesizers who's synthese skills are not as good as it should be.  
And finding themself in situations of switching through tons of presets/patches until finding an inspiring sound or even finding  a synthesizer to play around with.

## requirements
  * synthesizers, synthesizers, synthesizers... (the more, the better)
  * MIDI interface (output) for sending bankSelect, programChange, noteOn, noteOff events
  * audio interface for recording incoming audio produced by the synthesizers
  * python3 with some additional packages (rtmidi, numpy, TODO:complete this list)
  * ffmpeg
  * ffprobe
  * some configuration for each connected synthesizer (midi channel, available banks, program change range,...)

## current status/TODO's
quick and dirty proof-of-concept for automatically creating a huge sound database but basically everything is working.  
  * hardcoded synthesizer configuration has to be replaced by yaml files  
  * decision which MIDI notes should be played needs improvement  
  * documentation of configuration is missing  
  * add argument parser  
  * proper implementation of error handling  
  * implement a **dry run**-mode to address configuration-/audio-routing-/midi-routing- problems as the script may run for days (in case you have hundrets of hardware synths)  

