import kivy
kivy.require('1.1.2')

from kivy.config import Config
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from midi_screen import MidiScreen
from encounter_screen import EncounterScreen

from mingus.midi import fluidsynth
from party import PlayerParty


class TonePoemGame(ScreenManager):
    def __init__(self, screen_dict, **kw):
        super(TonePoemGame, self).__init__(**kw)
        self.screen_dict = screen_dict
        self.curr_screen = 'midi'
        self._kb = Window.request_keyboard(
            self._keyboard_closed, self, 'text'
        )
        if self._kb.widget:
            pass
        self._kb.bind(on_key_down=self._on_kb_down)
        self.switch_to(self.screen_dict[self.curr_screen])

    def _keyboard_closed(self):
        self._kb.unbind(on_key_down=self._on_kb_down)
        self._kb = None

    def _on_kb_down(self, kb, keycode, text, modifiers):
        if keycode[1] == 'left' and self.curr_screen == 'encounter':
            self.curr_screen = 'midi'
            self.switch_to(self.screen_dict['midi'], direction='right')
        elif keycode[1] == 'right' and self.curr_screen == 'midi':
            self.curr_screen = 'encounter'
            self.switch_to(self.screen_dict['encounter'], direction='left')
        else:
            return False


class TonePoemApp(App):
    def build(self):
        fluidsynth.init('sounds/FluidR3_GM.sf2')

        party = PlayerParty()
        sm = TonePoemGame({
            'midi': MidiScreen(name='midi'),
            'encounter': EncounterScreen(name='encounter', party=party)
        })
        return sm


if __name__ == '__main__':
    TonePoemApp().run()
