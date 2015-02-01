from random import choice
from mingus.containers.Note import Note
from mingus.containers.NoteContainer import NoteContainer
from mingushelpers import NOTE_NAMES
from mingus.core.intervals import determine


class NodeLabel(object):
    pass


class NodeNote(NodeLabel):
    def __init__(self, note=None):
        self.value = NoteContainer(
            note or Note(choice([n for n in NOTE_NAMES if len(n) == 1]))
        )

    def delta(self, other):
        return EdgeInterval(
            determine(self.value[0].name, other.value[0].name, shorthand=True)
        )

    def match(self, other):
        pass

    def __str__(self):
        return self.value[0].name


class EdgeLabel(object):
    pass


class EdgeInterval(EdgeLabel):
    def __init__(self, interval):
        self.value = interval

    def __str__(self):
        return self.value.replace('b', '\N{MUSIC FLAT SIGN}')
