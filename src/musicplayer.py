from fractions import Fraction
from threading import Thread

from kivy.clock import Clock

import mingus.core.value as value
from mingus.midi import fluidsynth
from mingus.containers.Bar import Bar
from mingus.containers.Composition import Composition
from mingus.containers.Note import Note
from mingus.containers.Track import Track

from mingushelpers import MidiPercussion, DRUM_TRACK


class MusicPlayer(object):
    def __init__(self):
        self.music = Track()
        bar = Bar('C', (4, 4))
        kick = Note().from_int(MidiPercussion.BassDrum2)
        kick.velocity = 100
        for i in range(4):
            bar.place_notes(kick, value.quarter)
        self.music.add_bar(bar)

        self.tempo = 120

        # When the upper number in the time signature is NOT a multiple of 3,
        # excepted 3 (binary beat), then the beat is equal to the fraction
        # represented by the bottom number.
        # When the upper number is a multiple of 3, excepted 3 (ternary beat),
        # then the beat is equal to the fraction represented by the bottom
        # number, multiplied by 3.
        num_beats, beat_unit = self.music[0].meter
        beats_per_measure = Fraction(num_beats, 1 if num_beats % 3 else 3)
        beat_length = Fraction(60, self.tempo)
        self.bar_interval = float(beats_per_measure * beat_length)

        fluidsynth.init("sounds/FluidR3_GM.sf2")

    def play_bar(self, *args):
        print(self.music)
        t = Thread(target=fluidsynth.play_Track,
                   args=(self.music, DRUM_TRACK))
        t.start()

    def play(self):
        Clock.schedule_once(self.play_bar)
        Clock.schedule_interval(self.play_bar, self.bar_interval)

    def stop(self):
        # Unfortunately, this throws a bunch of assertions and does nothing.
        # fluidsynth.stop_everything()
        Clock.unschedule(self.play_bar)
