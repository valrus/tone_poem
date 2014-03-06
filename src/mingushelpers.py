from threading import Thread
from time import sleep

from mingus.containers.Instrument import MidiInstrument
from mingus.containers.Note import Note
from mingus.containers.NoteContainer import NoteContainer
from mingus.midi import fluidsynth

# Music theory

NOTE_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

MAJOR_SCALE_INTERVALS = set([str(i) for i in range(2, 8)])
MINOR_SCALE_INTERVALS = set(["b2", "b3", "4", "5", "b6", "b7"])
ALL_INTERVALS = MINOR_SCALE_INTERVALS | MAJOR_SCALE_INTERVALS | set(["b5"])

# Playing things

# MIDI standard: tracks on channel 10 (channels zero-indexed in Python)
# are drum tracks.
DRUM_TRACK = 9
BEASTIE_CHANNEL = 14
PLAYER_CHANNEL = 15

MIDI_INSTRS = {name: num for num, name in enumerate(MidiInstrument.names)}


# TODO: Unit testable
def notes_match(nc1, nc2):
    """Return whether two NoteContainers' notes match, modulo octaves."""
    return len(nc1) == len(nc2) and all(int(n1) % 12 == int(n2) % 12
                                        for n1, n2 in zip(nc1, nc2))


# TODO: Unit testable
def is_note_on(msg):
    return msg.type == 'note_on' and msg.velocity > 0


# TODO: Unit testable
def is_note_off(msg):
    return msg.type == 'note_off' or (msg.type == 'note_on'
                                      and msg.velocity == 0)


def play_stop_NoteContainer(noteContainer, duration):
    fluidsynth.play_NoteContainer(noteContainer)
    sleep(duration)
    fluidsynth.stop_NoteContainer(noteContainer)


def thread_NoteContainer(notes, duration, instr, *args):
    nc = NoteContainer(notes)
    if instr is not None:
        fluidsynth.set_instrument(nc[0].channel, instr)
    t = Thread(
        target=play_stop_NoteContainer,
        args=(nc, duration)
    )
    t.start()
    return t


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

# Instruments

InstrumentNames = dict((v, k) for k, v in enumerate([
    "Acoustic Grand Piano",
    "Bright Acoustic Piano",
    "Electric Grand Piano",
    "Honky-tonk Piano",
    "Electric Piano 1",
    "Electric Piano 2",
    "Harpsichord",
    "Clavi",
    "Celesta",
    "Glockenspiel",
    "Music Box",
    "Vibraphone",
    "Marimba",
    "Xylophone",
    "Tubular Bells",
    "Dulcimer",
    "Drawbar Organ",
    "Percussive Organ",
    "Rock Organ",
    "Church Organ",
    "Reed Organ",
    "Accordion",
    "Harmonica",
    "Tango Accordion",
    "Acoustic Guitar (nylon)",
    "Acoustic Guitar (steel)",
    "Electric Guitar (jazz)",
    "Electric Guitar (clean)",
    "Electric Guitar (muted)",
    "Overdriven Guitar",
    "Distortion Guitar",
    "Guitar harmonics",
    "Acoustic Bass",
    "Electric Bass (finger)",
    "Electric Bass (pick)",
    "Fretless Bass",
    "Slap Bass 1",
    "Slap Bass 2",
    "Synth Bass 1",
    "Synth Bass 2",
    "Violin",
    "Viola",
    "Cello",
    "Contrabass",
    "Tremolo Strings",
    "Pizzicato Strings",
    "Orchestral Harp",
    "Timpani",
    "String Ensemble 1",
    "String Ensemble 2",
    "SynthStrings 1",
    "SynthStrings 2",
    "Choir Aahs",
    "Voice Oohs",
    "Synth Voice",
    "Orchestra Hit",
    "Trumpet",
    "Trombone",
    "Tuba",
    "Muted Trumpet",
    "French Horn",
    "Brass Section",
    "SynthBrass 1",
    "SynthBrass 2",
    "Soprano Sax",
    "Alto Sax",
    "Tenor Sax",
    "Baritone Sax",
    "Oboe",
    "English Horn",
    "Bassoon",
    "Clarinet",
    "Piccolo",
    "Flute",
    "Recorder",
    "Pan Flute",
    "Blown Bottle",
    "Shakuhachi",
    "Whistle",
    "Ocarina",
    "Lead1 (square)",
    "Lead2 (sawtooth)",
    "Lead3 (calliope)",
    "Lead4 (chiff)",
    "Lead5 (charang)",
    "Lead6 (voice)",
    "Lead7 (fifths)",
    "Lead8 (bass + lead)",
    "Pad1 (new age)",
    "Pad2 (warm)",
    "Pad3 (polysynth)",
    "Pad4 (choir)",
    "Pad5 (bowed)",
    "Pad6 (metallic)",
    "Pad7 (halo)",
    "Pad8 (sweep)",
    "FX1 (rain)",
    "FX2 (soundtrack)",
    "FX 3 (crystal)",
    "FX 4 (atmosphere)",
    "FX 5 (brightness)",
    "FX 6 (goblins)",
    "FX 7 (echoes)",
    "FX 8 (sci-fi)",
    "Sitar",
    "Banjo",
    "Shamisen",
    "Koto",
    "Kalimba",
    "Bag pipe",
    "Fiddle",
    "Shanai",
    "Tinkle Bell",
    "Agogo",
    "Steel Drums",
    "Woodblock",
    "Taiko Drum",
    "Melodic Tom",
    "Synth Drum",
    "Reverse Cymbal",
    "Guitar Fret Noise",
    "Breath Noise",
    "Seashore",
    "Bird Tweet",
    "Telephone Ring",
    "Helicopter",
    "Applause",
    "Gunshot"
]))

# Drawing things

WHITE_KEYS = [0, 2, 4, 5, 7, 9, 11]
BLACK_KEYS = [1, 3, 6, 8, 10]
