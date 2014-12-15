from __future__ import unicode_literals

from collections import OrderedDict

from tools import WINDOW_SIZE

import kivy
kivy.require('1.1.2')

from kivy.config import Config
Config.set('graphics', 'width', unicode(WINDOW_SIZE.w))
Config.set('graphics', 'height', unicode(WINDOW_SIZE.h))

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

from midi_screen import MidiScreen
from encounter_screen import EncounterScreen
from area_screen import AreaScreen

from mingus.midi import fluidsynth
from party import PlayerParty

PROFILE = True
if PROFILE:
    import cProfile


class TonePoemGame(ScreenManager):
    def __init__(self, screen_dict, **kw):
        super(TonePoemGame, self).__init__(**kw)
        self.screen_dict = screen_dict
        self.screen_order = list(screen_dict.keys())
        self.screen_index = 1
        self._kb = Window.request_keyboard(
            self._keyboard_closed, self, 'text'
        )
        if self._kb.widget:
            pass
        self._kb.bind(on_key_down=self._on_kb_down)
        self.switch_to(
            self.screen_dict[self.screen_order[self.screen_index]]
        )

    def _keyboard_closed(self):
        self._kb.unbind(on_key_down=self._on_kb_down)
        self._kb = None

    def _switch_screens(self, index, direction):
        self.switch_to(self.screen_dict[self.screen_order[index]],
                       direction=direction)

    def _on_kb_down(self, kb, keycode, text, modifiers):
        if keycode[1] == 'left' and self.screen_index != 0:
            self.screen_index -= 1
            self._switch_screens(self.screen_index, direction="right")
        elif keycode[1] == 'right' and self.screen_index != len(self.screen_dict):
            self.screen_index += 1
            self._switch_screens(self.screen_index, direction="left")
        else:
            return False


class TonePoemApp(App):
    def on_start(self):
        self.profile = cProfile.Profile()
        self.profile.enable()

    def on_stop(self):
        self.profile.disable()
        self.profile.dump_stats('tone_poem.profile')

    def build(self):
        fluidsynth.init('sounds/FluidR3_GM.sf2')

        party = PlayerParty()
        sm = TonePoemGame(OrderedDict([
            ('midi', MidiScreen(name='midi')),
            ('area', AreaScreen(name='area')),
            ('encounter', EncounterScreen(name='encounter', party=party))
        ]))
        return sm


if __name__ == '__main__':
    TonePoemApp().run()
    sys.exit(1)  # so that emacs will keep the compilation window open
