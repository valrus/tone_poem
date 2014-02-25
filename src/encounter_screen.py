import os
from functools import partial
from itertools import chain
from threading import Thread

from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import Screen

from musicplayer import MusicPlayer
from party import BeastieParty
from tools import y_iterator


class CreatureWidget(AnchorLayout):
    image_source = StringProperty(None)
    creature = ObjectProperty(None)
    beat_length = NumericProperty(1.0)

    def __init__(self, creature, **kw):
        super(CreatureWidget, self).__init__(**kw)
        self.creature = creature
        self.image_source = self.creature.atlas
        self.thread = None

    def flash(self, *args):
        length = self.beat_length
        self.thread = Thread(
            target=self.creature.anim.build(length).start,
            args=(self.ids.sprite, )
        )
        self.thread.start()


class EncounterScreen(Screen):
    music_player = ObjectProperty(MusicPlayer(os.path.join("midi",
                                                           "simplebeat.mid")))
    beat_length = NumericProperty(1.0)

    def __init__(self, **kw):
        self.party = kw.pop('party')
        self.beasties = BeastieParty()
        self.on_deck = None
        super(EncounterScreen, self).__init__(**kw)

        self.player_widgets = []
        for pc in self.party.members:
            self.player_widgets.append(
                CreatureWidget(pc)
            )
            self.ids.player_area.add_widget(
                self.player_widgets[-1]
            )

        self.creature_widgets = []
        for b, y_loc in zip(self.beasties.members, y_iterator()):
            self.creature_widgets.append(
                CreatureWidget(b)
            )
            self.ids.beastie_area.add_widget(
                self.creature_widgets[-1]
            )

        self.music_player.watchers.add(self)
        self.register_event_type('on_bar')

    def on_enter(self):
        self.beat_length = self.music_player.beat_length
        self.music_player.play()
        # This line is for testing!
        self.on_deck = self.creature_widgets[0]

    def on_pre_leave(self):
        self.music_player.stop()

    def on_beat_length(self, *args):
        for w in chain(self.player_widgets, self.creature_widgets):
            w.beat_length = self.beat_length

    def on_bar(self, *args):
        if self.on_deck:
            Clock.schedule_once(
                self.on_deck.flash,
                self.beat_length * (self.on_deck.creature.anim.beat - 1)
            )
            for index, t in enumerate(self.on_deck.creature.attack.
                                      schedule_times()):
                Clock.schedule_once(
                    partial(self.on_deck.creature.on_attack, index),
                    self.beat_length * (t - 1)
                )
