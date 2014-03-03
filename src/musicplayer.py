from fractions import Fraction
from threading import Thread

from kivy.clock import Clock
from kivy.event import EventDispatcher

import mingus.core.value as value
from mingus.midi import fluidsynth
from mingus.containers.Bar import Bar
from mingus.containers.Track import Track

from mingushelpers import MidiPercussion
from mido_player import MidiFilePlayer


class MusicPlayer(EventDispatcher):
    def __init__(self, midiFile, **kw):
        self.metronome = self._set_up_metronome()
        self.watchers = set()
        self.file_player = MidiFilePlayer('midi/simplebeat.mid')
        self.beat_length = self.file_player.beat_length
        self.music_length = self.file_player.length_with_full_measure()

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

    def on_bar(self, *args):
        pass

    def start(self):
        print(self.music_length)
        Clock.schedule_once(self.file_player.play)
        Clock.schedule_interval(self.file_player.play, self.music_length)
        Clock.schedule_once(self.play_bar)
        Clock.schedule_interval(self.play_bar, self.file_player.bar_length)

    def stop(self):
        self.file_player.stop()
        Clock.unschedule(self.play_bar)
        Clock.unschedule(self.file_player.play)
