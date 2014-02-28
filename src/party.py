from kivy.event import EventDispatcher

from beastie import Beastie
from creature import PlayerCharacter


class Party(EventDispatcher):
    pass


class PlayerParty(Party):
    def __init__(self):
        self.members = [
            PlayerCharacter('',
                            'sprites/walrus'),
            PlayerCharacter('Sally',
                            'sprites/turtle')
        ]


class BeastieParty(Party):
    def __init__(self):
        self.members = [
            Beastie(self, 'Timothy',
                    'sprites/landeel'),
            Beastie(self, 'Albert',
                    'sprites/pinkelephant'),
            Beastie(self, 'Nathan',
                    'sprites/landeel')
        ]
