# synth-patch-grabber
create audio samples of all your synthesizer presets  

probably the best description is:  
**synth-patch-grabber** is a bot that is looping through all your prests of all your midi controllable hardware synthesizers. Playing all kinds of notes (short, long, lower keys, higher keys, chords, etc.) and records each incoming sound to a single audio sample.  
the created database of probably ten thousands of audio samples is the basis for https://github.com/othmar52/synthspiration  

## who is it for?
Owners of hardware synthesizers who's synthese skills are not as good as it should be.  
And finding themself in situations of switching through tons of presets/patches until finding an inspiring sound to play around with

## requirements
  * MIDI interface (output) for sending bankSelect, programChange, noteOn, noteOff events
  * audio interface for recording
  * python3 with some additional libs (rtmidi, numpy, TODO:complete this list)
  * ffmpeg
  * ffprobe

## current status/TODO's
quick and dirty proof-of-concept but basically everything is working.  
hardcoded synthesizer configuration has to be replaced by yaml files  
decision which MIDI notes should be played needs improvement  
documentation of configuration is missing  

