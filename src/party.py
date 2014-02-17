from creature import PlayerCharacter, Beastie


class Party(object):
    def __init__(self):
        self.members = [
            PlayerCharacter('valrus',
                            'sprites/walrus'),
            PlayerCharacter('turtle',
                            'sprites/turtle')
        ]
