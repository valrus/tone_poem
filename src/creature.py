from mingushelpers import MidiPercussion


class Creature(object):
    def __init__(self, name, atlasPath):
        self.name = name
        self.state = 'normal'
        self.atlas = 'atlas://{}/{}'.format(atlasPath, self.state)
        # TODO: animation data should probably be a class or namedtuple
        self.anim_kw = (
            {'color': [1, 0, 0, 1]},
            {'color': [1, 1, 1, 1]}
        )
        self.sounds = (
            MidiPercussion.HighWoodBlock,
            MidiPercussion.LowWoodBlock
        )


class PlayerCharacter(Creature):
    pass


class Beastie(Creature):
    pass
