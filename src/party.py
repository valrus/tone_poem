from beastie import Beastie
from creature import PlayerCharacter


class Party(object):
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
    def __init__(self, screen):
        self.members = [
            Beastie('Timothy',
                    'sprites/landeel',
                    screen),
            Beastie('Albert',
                    'sprites/pinkelephant',
                    screen),
            Beastie('Nathan',
                    'sprites/landeel',
                    screen),
        ]
