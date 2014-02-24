from functools import partial

from kivy.animation import Animation

from creature import Creature
from mingushelpers import MidiPercussion, thread_NoteContainer


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
                                    stepDuration))
        return sum(steps[1:], steps[0])


class BeastieAttack(object):
    pass


class IntervalAttack(BeastieAttack):
    pass


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
