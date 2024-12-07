#A LOT OF THIS CODE CAME FROM RHOSY, MISY .py 
import mido, sounddevice
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from note_class import Note
from wave_tables import Sine_Generator, Square_Generator, Saw_Generator, Sample_Generator
# Calculate frequency for a 12-tone equal-tempered Western
# scale given MIDI note number. Change 440 to 432 for better
# sound </s>.

def key_to_freq(key, base_freq = 440):
    return base_freq * 2 ** ((key - 69) / 12)
#The idea is each can come from a different oscillator that is selected by the midi (read synth)

#trying to make a midi class that has list that is collection of current notes down. 
def pick_midi(default = None):
    input_ports = mido.get_input_names()
    if default is None:
        prompt_str = "\n".join([f"{i + 1}. {port}" for i,port in enumerate(input_ports) ])
        sel = int(input(f"Input ports:\n{prompt_str}\nPlease enter a number between 1 and {len(input_ports) }:")) - 1
    else:
        sel = default -1
    assert sel <= len(input_ports) +1
    return input_ports[sel]

def chord(func):
    def funct(t,f):
         
        end = func(t,f) + func(t , f* 1.25992105 ) + func(t, f * 1.498307077)
        return end
    return funct
def standard_note_gen(max_notes= 128):
    sines = {i:Note(key=i,generator=Sine_Generator(freq=key_to_freq(i))) for i in range(0,max_notes)}
    squares  = {i:Note(key=i,generator=Square_Generator(freq=key_to_freq(i))) for i in range(0,max_notes)}
    saws = {i:Note(key=i,generator=Saw_Generator(freq=key_to_freq(i))) for i in range(0,max_notes)}
    samples  = {i:Note(key=i,generator=Sample_Generator(freq=key_to_freq(i), wavfile_name="""sounds\\bram.wav""")) for i in range(0,max_notes)}
    messed = {i:Note(key = i, generator=samples[i].generator + saws[i].generator) for i in range(0,max_notes)} 
    return [sines,squares,saws,samples,messed]
class Midi:
    #

    def __init__(self, choose_input = False) -> None:

        if choose_input:
            self.controller = mido.open_input(pick_midi())
        else:
            self.controller = mido.open_input(pick_midi(default=1))
        self.out_keys = dict()
        #I am not sure this is needed since we are letting this flow through but, does allow for neat things if we wanted to plot, etc.
        self.programs = standard_note_gen()
        self.chords = self.gen_chords()
        self.current_wave_table = self.programs[0]
        self.note_attack_time = 0.020
        self.note_release_time = 0.1
        self.stop_values = 121
        self.attack_knob = 50
        self.release_knob = 51
        self.base_freq = 432
        self.log_notes = False
        self.chord_on = False
    def update_programs(self):
        for array in self.programs:
            for id in array: 
                note = array[id]
                note.update_time(self.note_attack_time, self.note_release_time)
    def gen_chords(self):
        #go thru 
        chords  = []
        for array in self.programs:
            tmp_array = {}
            id = 0
            while  id + 9 in array:
                print(id)
                id += 1
                tmp_array[id] = Note(key = id, generator= array[id].generator + array[id + 4].generator + array[id + 7].generator )
            chords.append(tmp_array)
        return chords 
    def process_midi_event(self):
        # These globals define the interface to sound generation.
        #global out_keys, out_osc

        # Block until a MIDI message is received.
        mesg = self.controller.receive()
        if(mesg is None):
            return True

        # Select what to do based on message type.
        mesg_type = mesg.type
        # Special case: note on with velocity 0 indicates
        # note off (for older MIDI instruments).
        if mesg_type == 'note_on' and mesg.velocity == 0:
            mesg_type = 'note_off'
        # Add a note to the sound. If it is already on just
        # start it again.
        if mesg_type == 'note_on':
            key = mesg.note
            velocity = mesg.velocity / 127
            if self.log_notes:
                print('note on', key, mesg.velocity, round(velocity, 2))
            note =self.current_wave_table[key]
            note.playing = True  
            self.out_keys[key] = note
            #self.NoteClass(key, self.oscillator, attack_time=self.note_attack_time, release_time=self.note_release_time, base_freq=self.base_freq)
        
        # Remove a note from the sound. If it is already off,
        # this message will be ignored.
        elif mesg_type == 'note_off':
            key = mesg.note
            velocity = round(mesg.velocity / 127, 2)
            if self.log_notes:
                print('note off', key, mesg.velocity, velocity)
            if key in self.out_keys:
                self.out_keys[key].release()
        # Handle various controls.
        elif mesg.type == 'control_change':
            # XXX Hard-wired for "stop" key on Oxygen8.
            if mesg.control == self.stop_values:
                print('stop')
                return False
            
            # Unknown control changes are logged and ignored.
            elif mesg.control == self.attack_knob:
                    self.note_attack_time = (0.020 * 127) * (mesg.value /127)
                    self.update_programs()
            elif mesg.control == self.release_knob:
                    self.note_release_time = (0.020 * 127) * (mesg.value /127)
                    self.update_programs()
            elif mesg.control == 53:    
                if mesg.value != 0:
                    self.chord_on = True
                    self.current_wave_table = self.chords[self.programs.index(self.current_wave_table)]
                else:
                    self.chord_on = False
                    self.current_wave_table = self.programs[self.chords.index(self.current_wave_table)]
            elif mesg.control == 22:
                self.plot_osc()
            else:
                print(f"control", mesg.control, mesg.value)
        # XXX Pitchwheel is currently logged and ignored.
        elif mesg.type == 'pitchwheel':
            pitch = round(mesg.pitch / 127, 2)
            print('pitchwheel', mesg.pitch, pitch)
        elif mesg.type == 'program_change':
            print(mesg.program % len(self.programs))
            self.current_wave_table = self.programs[mesg.program % len(self.programs )]
            if self.chord_on:
                    self.current_wave_table = self.chords[self.programs.index(self.current_wave_table)]
            

            #self.set_oscillator(self.programs[mesg.program % len(self.programs )])
        else:
            print('unknown MIDI message', mesg)
        return True

    def get_out_keys(self): return self.out_keys

    def plot_osc(self): 
        #goal is to show a plot of our waveform
        plt.plot(self.current_wave_table[69].samples(sample_times(880)))
        plt.show()
        pass 
    def set_oscillator(self ):
        #self.current_wave_table
        pass
    def get_sounds(self,t,samples):
        on_keys = list(self.out_keys.keys())
        # Set of keys that need deleting.
        del_keys = set()
        # Generate the samples for each key and add them
        # into the mix.
        for key in on_keys:
            note = synth.out_keys[key]
            note_samples = note.samples(t)
            if note_samples is None:
                del_keys.add(note)
                continue
            else:
                #need to find better scaling to stop clipping
                note_samples *= 0.25
            samples += note_samples

        # Close the deleted keys.
        for key in del_keys:
            self.out_keys.pop(key,None)
            
        return samples
#small helper function
def sample_times(frame_count):
    return np.linspace(
        sample_clock / sample_rate,
        (sample_clock + frame_count) / sample_rate,
        frame_count,
        dtype=np.float32,
    )

sample_rate = 48000
sample_clock = 0
blocksize = 32
synth = Midi()

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
#synth.log_notes = True
while synth.process_midi_event():
    pass