import os
from threading import Thread

from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import Screen

from musicplayer import MusicPlayer
from party import BeastieParty
from tools import y_iterator


class CreatureWidget(AnchorLayout):
    image_source = StringProperty(None)
    creature = ObjectProperty(None)

    def __init__(self, creature, **kw):
        super(CreatureWidget, self).__init__(**kw)
        self.creature = creature
        self.image_source = self.creature.atlas

    def _make_animation(self, flashDuration):
        otherkw = {
            'duration': flashDuration
        }
        anim = sum(
            (
                Animation(**dict(kw, **otherkw))
                for kw in self.creature.anim_kw[1:]
            ),
            Animation(**dict(self.creature.anim_kw[0], **otherkw))
        )
        return anim

    def flash(self, length):
        first = self._make_animation(length / 4.)
        second = self._make_animation(length / 4.)
        t = Thread(
            target=(first + second).start,
            args=(self.ids.sprite, )
        )
        t.start()


class BattleScreen(Screen):
    music_player = ObjectProperty(MusicPlayer(os.path.join("midi",
                                                           "simplebeat.mid")))

    def __init__(self, **kw):
        self.party = kw.pop('party')
        self.beasties = BeastieParty()
        super(BattleScreen, self).__init__(**kw)

        for pc in self.party.members:
            self.ids.player_area.add_widget(
                CreatureWidget(pc)
            )

        self.creature_widgets = []
        for b, y_loc in zip(self.beasties.members, y_iterator()):
            self.creature_widgets.append(
                CreatureWidget(b)
            )
            self.ids.beastie_area.add_widget(
                self.creature_widgets[-1]
            )

        print([cw.anchor_y for cw in self.creature_widgets])
        print([cw.pos for cw in self.creature_widgets])
        print([cw.size for cw in self.creature_widgets])

        self.music_player.watchers.add(self)
        self.register_event_type('on_bar')

    def on_enter(self):
        self.music_player.play()
        self.creature_widgets[0].flash(self.music_player.beat_length)

    def on_pre_leave(self):
        self.music_player.stop()

    def on_bar(self, *args):
        print("bar")
