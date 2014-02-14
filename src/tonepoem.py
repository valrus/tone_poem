from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from midi_screen import MidiScreen
from battle_screen import BattleScreen


class TonePoemGame(ScreenManager):
    def __init__(self, **kw):
        super(TonePoemGame, self).__init__(**kw)
        self._kb = Window.request_keyboard(
            self._keyboard_closed, self, 'text'
        )
        if self._kb.widget:
            pass
        self._kb.bind(on_key_down=self._on_kb_down)

    def _keyboard_closed(self):
        self._kb.unbind(on_key_down=self._on_kb_down)
        self._kb = None

    def _on_kb_down(self, kb, keycode, text, modifiers):
        print('The key', keycode, 'has been pressed.')
        if keycode[1] == 'left':
            self.transition = SlideTransition(direction='right')
            self.current = self.previous()
        elif keycode[1] == 'right':
            self.transition = SlideTransition(direction='left')
            self.current = self.next()
        else:
            return False


class TonePoemApp(App):
    def build(self):
        sm = TonePoemGame()
        sm.add_widget(MidiScreen(name='midi'))
        sm.add_widget(BattleScreen(name='battle'))
        return sm


if __name__ == '__main__':
    TonePoemApp().run()
