from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import Screen

from musicplayer import MusicPlayer
from party import BeastieParty
from tools import y_iterator


class CreatureWidget(AnchorLayout):
    image_source = StringProperty(None)

    def __init__(self, atlas, **kw):
        super(CreatureWidget, self).__init__(**kw)
        self.image_source = atlas


class BattleScreen(Screen):
    def __init__(self, **kw):
        self.party = kw.pop('party')
        self.beasties = BeastieParty()
        super(BattleScreen, self).__init__(**kw)

        for pc in self.party.members:
            self.ids.player_area.add_widget(
                CreatureWidget(pc.atlas)
            )

        self.creature_widgets = []
        for b, y_loc in zip(self.beasties.members, y_iterator()):
            self.creature_widgets.append(
                CreatureWidget(b.atlas)
            )
            self.ids.beastie_area.add_widget(
                self.creature_widgets[-1]
            )

        print([cw.anchor_y for cw in self.creature_widgets])
        print([cw.pos for cw in self.creature_widgets])
        print([cw.size for cw in self.creature_widgets])

        self.music = MusicPlayer()

    def on_enter(self):
        self.music.play()

    def on_pre_leave(self):
        self.music.stop()
