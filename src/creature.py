from kivy.event import EventDispatcher


class Creature(EventDispatcher):
    def __init__(self, name, atlasPath):
        self.name = name
        self.state = 'normal'
        self.atlas = 'atlas://{}/{}'.format(atlasPath, self.state)


class PlayerCharacter(Creature):
    pass
