from enum import Enum
import numpy as np
from typing import Union
import matplotlib.pyplot as plt


WARN_SAMPLES = 4
DEFAULT_INITIAL_EXP_AMP = 0.0001
DEFAULT_END_EXP_AMP = 0.001

class EnvelopeTypes(Enum):
    HANNING = 1
    ADSR = 3

class Envelope():
    def __init__(
        self, 
        envelope_type: EnvelopeTypes, 
        dur: float, 
        sr: int = 44100,
        atk: Union[float, None] = None, 
        decay: Union[float, None] = None, 
        release: Union[float, None] = None, 
        initial_amp: float = 0,
        sustain_amp: float = 1,
        end_amp: float = 0,
        mode: str = "lin"
    ) -> None:
        
        """
        INIT ENVELOPE
        
        Args
        ----
            envelope_type: EnvelopeTypes
                type of envelopes:
                    HANNING
                    ADSR
            dur: float
                total envelope duration in sec.
            sr: int
                sampling rate in Hz
                
            in ADSR type, specify:
                atk: float|None
                    attack duration (deafult = None). 
                    It specify the duration of the transition from initial to peak amp
                decay: float|None
                    decay duration (deafult = None).
                    It specify the duration of the transition from peak amp to sustain amp
                release: float|None
                    release duration (deafult = None).
                    It specify the duration of the transition from sustain amp to end amp
                initial_amp: float
                    Value of the initial amp (linear mode: default = 0.0, exp mode: default = 0.0001)
                sustain_amp: float
                    Value of the sustain amp (default = 1.0)
                end_amp: float
                    Value of the end amp (linear mode: default = 0.0, exp mode: default = 0.001)
                mode: str
                    envelope mode (default = "lin"):
                        "lin": lineam mode
                        "exp": exponential mode
                NOTE: 
                    - the value of initial_amp, sustain_amp and end_amp is from 0.0 to 1.0
                    - the duration of sustain segment is equal to dur - (atk + decay + release)
            
        """
        
        self.envelope_type = envelope_type
        self.dur = dur
        self.sr = sr        
        self.env = None
        self.atk = atk
        self.decay = decay
        self.release = release
        self.initial_amp = initial_amp
        self.sustain_amp = sustain_amp
        self.end_amp = end_amp    
        modes = ["lin", "exp"]
        assert mode in modes, f"[ERROR] mode can be only: {modes}!"
        self.mode = mode
        
        if self.mode == "exp":
            if self.initial_amp <= 0:
                print(f"[INFO] mode exp: initial amp set to default value = {DEFAULT_INITIAL_EXP_AMP}!")
                self.initial_amp = DEFAULT_INITIAL_EXP_AMP
            if self.end_amp <= 0:
                print(f"[INFO] mode exp: end amp set to default value = {DEFAULT_END_EXP_AMP}!")
                self.end_amp = DEFAULT_END_EXP_AMP
        
        self.__index = 0
    
    @property
    def envelope_t(self) -> int:
        return self.__index
    
    @envelope_t.setter
    def envelope_t(self) -> None:
        self.__index = 0
    
    def create_envelope(self) -> None:
        
        """
        CREATE ENVELOPE
        """
        
        self.lenght = int(self.dur * self.sr)
        env = np.zeros(self.lenght)
        
        self.atk = self.atk if self.atk is not None else 0.0
        atk_samples = int(self.atk * self.sr) - WARN_SAMPLES
        self.decay = self.decay if self.decay is not None else 0.0
        decay_samples = int(self.decay * self.sr)
        self.release = self.release if self.release is not None else 0.0
        release_samples = int(self.release * self.sr)
        sustain_samples = abs((self.lenght - (atk_samples + decay_samples + release_samples)))
        sustain_samples -= WARN_SAMPLES
        # print(atk_samples, decay_samples, sustain_samples, release_samples, atk_samples + release_samples)
        
        assert self.lenght >= (atk_samples + decay_samples + release_samples + sustain_samples), "[ERROR] atk, decay, release and sustain durs summation must be less then total length of envelope!"
        
        match self.envelope_type.name:
            case 'HANNING':
                self.env = np.hanning(self.lenght)
            case "ADSR":
                # atk
                initial_amp = self.initial_amp
                linear_step = (1 - self.initial_amp) / atk_samples
                exp_step = np.exp(np.log((1 - self.initial_amp) / self.initial_amp) / atk_samples) if self.mode == "exp" else 0.0
                start_atk = WARN_SAMPLES
                for a in range(atk_samples):
                    if self.mode == "lin":
                        atk_value = self.initial_amp + linear_step * a
                    else:
                        atk_value = initial_amp
                        initial_amp *= exp_step
                    env[start_atk + a] = atk_value
                
                # decay
                linear_step = (1 - self.sustain_amp) / decay_samples if self.mode == "lin" and decay_samples else 0.0
                exp_step = np.exp(np.log(self.sustain_amp) / decay_samples) if self.mode == "exp" and decay_samples else 0.0
                initial_amp = 1.0
                start_decay = atk_samples
                for d in range(decay_samples):
                    if self.mode == "lin":
                        decay_value = 1 - linear_step * d
                    else:
                        decay_value = initial_amp
                        initial_amp *= exp_step
                    env[start_decay + d] = decay_value
                
                # sustain
                start_sustain = atk_samples + decay_samples
                for s in range(sustain_samples):
                    env[start_sustain + s] = self.sustain_amp
                
                # release
                linear_step = (self.sustain_amp - self.end_amp) / release_samples if self.mode == "lin" and release_samples else 0.0
                exp_step = np.exp(np.log(self.end_amp / self.sustain_amp) / release_samples) if self.mode == "exp" and release_samples else 0.0
                initial_amp = self.sustain_amp
                start_release = atk_samples + decay_samples + sustain_samples
                for r in range(release_samples):
                    if self.mode == "lin":
                        release_value = self.sustain_amp - linear_step * r
                    else:
                        release_value = initial_amp
                        initial_amp *= exp_step
                    env[start_release + r] = release_value
                
                self.env = env
            case _:
                print("[ERROR] envelope type not implemented!\n")
                exit(1)
    
    def generate_env_factor(self) -> float:
        
        """
        GENERATE ENV FACTOR
    
        Returns
        -------
        float
            value by which to multiply the signal sample (sample by sample)
        """
        
        sample_env = self.env[self.__index]
        self.__index += 1
        self.__index %= self.lenght
        return sample_env
    
    def show_env(self) -> None:
        
        """
        SHOW THE ENV GRAPH
        """
        
        self.create_envelope()
        plt.stem(np.linspace(0, self.dur, self.lenght), self.env)
        plt.xlabel(xlabel="time[s]")
        plt.ylabel(ylabel="amp [0, 1]")
        plt.grid(alpha=0.6)
        plt.show()
         
                