from __future__ import division

from collections import deque
from fractions import Fraction

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty

from mingus.midi import fluidsynth
from mido.midifiles import MidiFile, MetaMessage, Message, merge_tracks

SYNTH = fluidsynth.midi.fs
DEFAULT_TEMPO = 500000


class PlayStatus(object):
    Stopped, Playing, Start = range(3)


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
    status = NumericProperty(PlayStatus.Start)
    bar_number = NumericProperty(0)

    def __init__(self, fileName):
        self.mf = MidiFile(fileName)
        self.time_signature = None
        self.tempo = DEFAULT_TEMPO
        for i, track in enumerate(self.mf.tracks):
            for msg in [m for m in track if isinstance(m, MetaMessage)]:
                if msg.type == 'set_tempo':
                    print(msg.tempo)
                    self.tempo = msg.tempo
                elif msg.type == 'time_signature':
                    self.time_signature = (msg.numerator, msg.denominator)

        self.messages = merge_tracks(self.mf.tracks)
        self.msg_queue = deque(self.messages)
        self.msg_buffer = deque()
        self.now = 0
        self.bar_pending = False
        self.loop = True
        self.notes_on = set()

        # XXX: All this time handling should go in a class
        (
            self.beats_per_bar,
            self.beat_length,
            self.bar_length
        ) = self._calculate_lengths()
        self.seconds_per_tick = self._get_seconds_per_tick(self.mf.ticks_per_beat)
        self.ticks_per_bar = (self.mf.ticks_per_beat * self.beats_per_bar)

    def _get_seconds_per_tick(self, ticks_per_beat):
        return (self.tempo / 1000000.0) / float(ticks_per_beat)

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
        beat_length = 60 / midi_tempo_to_bpm(self.tempo)
        num_beats, beat_unit = self.time_signature
        beats_per_bar = Fraction(num_beats, 1 if num_beats % 3 else 3)
        return beats_per_bar, beat_length, beats_per_bar * beat_length

    def _synth_msg(self, msg, *args):
        self.now = msg.time
        if msg.type == 'note_on':
            SYNTH.noteon(msg.channel, msg.note, msg.velocity)
            self.notes_on.add((msg.note, msg.channel))
        elif msg.type == 'note_off':
            SYNTH.noteoff(msg.channel, msg.note)
            self.notes_on.remove((msg.note, msg.channel))
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
        elif self.status != PlayStatus.Stopped:
            # no more messages; schedule a stop at the end of this bar
            bar_round_up = self.ticks_per_bar - (self.now % self.ticks_per_bar)
            Clock.schedule_once(self.done, bar_round_up * self.seconds_per_tick)

    def play(self, *args):
        self.status = PlayStatus.Playing
        if not self.msg_queue:
            self.msg_queue = deque(self.messages)
        # Schedule all the messages that play immediately
        while self.msg_queue[0].time == 0:
            self.msg_buffer.append(self.msg_queue.popleft())
        Clock.schedule_once(self._bar_break)
        self._synth_buffer()

    def done(self, *args):
        self.status = PlayStatus.Start
        self.reset()
        self.msg_queue = deque(self.messages)

    def stop(self):
        self.status = PlayStatus.Stopped
        Clock.unschedule(self._bar_break)
        # Fill the queue with messages that stop all notes currently playing.
        # Put a reset in there for good measure, though it doesn't seem to
        # actually do anything.
        self.msg_queue = deque([Message('note_off', note=n, channel=c,
                                        velocity=0, time=0)
                                for n, c in self.notes_on])
        self.msg_queue.append(Message('reset'))
        Clock.unschedule(self._synth_buffer)
        self.fill_buffer()
        self.reset()

    def reset(self):
        self.now, self.bar_number = 0, 0
        self.bar_pending = False
