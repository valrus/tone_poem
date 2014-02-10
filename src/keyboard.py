from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget

import midimsg
import rtmidi
from mingushelpers import BLACK_KEYS, WHITE_KEYS


class MidiInputDispatcher(EventDispatcher):
    def __init__(self, **kw):
        self.mi = rtmidi.MidiIn()
        self.port = None
        self.watchers = set()
        self.register_event_type('on_midi')
        super(MidiInputDispatcher, self).__init__(**kw)

    def available_ports(self):
        # need to poll this
        return dict(enumerate(self.mi.get_ports()))

    def dispatch_midi(self, *args):
        for watcher in self.watchers:
            watcher.dispatch('on_midi', *args)

    def open_port(self, port):
        self.mi.cancel_callback()
        self.mi.close_port()
        self.mi.open_port(port)
        self.mi.set_callback(self.dispatch_midi)

    def on_midi(self, *args):
        pass


class WhiteKey(Widget):
    width_hint = 1.0 / 7.0
    pressed = BooleanProperty(False)


class BlackKey(Widget):
    width_hint = 1.0 / 10.0
    pressed = BooleanProperty(False)


class Keyboard(AnchorLayout):
    keybox = ObjectProperty(None)
    midi_in = ObjectProperty(MidiInputDispatcher())

    @staticmethod
    def _white_keys_left_of(x):
        """Get the number of white keys to the left of a given black one."""
        return (x + 2) // 2

    def __init__(self, **kw):
        self.midi_in.watchers.add(self)
        self.register_event_type('on_midi')
        self.keys = [None] * 12
        super(Keyboard, self).__init__(**kw)

    def midi_port_changed(self, list_adapter, *args):
        self.midi_in.open_port(list_adapter.selection[0].index)

    def on_keybox(self, instance, value):
        for index, k in enumerate(WHITE_KEYS):
            key = WhiteKey(
                pos_hint={'x': index * WhiteKey.width_hint},
                size_hint=(WhiteKey.width_hint, 1)
            )
            self.keybox.add_widget(key)
            self.keys[k] = key
        for k in BLACK_KEYS:
            key = BlackKey(
                pos_hint={
                    'x': WhiteKey.width_hint
                    * Keyboard._white_keys_left_of(k)
                    - BlackKey.width_hint / 2,
                    'top': 1
                },
                size_hint=(BlackKey.width_hint, 0.6)
            )
            self.keybox.add_widget(key)
            self.keys[k] = key

    def on_midi(self, *args):
        midi_data, extra_data = args
        msg = midimsg.MidiMessage(midi_data)
        if msg.status == midimsg.MidiStatus.noteOn:
            self.keys[msg.data1 % 12].pressed = True
        elif msg.status == midimsg.MidiStatus.noteOff:
            self.keys[msg.data1 % 12].pressed = False
