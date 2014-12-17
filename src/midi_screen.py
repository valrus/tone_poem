import os

from kivy.adapters.dictadapter import DictAdapter
from kivy.properties import ObjectProperty
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.screenmanager import Screen

from keyboard import MidiKeyboard
from musicplayer import MusicPlayer
from tools import ROOT_DIR


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

    def __init__(self, **kw):
        super(MidiScreen, self).__init__(**kw)

        # set up the midi device list
        midi_data = self.ids.kb.midi_in.available_ports()
        dict_adapter = DictAdapter(sorted_keys=sorted(midi_data.keys()),
                                   data=midi_data,
                                   args_converter=midi_dict_args_converter,
                                   cls=ListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=True)
        self.ids.midi_list_layout.add_widget(ListView(adapter=dict_adapter,
                                                      size_hint=(0.5, 0.8)))

        # set up the keyboard layout
        dict_adapter.bind(on_selection_change=self.ids.kb.midi_port_changed)

    def on_enter(self):
        self.music_player.start()

    def on_pre_leave(self):
        self.music_player.stop()
