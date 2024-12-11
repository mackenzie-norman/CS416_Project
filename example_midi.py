#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT
import re
names = [ "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B", ]
note_names = { s : i for i, s in enumerate(names) }
note_name_re = re.compile(r"([A-G]b?)(\[([0-8])\])?")
# Given a string representing a knob setting between 0 and
# 10 inclusive, return a linear gain value between 0 and 1
# inclusive. The input is treated as decibels, with 10 being
# 0dB and 0 being the specified `db_at_zero` decibels.
def parse_log_knob(k, db_at_zero=-40):
    v = float(k)
    if v < 0 or v > 10:
        raise ValueError
    if v < 0.1:
        return 0
    if v > 9.9:
        return 10
    return 10**(-db_at_zero * (v - 10) / 200)

# Given a string representing a knob setting between 0 and
# 10 inclusive, return a linear gain value between 0 and 1
# inclusive.
def parse_linear_knob(k):
    v = float(k)
    if v < 0 or v > 10:
        raise ValueError
    return v / 10

# Given a string representing an gain in decibels, return a
# linear gain value in the interval (0,1]. The input gain
# must be negative.
def parse_db(d):
    v = float(d)
    if v > 0:
        raise ValueError
    return 10**(v / 20)

def parse_bool(arg):
    if "f" in arg:
        return False
    else: return True
def parse_list_of_ints(arg):
    return list(map(int, arg.split(',')))

    
def parse_note(s):
    m = note_name_re.fullmatch(s)
    if m is None:
        raise ValueError
    s = m[1]
    s = s[0].upper() + s[1:]
    q = 4
    if m[3] is not None:
        q = int(m[3])
    return note_names[s] + 12 * q
import random
import sys
import argparse
from mido import MAX_PITCHWHEEL, Message, MidiFile, MidiTrack,  bpm2tempo, second2tick,MetaMessage

ap = argparse.ArgumentParser()
ap.add_argument('--bpm', type=int, default=90)
ap.add_argument('--samplerate', type=int, default=48_000)
ap.add_argument('--root', type=parse_note, default="C[5]")
ap.add_argument('--bass-octave', type=int, default=2)
ap.add_argument('--balance', type=parse_linear_knob, default="5")
ap.add_argument('--gain', type=parse_db, default="-3")
ap.add_argument('--output')
ap.add_argument("--test", action="store_true", help=argparse.SUPPRESS)
ap.add_argument("--plot", type=parse_bool, default=False)
#MN add new chord progression
ap.add_argument("--chord-loop", type=parse_list_of_ints, default="1,5,6,4")
ap.add_argument("--loop", type= int, default=0)

args = ap.parse_args()
notes = [64, 64 + 4, 64 + 9]
# Take this from popgen.py
# Relative notes of a major scale.
major_scale = [0, 2, 4, 5, 7, 9, 11]

# Major chord scale tones — one-based.
major_chord = [1, 3, 5]

# Given a scale note with root note 0, return a key offset
# from the corresponding root MIDI key.
def note_to_key_offset(note):
    scale_degree = note % 7
    return note // 7 * 12 + major_scale[scale_degree]

# Given a position within a chord, return a scale note
# offset — zero-based.
def chord_to_note_offset(posn):
    chord_posn = posn % 3
    return posn // 3 * 7 + major_chord[chord_posn] - 1

# MIDI key where melody goes.
melody_root = args.root

# Bass MIDI key is below melody root.
bass_root = melody_root - 12 * args.bass_octave

# Root note offset for each chord in scale tones — one-based.
chord_loop = args.chord_loop

plot_sounds = args.plot

for i in range(args.loop):
    chord_loop += chord_loop

position = 0
def pick_notes(chord_root, n=4):
    max = n/2 
    global position
    p = position

    notes = []
    for _ in range(n):
        chord_note_offset = chord_to_note_offset(p)
        chord_note = note_to_key_offset(chord_root + chord_note_offset)
        notes.append(chord_note)

        if random.random() > 0.5:
            p = p + 1
        else:
            p = p - 1
        #p = p % max
    position = p
    return notes

outfile = MidiFile()

track = MidiTrack()
track.append(MetaMessage('set_tempo', tempo=bpm2tempo(100)))
outfile.tracks.append(track)


delta = 600
ticks_per_expr = int(sys.argv[1]) if len(sys.argv) > 1 else 20
for c in chord_loop: 
    notes = [note + melody_root for note in  pick_notes(c - 1, n = 4 )]
    bass_note = note_to_key_offset(c - 1) + bass_root
    track.append(Message('note_on', note=bass_note, velocity=100, time=10))
    for note in notes:
        track.append(Message('note_on', note=note, velocity=100, time=delta))
        track.append(Message('note_off', note=note, velocity=100, time=delta))


    track.append(Message('note_off', note=bass_note, velocity=100, time=0))


outfile.save('new_song.mid')