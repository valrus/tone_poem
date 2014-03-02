from functools import partial
from random import choice

from kivy.animation import Animation
from kivy.properties import BooleanProperty

import mingus.core.notes as notes
from mingus.containers.Note import Note
from mingus.containers.NoteContainer import NoteContainer

from creature import Creature
from mingushelpers import MidiPercussion, thread_NoteContainer
from mingushelpers import is_note_on, is_note_off, notes_match
from mingushelpers import ALL_INTERVALS, MIDI_INSTRS, BEASTIE_CHANNEL
from mingushelpers import NOTE_NAMES


class BeastieAnimation(object):
    def __init__(self, duration=1.0, repeat=2, kws=None, sounds=None, beat=1):
        self.duration = duration
        self.kws = kws
        self.sounds = sounds
        self.repeat = repeat
        self.beat = beat

    def build(self, beat_length):
        if not self.kws:
            raise ValueError("No attributes provided to animate!")
        elif self.sounds and len(self.kws) != len(self.sounds):
            raise ValueError("Need one set of callback args per animation.")
        stepDuration = (
            (beat_length * self.duration) / (self.repeat * len(self.kws))
        )
        steps = [Animation(duration=stepDuration, **kw)
                 for kw in self.kws * self.repeat]
        for i, s in enumerate(steps):
            s.bind(on_start=partial(thread_NoteContainer,
                                    self.sounds[i % len(self.kws)],
                                    stepDuration,
                                    None))
        return sum(steps[1:], steps[0])


# TODO: Unit testable
class NoteCollector(object):

    """Gather notes into a NoteContainer as MIDI msgs come in."""

    def __init__(self):
        self.pending_notes = {}
        self.received_notes = NoteContainer()

    def hear(self, msg):
        if is_note_on(msg):
            self.pending_notes[msg.note] = Note().from_int(msg.note)
        elif is_note_off(msg) and msg.note in self.pending_notes:
            self.received_notes.add_notes(self.pending_notes.pop(msg.note))

    def heard_count(self):
        return len(self.received_notes) if self.received_notes else 0

    def retrieve(self):
        returnVal = self.received_notes
        self.received_notes = None
        return returnVal


class BeastieAttack(object):
    def schedule_times(self):
        return [note_place[0] for note_place in self.note_placement]


class IntervalAttack(BeastieAttack):
    def __init__(self, **kw):
        self.start_notes = kw.get("start_notes")
        self.intervals = kw.get("intervals", list(ALL_INTERVALS))
        self.note_placement = kw["note_placement"]
        self.instr = kw["instr"]
        self.notes = None
        self.hl = None
        self.ear = NoteCollector()

    def play(self, index):
        if index == 0:
            start_note = choice(self.start_notes)
            start_note.channel = BEASTIE_CHANNEL
            end_note = Note(start_note)
            end_note.transpose(choice(self.intervals))
            self.notes = [start_note, end_note]
            self.hl = start_note
        duration = self.note_placement[index][1]
        thread_NoteContainer(self.notes[index], duration, self.instr)

    def handleNote(self, msg):
        self.ear.hear(msg)
        if self.ear.heard_count() >= 2:
            heard = self.ear.retrieve()
            return notes_match(heard, NoteContainer(self.notes))
        return None


class Beastie(Creature):
    is_attacking = BooleanProperty(False)

    def __init__(self, party, name):
        super(Beastie, self).__init__(name, self.__class__.sprite)
        self.register_event_type('on_midi')
        self.party = party

    def on_attack(self, index, *args):
        self.attack.play(index)
        self.is_attacking = True

    def on_midi(self, msg):
        if self.is_attacking:
            result = self.attack.handleNote(msg)
            if result is not None:
                self.is_attacking = False
                self.attack.finish()
                print(result)


class LandEel(Beastie):
    sprite = 'sprites/landeel'

    def __init__(self, party, name):
        super(LandEel, self).__init__(party, name)
        self.anim = BeastieAnimation(
            beat=2, duration=1,
            kws=({'color': [1, 0, 0, 1]}, {'color': [1, 1, 1, 1]}),
            sounds=(
                MidiPercussion.HighWoodBlock,
                MidiPercussion.LowWoodBlock
            )
        )
        self.attack = IntervalAttack(
            start_notes=[Note(n, 4) for n in NOTE_NAMES],
            note_placement=[(4, 0.5), (4.5, 0.5)],
            instr=MIDI_INSTRS['Drawbar Organ'],
        )


class PinkElephant(Beastie):
    sprite = 'sprites/pinkelephant'

    def __init__(self, party, name):
        super(PinkElephant, self).__init__(party, name)
        self.anim = BeastieAnimation(
            beat=1, duration=2, repeat=1,
            kws=({'color': [1, 0, 0, 1]}, {'color': [1, 1, 1, 1]}),
            sounds=(
                MidiPercussion.LowTom1,
                None
            )
        )
        self.attack = IntervalAttack(
            start_notes=[Note(n, 2) for n in NOTE_NAMES],
            note_placement=[(3, 1), (4, 1)],
            instr=MIDI_INSTRS['Tuba']
        )
