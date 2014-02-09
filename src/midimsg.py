class MidiStatus(object):
    mask = 0b11110000
    noteOff = 0b1000
    noteOn = 0b1001

    @staticmethod
    def _isNoteOff(status, data2):
        return (
            status == MidiStatus.noteOff
            or (status == MidiStatus.noteOn and data2 == 0)
        )


def bits_equal(n1, n2, mask=0b11111111):
    """Return whether masked bits in two numbers are all equal.

    >>> bits_equal(0b10100000, 0b10101101, mask=0b11100000)
    True
    >>> bits_equal(0b10100000, 0b10101101, mask=0b11111000)
    False
    """
    return not ((n1 & mask) ^ (n2 & mask))


class MidiMessage(object):
    def __init__(self, msgData):
        print(msgData)
        (status, self.data1, self.data2), self.elapsed = msgData
        statusFirstNybble = status >> 4
        if MidiStatus._isNoteOff(statusFirstNybble, self.data2):
            self.status = MidiStatus.noteOff
        else:
            self.status = statusFirstNybble
