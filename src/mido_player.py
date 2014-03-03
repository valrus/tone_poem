from fractions import Fraction
import threading

from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty

from mingus.midi import fluidsynth
from mido.midifiles import MidiFile, MetaMessage

SYNTH = fluidsynth.midi.fs


def midi_tempo_to_bpm(tempo):
    return (1000000 / tempo) * 60


def float_almost_equal(f1, f2):
    """Check that two floats are about the same.

    The precision used here is totally arbitrary but should be fine for
    lengths of midi files.
    """
    return abs(f1 - f2) < 0.0001


class MidiFilePlayer(EventDispatcher):
    def __init__(self, fileName):
        self.mf = MidiFile(fileName)
        self.time_signature = None
        for i, track in enumerate(self.mf.tracks):
            for msg in [m for m in track if isinstance(m, MetaMessage)]:
                if msg.type == 'set_tempo':
                    self.bpm = midi_tempo_to_bpm(msg.tempo)
                elif msg.type == 'time_signature':
                    self.time_signature = (msg.numerator, msg.denominator)

        self.beat_length, self.bar_length = self._calculate_lengths()
        print(self.bar_length)
        print(self.mf.length)

        self.thread = None
        self.stop_event = threading.Event()

    def _calculate_lengths(self):
        """Calculate and return the length of beats and bars in this file.

        Rationale for calculating:
        When the upper number in the time signature is NOT a multiple of 3,
        excepted 3 (binary beat), then the beat is equal to the fraction
        represented by the bottom number.
        When the upper number is a multiple of 3, excepted 3 (ternary beat),
        then the beat is equal to the fraction represented by the bottom
        number, multiplied by 3.
        """
        beat_length = float(Fraction(60, self.bpm))
        num_beats, beat_unit = self.time_signature
        beats_per_measure = Fraction(num_beats, 1 if num_beats % 3 else 3)
        return beat_length, beats_per_measure * beat_length

    def _play(self):
        for msg in self.mf.play():
            if msg.type == 'note_on':
                SYNTH.noteon(msg.channel, msg.note, msg.velocity)
            elif msg.type == 'note_off':
                SYNTH.noteoff(msg.channel, msg.note)
            elif msg.type == 'pitchwheel':
                SYNTH.pitch_bend(msg.channel, msg.pitch)
            elif msg.type == 'control_change':
                SYNTH.cc(msg.channel, msg.control, msg.value)
            elif msg.type == 'program_change':
                SYNTH.program_change(msg.channel, msg.program)
            elif msg.type == 'reset':
                SYNTH.program_reset()
            if self.stop_event.is_set():
                SYNTH.system_reset()
                break

    def play(self, *args):
        self.thread = threading.Thread(target=self._play)
        self.thread.start()

    def stop(self, *args):
        self.stop_event.set()
        self.playing = False

    def length_with_full_measure(self):
        """Return this file's length, rounded up to a full measure."""
        if float_almost_equal(self.mf.length / self.bar_length, 0.0):
            # No need to round up
            return self.mf.length
        else:
            return ((self.mf.length // self.bar_length) + 1) * self.bar_length
