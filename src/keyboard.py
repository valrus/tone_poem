from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

import midimsg
import rtmidi


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


class WhiteKey(Button):
    pressed = BooleanProperty(False)


class Keyboard(Widget):
    keybox = ObjectProperty(None)
    midi_in = ObjectProperty(MidiInputDispatcher())

    def __init__(self, **kw):
        self.midi_in.watchers.add(self)
        self.register_event_type('on_midi')
        super(Keyboard, self).__init__(**kw)

    def midi_port_changed(self, list_adapter, *args):
        self.midi_in.open_port(list_adapter.selection[0].index)

    def on_keybox(self, instance, value):
        for i in range(7):
            self.keybox.add_widget(
                WhiteKey(
                    text=str(i),
                    width=20,
                    pos=[22 * i, 20]
                )
            )

    def on_midi(self, *args):
        midi_data, extra_data = args
        msg = midimsg.MidiMessage(midi_data)
        print("Got MIDI data: ", msg)
