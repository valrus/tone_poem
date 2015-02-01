from random import choice
from mingus.containers.Note import Note
from mingushelpers import NOTE_NAMES
from mingus.core.intervals import determine


class NodeLabel(object):
    pass


class NodeNote(NodeLabel):
    def __init__(self, note=None):
        if note:
            self.value = note
        else:
            self.value = Note(choice([n for n in NOTE_NAMES if len(n) == 1]))

    def delta(self, other):
        return EdgeInterval(
            determine(self.value.name, other.value.name, shorthand=True)
        )

    def __str__(self):
        return self.value.name


class EdgeLabel(object):
    pass


class EdgeInterval(EdgeLabel):
    def __init__(self, interval):
        self.value = interval

    def __str__(self):
        return self.value.replace('b', '\N{MUSIC FLAT SIGN}')
