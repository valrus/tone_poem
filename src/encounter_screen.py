import os
from random import choice
from functools import partial
from itertools import chain
from threading import Thread

from kivy.clock import Clock
from kivy.graphics import Color
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import Screen
from mingus.core.notes import note_to_int

from musicplayer import MusicPlayer
from party import BeastieParty
from tools import y_iterator


class CreatureWidget(AnchorLayout):
    image_source = StringProperty(None)
    creature = ObjectProperty(None)
    beat_length = NumericProperty(1.0)
    happy_label = ObjectProperty(None)

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

    def on_happiness(self, *args):
        self.happy_label.text = "".join([
            u"\u25CF" * self.creature.current_happiness,
            u"\u25CB" * (self.creature.max_happiness
                         - self.creature.current_happiness)
        ])

    def on_creature(self, *args):
        self.on_happiness()
        self.creature.bind(current_happiness=self.on_happiness)


class EncounterScreen(Screen):
    music_player = ObjectProperty(
        MusicPlayer(os.path.join("midi", "simplebeat.mid"))
    )
    beat_length = NumericProperty(1.0)

    def __init__(self, **kw):
        self.party = kw.pop('party')
        self.beasties = BeastieParty()
        self.on_deck = None
        super(EncounterScreen, self).__init__(**kw)

        self.player_widgets = []
        for pc in self.party.members:
            self.player_widgets.append(CreatureWidget(pc))
            self.ids.player_area.add_widget(self.player_widgets[-1])

        self.beastie_widgets = []
        for b, y_loc in zip(self.beasties.members, y_iterator()):
            self.beastie_widgets.append(CreatureWidget(b))
            self.ids.beastie_area.add_widget(self.beastie_widgets[-1])
            b.bind(is_attacking=self.on_beastie_attack)
            self.ids.kb.watchers.add(b)

        self.music_player.watchers.add(self)
        self.register_event_type('on_bar')

    def next_on_deck(self):
        self.on_deck = choice(self.beastie_widgets)

    def on_enter(self):
        self.beat_length = self.music_player.beat_length
        self.music_player.start()
        self.next_on_deck()

    def on_pre_leave(self):
        self.music_player.stop()

    def on_beat_length(self, *args):
        for w in chain(self.player_widgets, self.beastie_widgets):
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

    def on_beastie_attack(self, beastie, is_attacking):
        note_highlight = beastie.attack.hl
        if is_attacking:
            if note_highlight:
                key_index = note_to_int(note_highlight.name)
                self.ids.kb.annotate(key_index, "rgb", [1., 0.5, 0.5])
            self.on_deck = None
        else:
            self.ids.kb.clear_annotations()
            self.next_on_deck()
