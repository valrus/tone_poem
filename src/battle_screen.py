from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import Screen

from musicplayer import MusicPlayer


class PCWidget(AnchorLayout):
    image_source = StringProperty(None)

    def __init__(self, atlas, **kw):
        super(PCWidget, self).__init__(**kw)
        self.image_source = atlas


class BattleScreen(Screen):
    def __init__(self, **kw):
        self.party = kw.pop('party')
        super(BattleScreen, self).__init__(**kw)

        for pc in self.party.members:
            self.ids.player_area.add_widget(
                PCWidget(pc.atlas)
            )

        self.music = MusicPlayer()

    def on_enter(self):
        self.music.play()

    def on_pre_leave(self):
        self.music.stop()
