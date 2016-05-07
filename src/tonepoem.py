from __future__ import unicode_literals

import json
import os
import random
import sys
from collections import OrderedDict

from tools import WINDOW_SIZE, ROOT_DIR, CONFIG_INI

import kivy
kivy.require('1.1.2')

from kivy.config import Config
Config.set('graphics', 'width', WINDOW_SIZE.w)
Config.set('graphics', 'height', WINDOW_SIZE.h)
Config.set('kivy', 'log_level', 'debug')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.settings import Settings, SettingItem, SettingsPanel, SettingTitle
from kivy.properties import ObjectProperty

from keyboard import MidiInputDispatcher
from encounter_screen import EncounterScreen
from area_screen import AreaScreen

from mingus.midi import fluidsynth
from party import PlayerParty

SETTINGS_JSON = os.path.join(ROOT_DIR, 'settings.json')
DEBUG = True
if DEBUG:
    import cProfile


class TonePoemGame(ScreenManager):
    def __init__(self, screen_dict, **kw):
        super(TonePoemGame, self).__init__(**kw)
        self.app = kw['app']
        self.screen_dict = screen_dict
        self.screen_order = list(screen_dict.keys())
        self.screen_index = 0
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
            self._switch_screens(self.screen_index, direction='right')
        elif keycode[1] == 'right' and self.screen_index < len(self.screen_dict):
            self.screen_index += 1
            self._switch_screens(self.screen_index, direction='left')
        elif keycode[1] == 's':
            self.app.open_settings()
        else:
            print(keycode, self.screen_index)
            return False


class TonePoemApp(App):
    midi_in = ObjectProperty(None)
    setting_panel = ObjectProperty(None)
    use_kivy_settings = DEBUG

    def __init__(self, *args, **kw):
        self.profile = None
        self.config = None
        super(TonePoemApp, self).__init__(*args, **kw)

    def on_start(self):
        if DEBUG:
            self.profile = cProfile.Profile()
            self.profile.enable()

    def on_stop(self):
        if DEBUG:
            self.profile.disable()
            self.profile.dump_stats('tone_poem.profile')

    def get_application_config(self):
        return super(TonePoemApp, self).get_application_config(
            os.path.join(self.user_data_dir, CONFIG_INI))

    def build_config(self, config):
        config.setdefaults('MIDI', {
            'Input device': '',
        })
        config.add_callback(lambda section, key, value: self.midi_in.open_port(value),
                            section='MIDI', key='Input Device')

    def build_settings(self, settings):
        with open(os.path.join(ROOT_DIR, SETTINGS_JSON), 'r') as json_file:
            setting_base = json.load(json_file)

        # Dynamically fill in available MIDI ports.
        for setting in setting_base:
            if setting['title'] == 'Input Device':
                setting['options'] = list(self.midi_in.available_ports().values())

        settings.add_json_panel('Tone Poem', self.config, data=json.dumps(setting_base))

    def build(self):
        fluidsynth.init(os.path.join(ROOT_DIR, 'sounds', 'FluidR3_GM.sf2'))
        self.midi_in = MidiInputDispatcher()
        midi_device = self.config.get('MIDI', 'Input device')
        if midi_device:
            self.midi_in.open_port(midi_device)

        self.setting_panel = Settings()

        party = PlayerParty()
        sm = TonePoemGame(OrderedDict([
            ('area', AreaScreen(name='area')),
            ('encounter', EncounterScreen(name='encounter', party=party))
        ]), app=self)
        return sm


if __name__ == '__main__':
    if DEBUG is True:
        seed = random.randint(0, sys.maxsize)
        print('Random seed is {}'.format(seed))
        random.seed(seed)
    elif DEBUG:
        random.seed(DEBUG)
    TonePoemApp().run()
    sys.exit(1)  # so that emacs will keep the compilation window open
