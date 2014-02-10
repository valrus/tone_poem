from kivy.app import App
from kivy.adapters.dictadapter import DictAdapter
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout

from keyboard import Keyboard


def midi_dict_args_converter(row_index, device_name):
    return {
        'index': row_index,
        'text': device_name,
        'height': 25
    }


# Make a menu to get the right MIDI device
class TonePoemApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical',
                         size_hint=(1.0, 1.0),
                         padding=10,
                         spacing=10)
        kb = Keyboard(anchor_x='center', anchor_y='center',
                      size_hint=(None, None),
                      size=(200, 100))

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
        print(kb.size)
        print(kb.to_window(*kb.pos))
        print(kb.children)
        return root


if __name__ == '__main__':
    TonePoemApp().run()
