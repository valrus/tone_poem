from random import choice
from mingus.containers.Note import Note
from mingus.containers.NoteContainer import NoteContainer
from mingushelpers import NOTE_NAMES
from mingus.core.intervals import determine


class NodeLabel(object):
    pass


class NodeNote(NodeLabel):
    POSSIBLE_VALUES = [Note(n, 4) for n in NOTE_NAMES]

    @property
    def value(self):
        return self._container[0]

    @value.setter
    def value(self, note_choices):
        self._container = NoteContainer(choice(note_choices))

    @property
    def name(self):
        return self.value.to_shorthand()

    def __init__(self, note=None):
        self._container = None
        self.value = [note] if note else [Note(n, 4) for n in NOTE_NAMES if len(n) == 1]

    def delta(self, other):
        return EdgeInterval(
            determine(self.value.name, other.value.name, shorthand=True),
            is_up=self.value <= other.value
        )

    def container(self):
        return self._container

    def match(self, other):
        pass

    def __str__(self):
        return self.value.name


class EdgeLabel(object):
    pass


class EdgeInterval(EdgeLabel):
    def __init__(self, interval, is_up=True):
        self.is_up = is_up
        self.value = interval

    def __str__(self):
        return "".join([
            '\N{UPWARDS ARROW}' if self.is_up else '\N{DOWNWARDS ARROW}',
            self.value.replace('b', '\N{MUSIC FLAT SIGN}')
        ])
