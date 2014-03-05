from collections import deque
from fractions import Fraction
from functools import partial

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, NumericProperty

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
    bar_number = NumericProperty(0)

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

        self.messages = self.mf._merge_tracks(self.mf.tracks)
        self.msg_queue = deque(self.messages)
        self.msg_buffer = deque()
        self.now = 0
        self.bar_pending = False

        # XXX: All this time handling should go in a class
        (
            self.beats_per_bar,
            self.beat_length,
            self.bar_length
        ) = self._calculate_lengths()
        self.seconds_per_tick = self.mf._compute_tick_time(self.tempo)
        self.ticks_per_bar = (self.mf.ticks_per_beat * self.beats_per_bar)

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
        beats_per_bar = Fraction(num_beats, 1 if num_beats % 3 else 3)
        return beats_per_bar, beat_length, beats_per_bar * beat_length

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
        self.fill_buffer()

    def _schedule_buffer(self):
        Clock.schedule_once(self._synth_buffer,
                            self.delta * self.seconds_per_tick)

    def _bar_break(self, *args):
        self.bar_number += 1
        self.bar_pending = False

    def fill_buffer(self):
        if self.msg_queue:
            self.msg_buffer.append(self.msg_queue.popleft())
            self.delta = self.msg_buffer[0].time - self.now
            while (self.msg_queue
                   and self.msg_queue[0].time - self.now == self.delta):
                self.msg_buffer.append(self.msg_queue.popleft())
            self._schedule_buffer()
            # XXX: Scheduling a bar break will fail if there are no messages
            # in a bar. To fix this we should look ahead in the queue
            # and schedule bar until the next message, but I don't feel
            # like it right now.
            if (self.now >= self.bar_number * self.ticks_per_bar
                    and not self.bar_pending):
                Clock.schedule_once(
                    self._bar_break,
                    ((self.bar_number + 1) * self.ticks_per_bar - self.now)
                    * self.seconds_per_tick
                )
                self.bar_pending = True
        else:
            # no more messages; schedule a stop at the end of this bar
            bar_round_up = self.ticks_per_bar - (self.now % self.ticks_per_bar)
            Clock.schedule_once(self.stop, bar_round_up * self.seconds_per_tick)

    def play(self, *args):
        self.playing = True
        # Schedule all the messages that play immediately
        while self.msg_queue[0].time == 0:
            self.msg_buffer.append(self.msg_queue.popleft())
        Clock.schedule_once(self._bar_break)
        self._synth_buffer()

    def stop(self, *args):
        self.playing = False
        self.now = 0
        self.bar_number = 0
        self.bar_pending = False
        self.msg_queue = deque(self.messages)
