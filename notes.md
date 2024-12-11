# Notes for this project

I am running into an issue
Want to use a generator class with my notes, but if I am using a .wav then I can't reset one globally

got my generator working well, and the fp side of things is good. 
```python
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo, second2tick

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

track.append(MetaMessage('key_signature', key='Dm'))
track.append(MetaMessage('set_tempo', tempo=bpm2tempo(120)))
track.append(MetaMessage('time_signature', numerator=6, denominator=8))

track.append(Message('program_change', program=12, time=10))
track.append(Message('note_on', channel=2, note=60, velocity=64, time=1))
track.append(Message('note_off', channel=2, note=60, velocity=100, time=2))

track.append(MetaMessage('end_of_track'))

mid.save('new_song.mid')
```
https://stackoverflow.com/questions/76013580/mido-example-code-for-creating-a-midifile

important to note that order matters a lot in midifiles

plan for now is to generate notes at tempo, then loop. 
can edit each note/notes and keep note on off

hard parts are going to be handling multi notes (need to get sleep time right)

also would like to be able to play over it, but not sure if that will be possible (the sleeping seems hard. need a better async/non blocking version)

had a problem with notes being shortened, debugged the problem being since I reuse notes a note needs to be reset

I got really annoyed that I couldn't see what the midi files I was making looked like so I threw together a VSCode extension to be able to see them

It is really hacky at the moment but I hope to spend a little more time and get it working well enough