from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from midi_screen import MidiScreen


class TonePoemApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MidiScreen(name='midi'))
        return sm


if __name__ == '__main__':
    TonePoemApp().run()
