from random import choice
from mingus.containers.Note import Note
from mingus.containers.NoteContainer import NoteContainer
from mingushelpers import NOTE_NAMES
from mingus.core.intervals import determine


class NodeLabel(object):
    pass


class NodeNote(NodeLabel):
    @property
    def value(self):
        return self._container[0]

    def __init__(self, note=None):
        self._container = NoteContainer(
            note or Note(choice([n for n in NOTE_NAMES if len(n) == 1]), 4)
        )

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
