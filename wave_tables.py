#MN 
import numpy as np
from scipy import io, signal
#import sounddevice as sd
#NOTE trying to decide if these should be classes or just make a compose function. Probably make a compose function
class Wave_Generator:
    def __init__(self) -> None:
        pass
    def get_samples(self,t,f):
        #this does nothing
        return t 
    def reset():
        pass
class Sine_Generator(Wave_Generator):
    def get_samples(self,t, f):
        return np.sin(2 * np.pi * f * t)
class Saw_Generator(Wave_Generator):
    def get_samples(self,t, f):
        return (f * t) % 2.0 - 1.0

class Square_Generator(Wave_Generator):
    def get_samples(self,t, f):
        return np.sign((f * t) % 2.0 - 1.0)

class Sample_Generator(Wave_Generator):
    def __init__(self,wavfile_name) -> None:
        super().__init__()
        rate, data = io.wavfile.read(wavfile_name)
        assert data.dtype == np.int16
        data = data.astype(np.float32)
        data /= 32768
        self.data = data
        self.sample_loc = 0
    def get_samples(self,t,f):
        #super().get_samp
        #interpolate
        #new_data = self.data
        #new_data.resize(t.shape)
        #print(t)
        #wrap 
        while self.data.size < t.size:
            self.data = np.append(self.data,self.data)

        start = self.sample_loc 
        end = start + t.size
        indices = range(start,end)
        ret_data = self.data.take(indices, mode='wrap')
        assert(ret_data.size == t.size)
        self.sample_loc += t.size
        #print(self.sample_loc,ret_data)
        return ret_data
    def reset(self):
        self.sample_loc = 0


