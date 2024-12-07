#MN 
import numpy as np
from scipy import io, signal
from note_class import Note
#import sounddevice as sd

class Wave_Generator:
    def __init__(self,freq) -> None:
        self.freq = freq
        pass
    def get_samples(self,t):
        #this does nothing
        return t 
    def reset(self):
        pass
    def set_samples(self,f):
        self.get_samples = f
    #this is basically the only cool thing in this, quite like the idea of being able to combine two waves
    def __add__(self,other):
        #assert self.freq == other.freq
        new = Wave_Generator(freq=self.freq)
        new.set_samples( lambda x: self.get_samples(x) + other.get_samples(x))
        return new
class Sine_Generator(Wave_Generator):
    def get_samples(self,t ):
        return np.sin(2 * np.pi * self.freq * t)
class Saw_Generator(Wave_Generator):
    def get_samples(self,t):
        return (self.freq * t) % 2.0 - 1.0

class Square_Generator(Wave_Generator):
    def get_samples(self,t):
        return np.sign((self.freq * t) % 2.0 - 1.0)

class Sample_Generator(Wave_Generator):
    def __init__(self,freq, wavfile_name) -> None:
        super().__init__(freq=freq)
        rate, data = io.wavfile.read(wavfile_name)
        assert data.dtype == np.int16
        data = data.astype(np.float32)
        data /= 32768
        self.data = data.flatten()
        #we want to interp here

        speed_up_factor = 440/self.freq

        original_duration = len(data) / rate
        original_time = np.linspace(0, original_duration, num=len(data))
        new_time = np.linspace(0, original_duration, num=int(len(data) / speed_up_factor))

        new_data = np.interp(new_time, original_time, data)
        self.data = new_data
        self.sample_loc = 0
    def get_samples(self,t):
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

#class chorded(Wave_Generator):
    

if __name__ == "__main__":

    # right now were testing our sample code.
    #make a wave table
    {i:Note(key=i,osc=Sine_Generator().get_samples) for i in range(0,128)}
