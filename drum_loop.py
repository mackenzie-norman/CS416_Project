
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo, second2tick

mid = MidiFile(type = 1)
track = MidiTrack()
mid.tracks.append(track)

#track.append(MetaMessage('key_signature', key='Dm'))
#track.append(MetaMessage('set_tempo', tempo=bpm2tempo(120)))
#track.append(MetaMessage('time_signature', numerator=4, denominator=4))

#track.append(Message('program_change', program=12, time=10))
delta = 600
for i in range(4):
    track.append(Message('note_on',  note=60, velocity=100, time=0))
    
    track.append(Message('note_off',  note=60, velocity=100, time=delta))

track.append(MetaMessage('end_of_track'))

mid.save('new_song.mid')