# AUTOGENERATED! DO NOT EDIT! File to edit: beat_fit.ipynb (unless otherwise specified).

__all__ = ['primefactors', 'FracHalves', 'Offset', 'BeatFit', 'note_starts', 'input_tempo', 'NoteOn', 'NoteOff',
           'complete', 'play', 'outport']

# Cell
import mido

import random
import math
from math import floor, ceil

from fastcore.basics import patch
from fractions import Fraction

# Cell
def primefactors(n):
    while (n % 2 == 0):
        yield 2
        n //= 2
    p = 3
    while p*p <= n:
        while (n % p == 0):
            yield p
            n //= p
        p += 2
    if n > 2:
        yield n
    while True:
        yield 1

# Cell
def FracHalves():
    yield Fraction(1,1)
    fh = [Fraction(1,1)]
    fc = Fraction(1,2)
    while True:
        newf = []
        for f in fh:
            new = f - fc
            yield new
            newf.append(new)

        fc *= Fraction(1,2)
        fh.extend(newf)

# Cell
class Offset(Fraction):
    def __new__(cls, *args):
        f = Fraction(*args)
        return Fraction.__new__(cls, f.numerator%f.denominator, f.denominator)

    def __lt__(self, other):
        if self == other: return False
        if self.denominator != other.denominator:
            self_pf = primefactors(self.denominator)
            other_pf = primefactors(other.denominator)
            while True:
                sp = next(self_pf)
                op = next(other_pf)
                if sp != op:
                    return sp < op
        else:
            fh = FracHalves()
            while True:
                nfh = next(fh)
                num = ceil(nfh * self.denominator) - 1
                nf = Fraction(num, self.denominator)

                if nf == self: return True
                if nf == other: return False

# Cell
class BeatFit:
    def __init__(self, lead=None):
        if lead is not None:
            if not isinstance(lead, mido.MidiFile) or lead.type != 0:
                raise ValueError("Lead part must be a type 0 mido.MidiFile")
            self.onsets = BeatFit.note_starts(lead)
            # check lead contains at least two differing note starts
            if len(set(self.onsets)) < 2:
                raise ValueError("Lead part must contain at least two notes with differing start times")

        self.lead = lead

        self._input_tempo = None
        self.fitted_state = None
        self.loss_map = []

    def fit(self, iterations=100):
        state = self.random_state()
        for iteration in range(iterations):
            temp = self.temperature(iteration/iterations)
            next_state = self.neighbour(state)
            state_loss, next_state_loss = self.losses(state, next_state)
            if next_state_loss < state_loss or random.uniform(0,1) < math.exp((state_loss-next_state_loss)/temp):
                state = next_state

        self.fitted_state = state

# Cell
@patch(cls_method=True)
def note_starts(cls:BeatFit, lead):
    output = []
    pos = 0
    track = lead.tracks[0]
    ppq = lead.ticks_per_beat
    for m in track:
        if m.type == 'note_on':
            output.append(Fraction(pos, ppq))
        pos += m.time

    return output

# Cell
@patch(as_prop=True)
def input_tempo(self:BeatFit):
    if self._input_tempo is None:
        self._input_tempo = mido.tempo2bpm(500000)
        for msg in self.lead:
            # we assume just one tempo, so take the last one in the file
            if msg.type == 'set_tempo':
                self._input_tempo = mido.tempo2bpm(msg.tempo)
    return self._input_tempo

# Cell
@patch
def closest_div(self:BeatFit, a, b, targ_tempo, old_tempo=None):
    if old_tempo is None:
        old_tempo = self.input_tempo
    return max(1, round(targ_tempo * (b-a) / old_tempo))

# Cell
@patch
def random_state(self:BeatFit, bpm_min=40, bpm_max=280):
    a,b = tuple(random.sample(list(set(self.onsets)), 2))

    if a > b: a,b = b,a

    # choose a random tempo uniformly bewteen min and max
    targ_tempo = random.uniform(bpm_min, bpm_max)

    # calculate the appropriate divisor to reach tempo, but use at least one
    div = self.closest_div(a,b,targ_tempo)

    return a, b, div

