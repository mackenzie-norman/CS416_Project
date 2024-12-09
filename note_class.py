import numpy as np
def key_to_freq(key, base_freq = 440):
    return base_freq * 2 ** ((key - 69) / 12)
class Note:
    #I took a lot of these defaults from MISY
    def __init__(self, key, generator, attack_time = 0.020, release_time = 0.1, sample_rate = 48000, base_freq = 440 ):
        self.frequency = key_to_freq(key, base_freq)
        self.attack_time = attack_time
        self.attack_time_remaining = self.attack_time
        self.release_time = release_time
        self.generator = generator
        self.playing = True
        self.sample_rate = sample_rate
        self.release_time_remaining = None

    # Note has been released.
    def release(self):
        self.release_time_remaining = self.release_time
    def finish(self):
        #since our notes stay around, we need to reset some stuff
        self.playing = False
        self.generator.reset()
        self.release_time_remaining = None
        self.attack_time_remaining = self.attack_time

    def update_time(self,attack_time,release_time):
        self.attack_time = attack_time
        #self.attack_time_remaining = self.attack_time
        self.release_time = release_time
    def play(self):
        self.playing = True
        if self.release_time_remaining:
            self.release_time_remaining = None    
        
    # Accept a time linspace to generate samples in.  Return
    # that many samples of note being played, or None if
    # note is over.
    def samples(self, t):
        if not self.playing:
            return None

        frame_count = len(t)
        #out_frequency = self.frequency

        # Pick and generate a waveform.
        samples = self.generator.get_samples(t )

        if self.release_time_remaining is not None:
            # Do release part of ADSR envelope.
            release_time_remaining = self.release_time_remaining
            if release_time_remaining <= 0:
                print("finish")
                self.finish()
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