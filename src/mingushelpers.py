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


MidiPercussion = enum(
    BassDrum2=23,
    BassDrum1=24,
    SideStick_Rimshot=25,
    SnareDrum1=26,
    HandClap=27,
    SnareDrum2=28,
    LowTom2=29,
    ClosedHihat=30,
    LowTom1=31,
    PedalHihat=32,
    MidTom2=33,
    OpenHihat=34,
    MidTom1=35,
    HighTom2=36,
    CrashCymbal1=37,
    HighTom1=38,
    RideCymbal1=39,
    ChineseCymbal=40,
    RideBell=41,
    Tambourine=42,
    SplashCymbal=43,
    Cowbell=44,
    CrashCymbal2=45,
    VibraSlap=46,
    RideCymbal2=47,
    HighBongo=48,
    LowBongo=49,
    MuteHighConga=50,
    OpenHighConga=51,
    LowConga=52,
    HighTimbale=53,
    LowTimbale=54,
    HighAgogo=55,
    LowAgogo=56,
    Cabasa=57,
    Maracas=58,
    ShortWhistle=59,
    LongWhistle=60,
    ShortGuiro=61,
    LongGuiro=62,
    Claves=63,
    HighWoodBlock=64,
    LowWoodBlock=65,
    MuteCuica=66,
    OpenCuica=67,
    MuteTriangle=68,
    OpenTriangle=69
)
