from kivy.event import EventDispatcher
from kivy.properties import NumericProperty


class Creature(EventDispatcher):
    current_happiness = NumericProperty(None)

    def get_happy(self):
        if self.current_happiness < self.max_happiness:
            self.current_happiness += 1

    def get_mad(self):
        if self.current_happiness > 0:
            self.current_happiness -= 1

    def __init__(self, name, atlas_path):
        self.name = name
        self.current_happiness = 0
        self.max_happiness = self.__class__.base_happiness
        self.state = "normal"
        self.atlas = "atlas://{}/{}".format(atlas_path, self.state)


class PlayerCharacter(Creature):
    base_happiness = 4

    def __init__(self, name, atlas_path):
        super(PlayerCharacter, self).__init__(name, atlas_path)
        self.current_happiness = self.max_happiness
