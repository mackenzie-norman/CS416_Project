#A LOT OF THIS CODE CAME FROM RHOSY, MISY .py 
import mido, sounddevice
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

from wave_tables import Sine_Generator, Square_Generator, Saw_Generator, Sample_Generator
# Calculate frequency for a 12-tone equal-tempered Western
# scale given MIDI note number. Change 440 to 432 for better
# sound </s>.

def key_to_freq(key, base_freq = 440):
    return base_freq * 2 ** ((key - 69) / 12)
#The idea is each can come from a different oscillator that is selected by the midi (read synth)
class Note:
    #I took a lot of these defaults from MISY
    def __init__(self, key, osc, attack_time = 0.020, release_time = 0.1, sample_rate = 48000, base_freq = 440 ):
        self.frequency = key_to_freq(key, base_freq)
        self.attack_time = attack_time
        self.attack_time_remaining = self.attack_time
        self.release_time = release_time
        self.out_osc = osc
        self.playing = True
        self.sample_rate = sample_rate
        self.release_time_remaining = None

    # Note has been released.
    def release(self):
        self.release_time_remaining = self.release_time

    # Accept a time linspace to generate samples in.  Return
    # that many samples of note being played, or None if
    # note is over.
    def samples(self, t):
        if not self.playing:
            return None

        frame_count = len(t)
        out_frequency = self.frequency

        # Pick and generate a waveform.
        samples = self.out_osc(t, out_frequency)

        if self.release_time_remaining is not None:
            # Do release part of ADSR envelope.
            release_time_remaining = self.release_time_remaining
            if release_time_remaining <= 0:
                self.playing = False
                return None
            # Figure out the gain at the starting time according
            # to a linear ramp.
            start_gain = release_time_remaining / self.release_time
            # Figure out the time after the last sample, and
            # adjust the release_time_remaining to reflect it.
            end_time = frame_count / self.sample_rate
            release_time_remaining -= end_time
            # Figure out the gain at the ending time according
            # to a linear ramp.
            end_gain = release_time_remaining / self.release_time
            # Calculate the linear slope over the samples. Make
            # sure it doesn't go below 0.0 due to finishing the
            # release in the middle.
            #
            # XXX This should probably be linear in dBFS rather than
            # linear in amplitude, but meh.
            envelope = np.clip(
                np.linspace(start_gain, end_gain, frame_count),
                0.0,
                1.0,
            )
            # Apply the per-sample gains for the release.
            samples *= envelope
            # Update the release time remaining for next pass.
            self.release_time_remaining = max(0, release_time_remaining)
        elif self.attack_time_remaining > 0.0:
            # Do attack part of ADSR envelope.
            attack_time_remaining = self.attack_time_remaining
            # Figure out the gain at the starting time according
            # to a linear ramp.
            start_gain = 1.0 - attack_time_remaining / self.attack_time
            # Figure out the time after the last sample, and
            # adjust the attack_time_remaining to reflect it.
            end_time = frame_count / self.sample_rate
            attack_time_remaining -= end_time
            # Figure out the gain at the ending time according
            # to a linear ramp.
            end_gain = 1.0 - attack_time_remaining / self.attack_time
            # Calculate the linear slope over the samples. Make
            # sure it doesn't go above 1.0 due to finishing the
            # attack in the middle.
            #
            # XXX This should probably be linear in dBFS rather than
            # linear in amplitude, but meh.
            envelope = np.clip(
                np.linspace(start_gain, end_gain, frame_count),
                0.0,
                1.0,
            )
            # Apply the per-sample gains for the attack.
            samples *= envelope
            # Update the attack time remaining for next pass.
            self.attack_time_remaining = attack_time_remaining

        return samples
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
def sine_samples(t, f):
    return np.sin(2 * np.pi * f * t)

# Return a rising sawtooth wave at frequency f over the
# given sample times t.
def saw_samples(t, f):
    return (f * t) % 2.0 - 1.0

