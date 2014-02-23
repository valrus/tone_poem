class Creature(object):
    def __init__(self, name, atlasPath):
        self.name = name
        self.state = 'normal'
        self.atlas = 'atlas://{}/{}'.format(atlasPath, self.state)
        self.anim_kw = [
            {'color': [1, 0, 0, 1]},
            {'color': [1, 1, 1, 1]}
        ]


class PlayerCharacter(Creature):
    pass


class Beastie(Creature):
    pass
