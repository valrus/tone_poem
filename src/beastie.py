from functools import partial
from random import choice

from kivy.animation import Animation

import mingus.core.notes as notes
from mingus.containers.Note import Note

from creature import Creature
from mingushelpers import MidiPercussion, thread_NoteContainer
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

    def play(self, index):
        if index == 0:
            start_note_name = choice(self.start_notes)
            start_note = Note(start_note_name)
            start_note.channel = BEASTIE_CHANNEL
            end_note = Note(choice(self.intervals)(start_note_name))
            end_note.channel = BEASTIE_CHANNEL
            self.notes = [start_note, end_note]
        duration = self.note_placement[index][1]
        thread_NoteContainer(self.notes[index], duration, self.instr)


class Beastie(Creature):
    def __init__(self, name, atlasPath):
        super(Beastie, self).__init__(name, atlasPath)
        self.anim = BeastieAnimation(
            beat=2, duration=0.5,
            kws=({'color': [1, 0, 0, 1]}, {'color': [1, 1, 1, 1]}),
            sounds=(
                MidiPercussion.HighWoodBlock,
                MidiPercussion.LowWoodBlock
            )
        )
        self.attack = IntervalAttack(
            start_notes=NOTE_NAMES,
            note_placement=[(4, 0.5), (4.5, 0.5)],
            instr=MIDI_INSTRS['Drawbar Organ']
        )

    def on_attack(self, index, *args):
        self.attack.play(index)
