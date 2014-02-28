import threading

from kivy.event import EventDispatcher
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty, ListProperty
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget

import mido
from mingus.containers.Note import Note
from mingus.midi import fluidsynth
from mingushelpers import BLACK_KEYS, WHITE_KEYS, PLAYER_CHANNEL


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


class KeyboardThread(threading.Thread):
    def __init__(self, note):
        threading.Thread.__init__(self)
        self.note = note
        self.event = threading.Event()

    def run(self):
        fluidsynth.play_Note(self.note)
        self.event.wait()
        fluidsynth.stop_Note(self.note)


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
        self.events = {}
        super(MidiKeyboard, self).__init__(**kw)

    def midi_port_changed(self, list_adapter, *args):
        self.midi_in.open_port(list_adapter.selection[0].text)

    def on_keybox(self, *args):
        print(self.ids)

    def on_midi(self, msg):
        if msg.type == 'note_on':
            self.keys[msg.note % 12].pressed = (msg.velocity > 0)
            note = Note().from_int(msg.note - 20)
            note.channel, note.velocity = PLAYER_CHANNEL, msg.velocity
            noteThread = KeyboardThread(note)
            self.events[msg.note] = noteThread.event
            noteThread.start()
        elif msg.type == 'note_off':
            self.keys[msg.note % 12].pressed = False
            self.events[msg.note].set()