# Return a square wave at frequency f over the
# given sample times t.
def square_samples(t, f):
    return np.sign((f * t) % 2.0 - 1.0)
def compose_waves(func1, func2):
    def combined_function(t, f):
        return func1(t, f) + func2(t, f)
    return combined_function
# following stack exchange https://music.stackexchange.com/questions/88572/how-are-chord-ratios-developed-exactly
def chord(func):
    def funct(t,f):
         
        end = func(t,f) + func(t , f* 1.25992105 ) + func(t, f * 1.498307077)
        return end
    return funct
def noise_sample(t,f):

    duration = int(0.1 * len(t))
    noise_part = np.linspace(0, 1, duration, endpoint=False)
    noise_part = square_samples(sine_samples(saw_samples(noise_part,440), 440), 440)
    t[:duration] = noise_part
    return t
class Midi:
    #
    
    def __init__(self, choose_input = False) -> None:

        if choose_input:
            self.controller = mido.open_input(pick_midi())
        else:
            self.controller = mido.open_input(pick_midi(default=1))
        self.out_keys = dict()
        #I am not sure this is needed since we are letting this flow through but, does allow for neat things if we wanted to plot, etc.
        self.NoteClass = Note 
        self.programs = [Sine_Generator(), Square_Generator(), Saw_Generator(), Sample_Generator("""code\\sounds\\echomorph-hpf.wav""")]
        #self.programs = [g.get_samples for g in self.generators()]
        #self.programs += [noise_sample]
        self.prev_osc = sine_samples 
        self.oscillator = sine_samples

        self.note_attack_time = 0.020
        self.note_release_time = 0.1
        self.stop_values = 121
        self.attack_knob = 50
        self.release_knob = 51
        self.base_freq = 432
        self.log_notes = False
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
            self.out_keys[key] = self.NoteClass(key, self.oscillator, attack_time=self.note_attack_time, release_time=self.note_release_time, base_freq=self.base_freq)
        
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
            elif mesg.control == self.release_knob:
                    self.note_release_time = (0.020 * 127) * (mesg.value /127)
            elif mesg.control == 53:
                
                if mesg.value != 0:
                    self.set_oscillator(chord(self.oscillator))
                else:
                    self.set_oscillator(self.prev_osc)
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
            self.oscillator = self.programs[mesg.program % len(self.programs )]
            self.set_oscillator(self.programs[mesg.program % len(self.programs )])
        else:
            print('unknown MIDI message', mesg)
        return True

    def get_out_keys(self): return self.out_keys

    def plot_osc(self): 
        #goal is to show a plot of our waveform
        
        plt.plot(self.oscillator(sample_times(10 * self.base_freq) ,self.base_freq))
        plt.show()
    
    def set_oscillator(self, new_osc):
        self.prev_osc = self.oscillator
        self.oscillator = new_osc

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
    # If keys are pressed, generate sounds.
    if synth.get_out_keys():
        # Time point in seconds for each sample.
        t = sample_times(frame_count)

        # Set of keys that need playing.
        on_keys = list(synth.get_out_keys().keys())
        # Set of keys that need deleting.
        del_keys = set()
        # Generate the samples for each key and add them
        # into the mix.
        for key in on_keys:
            note = synth.get_out_keys()[key]
            note_samples = note.samples(t)
            if note_samples is None:
                del_keys.add(key)
                continue
            else:
                #need to find better scaling to stop clipping
                note_samples *= 0.25
            samples += note_samples

        # Close the deleted keys.
        for key in del_keys:
            del synth.out_keys[key]

    # Adjust the gain so that each key gets louder up to
    # some maximum.  If necessary, scale to avoid clipping.
    nkeys = len(synth.get_out_keys())
    if nkeys <= 8:
        samples *= 1.0 / 8.0
    else:
        samples *= 1.0 / len(synth.get_out_keys())

    # Reshape to have an array of 1 sample for each frame.
    # Must write into the existing array rather than
    # accidentally copying over the parameter.
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