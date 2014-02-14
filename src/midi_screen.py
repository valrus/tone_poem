from kivy.adapters.dictadapter import DictAdapter
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.screenmanager import Screen

from keyboard import MidiKeyboard


def midi_dict_args_converter(row_index, device_name):
    return {
        'index': row_index,
        'text': device_name,
        'size_hint_y': None,
        'height': 25
    }


class MidiScreen(Screen):
    def __init__(self, **kw):
        super(MidiScreen, self).__init__(**kw)
        root = BoxLayout(orientation='vertical',
                         size_hint=(1.0, 1.0),
                         padding=10,
                         spacing=10)
        kb = MidiKeyboard(anchor_x='center', anchor_y='center',
                          size_hint=(0.5, 0.5))

        self.add_widget(root)
        # set up the midi device list
        midi_list_layout = AnchorLayout()
        root.add_widget(midi_list_layout)
        midi_data = kb.midi_in.available_ports()
        dict_adapter = DictAdapter(sorted_keys=sorted(midi_data.keys()),
                                   data=midi_data,
                                   args_converter=midi_dict_args_converter,
                                   cls=ListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=False)
        midi_list_layout.add_widget(ListView(adapter=dict_adapter,
                                             size_hint=(0.5, 0.8)))

        # set up the keyboard layout
        keyboard_layout = AnchorLayout()
        root.add_widget(keyboard_layout)
        keyboard_layout.add_widget(kb)
        dict_adapter.bind(on_selection_change=kb.midi_port_changed)
