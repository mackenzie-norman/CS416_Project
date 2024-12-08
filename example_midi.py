#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Create a new MIDI file with some random notes.

The file is saved to test.mid.
"""
import random
import sys

from mido import MAX_PITCHWHEEL, Message, MidiFile, MidiTrack

notes = [64, 64 + 7, 64 + 12]

outfile = MidiFile(type=1)

track = MidiTrack()
outfile.tracks.append(track)


delta = 600
ticks_per_expr = int(sys.argv[1]) if len(sys.argv) > 1 else 20
for i in range(4):
    noteA = random.choice(notes)
    noteB = random.choice(notes)
    track.append(Message('note_on', note=noteA, velocity=100, time=0))
    track.append(Message('note_on', note=noteB, velocity=100, time=0))
    track.append(Message('note_off', note=noteA, velocity=100, time=delta))
    track.append(Message('note_off', note=noteB, velocity=100, time=delta))
    track.append(Message('program_change', program=i))
track = MidiTrack()
outfile.tracks.append(track)


delta = 600
ticks_per_expr = int(sys.argv[1]) if len(sys.argv) > 1 else 20
for i in range(4):
    noteA = random.choice(notes)
    noteB = random.choice(notes)
    track.append(Message('note_on', note=noteA, velocity=100, time=0))
    track.append(Message('note_on', note=noteB, velocity=100, time=0))
    track.append(Message('note_off', note=noteA, velocity=100, time=delta))
    track.append(Message('note_off', note=noteB, velocity=100, time=delta))
    track.append(Message('program_change', program=i))

outfile.save('test.mid')