# Cell
@patch
def temperature(self:BeatFit, p):
    return math.exp(-5 * p)

# Cell
@patch
def neighbour(self:BeatFit, state):
    a,b,div = state

    opts = list(set(self.onsets) - {a,b})

    def trans_a(a,b,div):
        a_new = random.choice(opts)
        div_new = max(1, round(div * abs(b-a_new) / abs(b-a)))
        return a_new, b, div_new
    def trans_b(a,b,div):
        b,a,div = trans_a(b,a,div)
        return a,b,div
    trans_div = lambda a,b,div: (a, b, 2 if div == 1 else div + random.choice([-1,1]))

    if len(opts) < 1:
        return trans_div(a,b,div)

    trans = random.choice([trans_a, trans_b, trans_div])
    a,b,div = trans(a,b,div)
    if a > b: a,b = b,a
    return a,b,div

# Cell
@patch
def transformed_onsets(self:BeatFit, state):
    a,b,div = state
    assert a < b
    return [(n-a) * div / (b-a) for n in self.onsets]

@patch
def offsets(self:BeatFit, state):
    return [Offset(n) for n in self.transformed_onsets(state)]

# Cell
@patch
def tempo(self:BeatFit, state=None):
    if state is None:
        state = self.fitted_state
    a,b,div = state
    assert a < b
    return self.input_tempo * div / (b-a)

# Cell
@patch
def losses(self:BeatFit, state, next_state):
    # update losses map with offsets from states
#     self.loss_map = sorted(list(set(self.loss_map)|set(self.offsets(state))|set(self.offsets(next_state))))
    for ss in [state, next_state]:
        for s in self.offsets(ss):
            if s not in self.loss_map:
                self.loss_map.append(s)
#     self.loss_map.extend(self.offsets(state))
#     self.loss_map.extend(self.offsets(next_state))
    self.loss_map.sort()

    # map offsets to losses, add tempo loss
    offs_lossf = lambda state: sum([self.loss_map.index(o) for o in self.offsets(state)])
    tempo_lossf = lambda state: math.exp((self.tempo(state)-280)/4)
    state_loss = offs_lossf(state) + tempo_lossf(state)
    next_state_loss = offs_lossf(next_state) + tempo_lossf(next_state)
    return state_loss, next_state_loss

# Cell
from dataclasses import dataclass

@dataclass
class NoteOn:
    pitch: int
    time: Fraction

@dataclass
class NoteOff:
    pitch: int
    time: Fraction

@patch(as_prop=True)
def complete(self:BeatFit):
    ppq = self.lead.ticks_per_beat
    lead_frac = []
    pos = 0
    for m in self.lead.tracks[0]:
        pos += m.time
        if m.type == 'note_on':
            lead_frac.append(NoteOn(m.note, Fraction(pos, ppq)))
        if m.type == 'note_off':
            lead_frac.append(NoteOff(m.note, Fraction(pos, ppq)))

    a,b,div = self.fitted_state

    transformed_events = []
    for e in lead_frac:
        time = (e.time-a) * div / (b-a)
        transformed_events.append(NoteOn(e.pitch, time) if isinstance(e, NoteOn) else NoteOff(e.pitch, time))

    anacrusis = floor(transformed_events[0].time) - 4
    length = ceil(transformed_events[-1].time) - anacrusis

    hihathit = [mido.Message('note_on', note=42, channel=9, time=0),
                mido.Message('note_off', note=42, channel=9, time=ppq)]

    midifile = mido.MidiFile(type=1)

    pulse = mido.MidiTrack()
    midifile.tracks.append(pulse)

    # append tempo to pulse track
    pulse.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.tempo())))
    pulse.extend(hihathit*length)

    trasf_lead = mido.MidiTrack()
    midifile.tracks.append(trasf_lead)

    pos = anacrusis
    for te in transformed_events:
        trasf_lead.append(mido.Message('note_on' if isinstance(te, NoteOn) else 'note_off', note=te.pitch,
                                       time=round((te.time-pos)*ppq)))
        pos = te.time

    return midifile

# Cell
outport = mido.open_output('mido_out', virtual=True)

def play(midifile):
    for m in midifile.play():
        outport.send(m)