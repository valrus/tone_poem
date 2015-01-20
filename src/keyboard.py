import threading

from kivy.event import EventDispatcher
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, ListProperty
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

import mido
from mingus.containers.Note import Note
from mingus.midi import fluidsynth
from mingushelpers import is_note_on, is_note_off, PLAYER_CHANNEL
from mingushelpers import InstrumentNames


class MidiInputDispatcher(EventDispatcher):
    def __init__(self, **kw):
        self.port = None
        self.watchers = set()
        self.register_event_type('on_midi')
        super(MidiInputDispatcher, self).__init__(**kw)

    def available_ports(self):
        # need to poll this
        return dict(enumerate(mido.get_input_names()))

    def dispatch_midi(self, *args):
        for watcher in self.watchers:
            watcher.dispatch('on_midi', *args)

    def open_port(self, list_adapter, *args):
        portName = list_adapter.selection[0].text
        if not self.port or self.port.name != portName:
            if self.port:
                self.port.close()
            print(portName)
            self.port = mido.open_input(portName, callback=self.dispatch_midi)

    def on_midi(self, *args):
        pass


class KeyboardThread(threading.Thread):
    def __init__(self, note):
        threading.Thread.__init__(self)
        self.note = note
        self.event = threading.Event()

    def run(self):
        # need to use bank_select
        fluidsynth.set_instrument(PLAYER_CHANNEL,
                                  InstrumentNames["Acoustic Grand Piano"])
        fluidsynth.play_Note(self.note)
        self.event.wait()
        fluidsynth.stop_Note(self.note)


class KeyboardKey(Widget):
    pressed = BooleanProperty(False)
    index = NumericProperty(None)

    def on_index(self, obj, idx):
        self.parent.keys[idx] = self


class BlackKey(KeyboardKey):
    default_rgb = [0.2, 0.2, 0.2]
    rgb = ListProperty(default_rgb)


class WhiteKey(KeyboardKey):
    default_rgb = [1.0, 1.0, 1.0]
    rgb = ListProperty(default_rgb)


class KeyAnnotation(object):
    def __init__(self, attr, normal, special):
        self.attr = attr
        self.normal = normal
        self.special = special


class MidiKeyboard(RelativeLayout):
    midi_in = ObjectProperty(None)

    def __init__(self, **kw):
        self.register_event_type('on_midi')
        self.keys = [None] * 12
        self.events = {}
        self.annotations = {}
        self.watchers = set()
        super(MidiKeyboard, self).__init__(**kw)

    def on_midi_in(self, inst, value):
        value.watchers.add(self)

    def annotate(self, key_index, attr, value):
        self.annotations[key_index] = KeyAnnotation(
            attr, getattr(self.keys[key_index], attr), value
        )
        setattr(self.keys[key_index], attr, value)

    def clear_annotations(self):
        for key_index, annotation in self.annotations.items():
            setattr(self.keys[key_index], annotation.attr, annotation.normal)

    def on_midi(self, msg):
        if is_note_on(msg):
            self.keys[msg.note % 12].pressed = True
            note = Note().from_int(msg.note)
            note.channel, note.velocity = PLAYER_CHANNEL, msg.velocity
            noteThread = KeyboardThread(note)
            self.events[msg.note] = noteThread.event
            noteThread.start()
        elif is_note_off(msg):
            self.keys[msg.note % 12].pressed = False
            self.events[msg.note].set()
        for watcher in self.watchers:
            watcher.dispatch('on_midi', msg)
