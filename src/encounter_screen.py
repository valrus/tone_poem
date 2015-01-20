import os
from random import choice
from functools import partial
from itertools import chain

from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from mingus.core.notes import note_to_int

from creature_widget import CreatureWidget
from musicplayer import MusicPlayer
from party import BeastieParty
from tools import ROOT_DIR, y_iterator


class EncounterScreen(Screen):
    music_player = ObjectProperty(
        MusicPlayer(os.path.join(ROOT_DIR, "midi", "simplebeat.mid"))
    )
    kb = ObjectProperty(None)
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

        self.music_player.watchers.add(self)
        self.register_event_type('on_bar')

    def on_kb(self, inst, value):
        for b in self.beasties.members:
            value.watchers.add(b)

    def next_on_deck(self):
        self.on_deck = choice([
            b for b in self.beastie_widgets
            if not b.creature.current_happiness == b.creature.max_happiness
        ])

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
            attacker, self.on_deck = self.on_deck, None
            Clock.schedule_once(
                attacker.flash,
                self.beat_length * (attacker.creature.anim.beat - 1)
            )
            for index, t in enumerate(attacker.creature.attack
                                      .schedule_times()):
                Clock.schedule_once(
                    partial(attacker.creature.on_attack, index),
                    self.beat_length * (t - 1)
                )

    def on_beastie_attack(self, beastie, is_attacking):
        note_highlight = beastie.attack.hl
        if is_attacking:
            if note_highlight:
                key_index = note_to_int(note_highlight.name)
                self.kb.annotate(key_index, "rgb", [1., 0.5, 0.5])
        else:
            self.kb.clear_annotations()
            self.next_on_deck()
