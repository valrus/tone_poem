from threading import Thread
from time import sleep

from mingus.containers.Note import Note
from mingus.containers.NoteContainer import NoteContainer
from mingus.midi import fluidsynth


def play_stop_NoteContainer(noteContainer, duration):
    fluidsynth.play_NoteContainer(noteContainer)
    sleep(duration)
    fluidsynth.stop_NoteContainer(noteContainer)


def thread_NoteContainer(notes, duration, *args):
    nc = NoteContainer(notes)
    t = Thread(
        target=play_stop_NoteContainer,
        args=(nc, duration)
    )
    t.start()
    return t


WHITE_KEYS = [0, 2, 4, 5, 7, 9, 11]
BLACK_KEYS = [1, 3, 6, 8, 10]

# MIDI standard: tracks on channel 10 (channels zero-indexed in Python)
# are drum tracks.
DRUM_TRACK = 9


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


def _drumNote_from_int(i):
    n = Note().from_int(i)
    n.channel = DRUM_TRACK
    return n


class MidiPercussion(object):
    BassDrum2 = _drumNote_from_int(23)
    BassDrum1 = _drumNote_from_int(24)
    SideStick_Rimshot = _drumNote_from_int(25)
    SnareDrum1 = _drumNote_from_int(26)
    HandClap = _drumNote_from_int(27)
    SnareDrum2 = _drumNote_from_int(28)
    LowTom2 = _drumNote_from_int(29)
    ClosedHihat = _drumNote_from_int(30)
    LowTom1 = _drumNote_from_int(31)
    PedalHihat = _drumNote_from_int(32)
    MidTom2 = _drumNote_from_int(33)
    OpenHihat = _drumNote_from_int(34)
    MidTom1 = _drumNote_from_int(35)
    HighTom2 = _drumNote_from_int(36)
    CrashCymbal1 = _drumNote_from_int(37)
    HighTom1 = _drumNote_from_int(38)
    RideCymbal1 = _drumNote_from_int(39)
    ChineseCymbal = _drumNote_from_int(40)
    RideBell = _drumNote_from_int(41)
    Tambourine = _drumNote_from_int(42)
    SplashCymbal = _drumNote_from_int(43)
    Cowbell = _drumNote_from_int(44)
    CrashCymbal2 = _drumNote_from_int(45)
    VibraSlap = _drumNote_from_int(46)
    RideCymbal2 = _drumNote_from_int(47)
    HighBongo = _drumNote_from_int(48)
    LowBongo = _drumNote_from_int(49)
    MuteHighConga = _drumNote_from_int(50)
    OpenHighConga = _drumNote_from_int(51)
    LowConga = _drumNote_from_int(52)
    HighTimbale = _drumNote_from_int(53)
    LowTimbale = _drumNote_from_int(54)
    HighAgogo = _drumNote_from_int(55)
    LowAgogo = _drumNote_from_int(56)
    Cabasa = _drumNote_from_int(57)
    Maracas = _drumNote_from_int(58)
    ShortWhistle = _drumNote_from_int(59)
    LongWhistle = _drumNote_from_int(60)
    ShortGuiro = _drumNote_from_int(61)
    LongGuiro = _drumNote_from_int(62)
    Claves = _drumNote_from_int(63)
    HighWoodBlock = _drumNote_from_int(64)
    LowWoodBlock = _drumNote_from_int(65)
    MuteCuica = _drumNote_from_int(66)
    OpenCuica = _drumNote_from_int(67)
    MuteTriangle = _drumNote_from_int(68)
    OpenTriangle = _drumNote_from_int(69)
