from maxMidi import Midi, sample_times
import  sounddevice
import numpy as np
from mido import MidiFile

sample_rate = 48000
sample_clock = 0
blocksize = 32
synth = Midi()

def sample_times(frame_count):
    
    return np.linspace(
        sample_clock / sample_rate,
        (sample_clock + frame_count) / sample_rate,
        frame_count,
        dtype=np.float32,
    )
def output_callback(out_data, frame_count, time_info, status):
    # Make sure to update the *global* sample clock.
    global sample_clock
    global synth
    if status:
        print("output callback:", status)

    # Start with silence and maybe work up.
    samples = np.zeros(frame_count, dtype=np.float32)
    t = sample_times(frame_count)

    samples = synth.get_sounds(t,samples)
   
    
    out_data[:] = np.reshape(samples, (frame_count, 1))

    # Bump the sample clock for next cycle.
    sample_clock += frame_count

output_stream = sounddevice.OutputStream(
    samplerate=sample_rate,
    channels=1,
    blocksize=blocksize,
    callback=output_callback,
)
output_stream.start()
synth.log_notes = False
play = False

if play:
    while synth.process_midi_event():
        pass
else:
    for msg in MidiFile('GoodTheBadAndTheUgly.mid').play():
        print(msg)
        synth.process_midi_event(msg)