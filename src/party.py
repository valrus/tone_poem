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
    def __init__(self):
        self.members = [
            Beastie('Timothy',
                    'sprites/landeel'),
            Beastie('Albert',
                    'sprites/pinkelephant'),
            Beastie('Nathan',
                    'sprites/landeel'),
        ]
