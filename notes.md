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