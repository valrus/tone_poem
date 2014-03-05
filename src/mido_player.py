from collections import deque
from fractions import Fraction
from functools import partial

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty

from mingus.midi import fluidsynth
from mido.midifiles import MidiFile, MetaMessage, Message

SYNTH = fluidsynth.midi.fs
DEFAULT_TEMPO = 500000


def midi_tempo_to_bpm(tempo):
    return (1000000 / tempo) * 60


def float_almost_equal(f1, f2):
    """Check that two floats are about the same.

    The precision used here is totally arbitrary but should be fine for
    lengths of midi files.
    """
    return abs(f1 - f2) < 0.0001


# def schedule_notes(midifile, meta_messages=False):
#     """Play back all tracks.

#     The generator will sleep between each message, so that
#     messages are yielded with correct timing. The time attribute
#     is set to the number of seconds slept since the previous
#     message.

#     You will receive copies of the original messages, so you can
#     safely modify them without ruining the tracks.
#     """

#     # The tracks of type 2 files are not in sync, so they can
#     # not be played back like this.
#     if midifile.type == 2:
#         raise TypeError('type 2 file can not be played back like this')

#     seconds_per_tick = midifile._compute_tick_time(DEFAULT_TEMPO)

#     messages = midifile._merge_tracks(midifile.tracks)

#     # Play back messages.
#     now = 0
#     for message in messages:
#         delta = message.time - now
#         if delta:
#             sleep_time = delta * seconds_per_tick
#             time.sleep(sleep_time)
#         else:
#             sleep_time = 0.0

#         if meta_messages or isinstance(message, Message):
#             message.time = sleep_time
#             yield message

#         now += delta
#         if message.type == 'set_tempo':
#             seconds_per_tick = self._compute_tick_time(message.tempo)


class MidiFilePlayer(EventDispatcher):
    playing = BooleanProperty(False)

    def __init__(self, fileName):
        self.mf = MidiFile(fileName)
        self.time_signature = None
        self.tempo = DEFAULT_TEMPO
        for i, track in enumerate(self.mf.tracks):
            for msg in [m for m in track if isinstance(m, MetaMessage)]:
                if msg.type == 'set_tempo':
                    self.tempo = msg.tempo
                elif msg.type == 'time_signature':
                    self.time_signature = (msg.numerator, msg.denominator)

        self.seconds_per_tick = self.mf._compute_tick_time(self.tempo)
        self.messages = self.mf._merge_tracks(self.mf.tracks)
        self.msg_queue = deque(self.messages)
        self.msg_buffer = deque()
        self.now = 0
        self.register_event_type('on_next_msgs')

        (
            self.beats_per_measure,
            self.beat_length,
            self.bar_length
        ) = self._calculate_lengths()

    def _calculate_lengths(self):
        """Calculate and return the length of beats and bars in this file.

        Rationale for calculating:
        When the upper number in the time signature is NOT a multiple of 3,
        excepted 3 (binary beat), then the beat is equal to the fraction
        represented by the bottom number.
        When the upper number is a multiple of 3, excepted 3 (ternary beat),
        then the beat is equal to the fraction represented by the bottom
        number, multiplied by 3.
        """
        beat_length = float(Fraction(60, midi_tempo_to_bpm(self.tempo)))
        num_beats, beat_unit = self.time_signature
        beats_per_measure = Fraction(num_beats, 1 if num_beats % 3 else 3)
        return beats_per_measure, beat_length, beats_per_measure * beat_length

    def _synth_msg(self, msg, *args):
        self.now = msg.time
        if msg.type == 'note_on':
            SYNTH.noteon(msg.channel, msg.note, msg.velocity)
        elif msg.type == 'note_off':
            SYNTH.noteoff(msg.channel, msg.note)
        elif msg.type == 'pitchwheel':
            SYNTH.pitch_bend(msg.channel, msg.pitch)
        elif msg.type == 'control_change':
            SYNTH.cc(msg.channel, msg.control, msg.value)
        elif msg.type == 'program_change':
            SYNTH.program_change(msg.channel, msg.program)
        elif msg.type == 'reset':
            SYNTH.program_reset()

    def _synth_buffer(self, *args):
        while self.msg_buffer:
            self._synth_msg(self.msg_buffer.popleft())
        self.on_next_msgs()

    def _schedule_buffer(self):
        Clock.schedule_once(self._synth_buffer,
                            self.delta * self.seconds_per_tick)

    def on_next_msgs(self):
        if self.msg_queue:
            self.msg_buffer.append(self.msg_queue.popleft())
            self.delta = self.msg_buffer[0].time - self.now
            while (self.msg_queue
                   and self.msg_queue[0].time - self.now == self.delta):
                self.msg_buffer.append(self.msg_queue.popleft())
            self._schedule_buffer()
        else:
            ticks_per_measure = (self.mf.ticks_per_beat
                                 * self.beats_per_measure)
            measure_round_up = ticks_per_measure - (self.now
                                                    % ticks_per_measure)
            Clock.schedule_once(self.stop,
                                measure_round_up * self.seconds_per_tick)

    def play(self, *args):
        self.playing = True
        # Schedule all the messages that play immediately
        while self.msg_queue[0].time == 0:
            self.msg_buffer.append(self.msg_queue.popleft())
        self._synth_buffer()

    def stop(self, *args):
        self.playing = False
        self.now = 0
        self.msg_queue = deque(self.messages)
