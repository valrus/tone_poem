from kivy.clock import Clock
from kivy.event import EventDispatcher

import mingus.core.value as value
from mingus.containers.Bar import Bar
from mingus.containers.Track import Track

from mingushelpers import MidiPercussion
from mido_player import MidiFilePlayer


class MusicPlayer(EventDispatcher):
    def __init__(self, midiFile, **kw):
        self.tempo = 80
        self.metronome = self._set_up_metronome()
        self.watchers = set()
        self.file_player = MidiFilePlayer('midi/simplebeat.mid')
        self.beat_length = self.file_player.beat_length

        self.register_event_type('on_bar')
        # Can add a flag for repeating
        self.file_player.bind(playing=self.schedule_music)
        self.file_player.bind(bar_number=self.on_bar)
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

    def on_bar(self, inst, bar_number):
        if bar_number:
            print('bar {}'.format(bar_number))
            for watcher in self.watchers:
                watcher.dispatch('on_bar', bar_number)

    def start(self):
        self.schedule_music(None, False)

    def schedule_music(self, inst, already_playing):
        if not already_playing:
            Clock.schedule_once(self.file_player.play)

    def stop(self):
        # Unfortunately, this throws a bunch of assertions and does nothing.
        # fluidsynth.stop_everything()
        Clock.unschedule(self.play_bar)
