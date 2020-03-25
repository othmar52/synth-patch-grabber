 
#!/bin/env python3


# thanks to https://github.com/SpotlightKid/python-rtmidi/blob/master/examples/advanced/midioutwrapper.py

import rtmidi

from rtmidi.midiconstants import (ALL_NOTES_OFF, ALL_SOUND_OFF, BALANCE, BANK_SELECT_LSB,
                                  BANK_SELECT_MSB, BREATH_CONTROLLER, CHANNEL_PRESSURE,
                                  CHANNEL_VOLUME, CONTROL_CHANGE, DATA_ENTRY_LSB, DATA_ENTRY_MSB,
                                  END_OF_EXCLUSIVE, EXPRESSION_CONTROLLER, FOOT_CONTROLLER,
                                  LOCAL_CONTROL, MIDI_TIME_CODE, NOTE_OFF, NOTE_ON,
                                  NRPN_LSB, NRPN_MSB, PAN, PITCH_BEND, POLY_PRESSURE,
                                  PROGRAM_CHANGE, RESET_ALL_CONTROLLERS, RPN_LSB, RPN_MSB,
                                  SONG_POSITION_POINTER, SONG_SELECT, TIMING_CLOCK)


class MidiOutWrapper:
    def __init__(self, midi, ch=1):
        self.channel = ch
        self._midi = midi

    def channel_message(self, command, *data, ch=None):
        """Send a MIDI channel mode message."""
        command = (command & 0xf0) | ((ch if ch else self.channel) - 1 & 0xf)
        msg = [command] + [value & 0x7f for value in data]
        self._midi.send_message(msg)

    def note_off(self, note, velocity=0, ch=None):
        """Send a 'Note Off' message."""
        self.channel_message(NOTE_OFF, note, velocity, ch=ch)

    def note_on(self, note, velocity=127, ch=None):
        """Send a 'Note On' message."""
        self.channel_message(NOTE_ON, note, velocity, ch=ch)

    def program_change(self, program, ch=None):
        """Send a 'Program Change' message."""
        self.channel_message(PROGRAM_CHANGE, program, ch=ch)

    def send_bank_select(self, bank=None, msb=None, lsb=None, ch=None):
        """Send 'Bank Select' MSB and/or LSB 'Control Change' messages."""
        if bank is not None:
            msb = (bank >> 7) & 0x7F
            lsb = bank & 0x7F

        if msb is not None:
            self.send_control_change(BANK_SELECT_MSB, msb, ch=ch)

        if lsb is not None:
            self.send_control_change(BANK_SELECT_LSB, lsb, ch=ch)

    def send_control_change(self, cc=0, value=0, ch=None):
        """Send a 'Control Change' message."""
        self.send_channel_message(CONTROL_CHANGE, cc, value, ch=ch)

    def send_channel_message(self, status, data1=None, data2=None, ch=None):
        """Send a MIDI channel mode message."""
        msg = [(status & 0xF0) | ((ch if ch else self.channel) - 1 & 0xF)]

        if data1 is not None:
            msg.append(data1 & 0x7F)

            if data2 is not None:
                msg.append(data2 & 0x7F)

        self._midi.send_message(msg)

    def send_all_sound_off(self, ch=None):
        """Send a 'All Sound Off' (CC #120) 'Control Change' message."""
        self.send_control_change(ALL_SOUND_OFF, 0, ch=ch)
