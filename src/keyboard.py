from kivy.event import EventDispatcher
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, ListProperty
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget

import mido
from mingushelpers import BLACK_KEYS, WHITE_KEYS


class MidiInputDispatcher(EventDispatcher):
    def __init__(self, **kw):
        self.port = mido.open_input()
        self.watchers = set()
        self.register_event_type('on_midi')
        super(MidiInputDispatcher, self).__init__(**kw)

    def available_ports(self):
        # need to poll this
        return dict(enumerate(mido.get_input_names()))

    def dispatch_midi(self, *args):
        for watcher in self.watchers:
            watcher.dispatch('on_midi', *args)

    def open_port(self, portName):
        self.port.close()
        print(portName)
        self.port = mido.open_input(portName, callback=self.dispatch_midi)

    def on_midi(self, *args):
        pass


class BlackKey(Widget):
    pressed = BooleanProperty(False)
    index = NumericProperty(0)
    rgb = ListProperty([0.2, 0.2, 0.2])


class WhiteKey(Widget):
    pressed = BooleanProperty(False)
    index = NumericProperty(0)
    rgb = ListProperty([1.0, 1.0, 1.0])


class MidiKeyboard(AnchorLayout):
    keybox = ObjectProperty(None)
    midi_in = ObjectProperty(MidiInputDispatcher())

    def __init__(self, **kw):
        self.midi_in.watchers.add(self)
        self.register_event_type('on_midi')
        self.keys = None
        super(MidiKeyboard, self).__init__(**kw)

    def on_keybox(self, *args):
        self.keys = sorted(self.keybox.children,
                           key=lambda i: i.index)

    def midi_port_changed(self, list_adapter, *args):
        self.midi_in.open_port(list_adapter.selection[0].text)

    def on_midi(self, msg):
        if msg.type == 'note_on':
            self.keys[msg.note % 12].pressed = (msg.velocity > 0)
        elif msg.type == 'note_off':
            self.keys[msg.note % 12].pressed = False
