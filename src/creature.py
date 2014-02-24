from functools import partial

from kivy.animation import Animation

from mingushelpers import MidiPercussion, thread_NoteContainer


class CreatureAnimation(object):
    def __init__(self, duration=1.0, repeat=2, kws=None, sounds=None):
        self.duration = duration
        self.kws = kws
        self.sounds = sounds
        self.repeat = repeat

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


class Creature(object):
    def __init__(self, name, atlasPath):
        self.name = name
        self.state = 'normal'
        self.atlas = 'atlas://{}/{}'.format(atlasPath, self.state)
        # TODO: animation data should probably be a class or namedtuple
        self.anim = CreatureAnimation(
            duration=0.5,
            kws=({'color': [1, 0, 0, 1]}, {'color': [1, 1, 1, 1]}),
            sounds=(
                MidiPercussion.HighWoodBlock,
                MidiPercussion.LowWoodBlock
            )
        )


class PlayerCharacter(Creature):
    pass


class Beastie(Creature):
    pass
