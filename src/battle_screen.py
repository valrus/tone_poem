from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen

from keyboard import MidiKeyboard


class BattleScreen(Screen):
    def __init__(self, **kw):
        super(BattleScreen, self).__init__(**kw)
        root = BoxLayout(orientation='vertical',
                         size_hint=(1.0, 1.0),
                         padding=10,
                         spacing=10)
        battleArea = RelativeLayout(size_hint=(1.0, 0.6))
        root.add_widget(battleArea)
        keyboardArea = AnchorLayout(size_hint=(1.0, 0.1))
        kb = MidiKeyboard(anchor_x='left', anchor_y='center',
                          size_hint=(1.0, 1.0))
        keyboardArea.add_widget(kb)
        root.add_widget(keyboardArea)
        infoArea = BoxLayout(size_hint=(1.0, 0.3))
        root.add_widget(infoArea)
        self.add_widget(root)
