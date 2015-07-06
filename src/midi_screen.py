import os

from kivy.app import App
from kivy.adapters.dictadapter import DictAdapter
from kivy.properties import ObjectProperty
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.screenmanager import Screen

from keyboard import MidiKeyboard
from musicplayer import MusicPlayer
from tools import ROOT_DIR

SETTINGS_FILE_NAME = 'settings.json'


def midi_dict_args_converter(row_index, device_name):
    return {
        'index': row_index,
        'text': device_name,
        'size_hint_y': None,
        'height': 25
    }


class MidiScreen(Screen):
    music_player = ObjectProperty(
        MusicPlayer(os.path.join(ROOT_DIR, "midi", "brady.mid"))
    )
    kb = ObjectProperty(None)

    def __init__(self, **kw):
        self.settings_dir = kw['settings_dir']
        super(MidiScreen, self).__init__(**kw)

    def on_kb(self, inst, value):
        # set up the midi device list
        midi_data = value.midi_in.available_ports()
        dict_adapter = DictAdapter(sorted_keys=sorted(midi_data.keys()),
                                   data=midi_data,
                                   args_converter=midi_dict_args_converter,
                                   cls=ListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=True)
        self.ids.midi_list_layout.add_widget(ListView(adapter=dict_adapter,
                                                      size_hint=(0.5, 0.8)))

        dict_adapter.bind(on_selection_change=value.midi_in.open_port_from_list)

    def on_enter(self):
        self.music_player.start()

    def on_pre_leave(self):
        self.music_player.stop()

    def save(self):
        pass

