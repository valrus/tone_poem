from fractions import Fraction
from threading import Thread

from kivy.clock import Clock
from kivy.event import EventDispatcher

import mingus.core.value as value
from mingus.midi import fluidsynth
from mingus.containers.Bar import Bar
from mingus.containers.Track import Track

from mingushelpers import MidiPercussion


class MusicPlayer(EventDispatcher):
    def __init__(self, midiFile, **kw):
        self.metronome = self._set_up_metronome()
        self.tempo = 120
        self.watchers = set()

        # When the upper number in the time signature is NOT a multiple of 3,
        # excepted 3 (binary beat), then the beat is equal to the fraction
        # represented by the bottom number.
        # When the upper number is a multiple of 3, excepted 3 (ternary beat),
        # then the beat is equal to the fraction represented by the bottom
        # number, multiplied by 3.
        num_beats, beat_unit = self.metronome[0].meter
        beats_per_measure = Fraction(num_beats, 1 if num_beats % 3 else 3)
        self.beat_length = Fraction(60, self.tempo)
        self.bar_interval = float(beats_per_measure * self.beat_length)

        self.register_event_type('on_bar')
        super(MusicPlayer, self).__init__(**kw)

    def _set_up_metronome(self):
        metronome = Track()
        bar = Bar('C', (4, 4))
        metronome.add_bar(bar)
        kick = MidiPercussion.BassDrum1
        kick.velocity = 120
        for i in range(4):
            bar.place_notes(kick, value.quarter)
        return metronome

    def play_bar(self, *args):
        for watcher in self.watchers:
            watcher.dispatch('on_bar', *args)
        t = Thread(
            target=fluidsynth.play_Track,
            args=(self.metronome, )
        )
        t.start()

    def on_bar(self, *args):
        pass

    def play(self):
        print(self.bar_interval)
        Clock.schedule_once(self.play_bar)
        Clock.schedule_interval(self.play_bar, self.bar_interval)

    def stop(self):
        # Unfortunately, this throws a bunch of assertions and does nothing.
        # fluidsynth.stop_everything()
        Clock.unschedule(self.play_bar)
