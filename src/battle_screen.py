from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen

from keyboard import MidiKeyboard
from musicplayer import MusicPlayer


class BattleScreen(Screen):
    def __init__(self, **kw):
        super(BattleScreen, self).__init__(**kw)

        self.music = MusicPlayer()

    def on_enter(self):
        self.music.play()

    def on_pre_leave(self):
        self.music.stop()
