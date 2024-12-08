
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo, second2tick

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

track.append(MetaMessage('key_signature', key='Dm'))
track.append(MetaMessage('set_tempo', tempo=bpm2tempo(12)))
track.append(MetaMessage('time_signature', numerator=6, denominator=8))

track.append(Message('program_change', program=12, time=10))
#for i in range(200):
track.append(Message('note_on', channel=2, note=60, velocity=64, time=40))
track.append(Message('note_off', channel=2, note=60, velocity=100, time=2))

track.append(MetaMessage('end_of_track'))

mid.save('new_song.mid')