from kivy.event import EventDispatcher

from beastie import *
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
            LandEel(self, 'Timothy'),
            PinkElephant(self, 'Albert'),
            LandEel(self, 'Nathan')
        ]
