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
    BassDrum2=35,
    BassDrum1=36,
    SideStick_Rimshot=37,
    SnareDrum1=38,
    HandClap=39,
    SnareDrum2=40,
    LowTom2=41,
    ClosedHihat=42,
    LowTom1=43,
    PedalHihat=44,
    MidTom2=45,
    OpenHihat=46,
    MidTom1=47,
    HighTom2=48,
    CrashCymbal1=49,
    HighTom1=50,
    RideCymbal1=51,
    ChineseCymbal=52,
    RideBell=53,
    Tambourine=54,
    SplashCymbal=55,
    Cowbell=56,
    CrashCymbal2=57,
    VibraSlap=58,
    RideCymbal2=59,
    HighBongo=60,
    LowBongo=61,
    MuteHighConga=62,
    OpenHighConga=63,
    LowConga=64,
    HighTimbale=65,
    LowTimbale=66,
    HighAgogo=67,
    LowAgogo=68,
    Cabasa=69,
    Maracas=70,
    ShortWhistle=71,
    LongWhistle=72,
    ShortGuiro=73,
    LongGuiro=74,
    Claves=75,
    HighWoodBlock=76,
    LowWoodBlock=77,
    MuteCuica=78,
    OpenCuica=79,
    MuteTriangle=80,
    OpenTriangle=81
)
