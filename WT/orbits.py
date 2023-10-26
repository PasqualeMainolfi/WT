from enum import Enum
from numpy.typing import NDArray
from typing import Union
import numpy as np
from envelopes import Envelope
import matplotlib.pyplot as plt
import librosa as lb

TWOPI = 2 * np.pi

class OrbitTypes(Enum):
    CIRCULAR = 1
    SPIRAL = 2
    CAOS = 3
    SIG = 4

class Orbit():
    
    def __init__(self, orbit_type: OrbitTypes, center: tuple[float, float], envelope: Union[Envelope, None] = None) -> None:
        
        """
        INIT ORBIT
        
        Args
        ----
            orbit_type: OrbitTypes
                orbit mode, can be:
                    - CIRCULAR, circular orbit
                    - SPIRAL, spiral orbit
                    - CAOS, random orbit
                    - SIG, use a signal as an orbit
            center: tuple[float, float]
                orbit center [0, 1]
            envelope: Envelope|None
                envelope object (see envelopes.py)
        """
        
        self.orbit_type = orbit_type
        self.center = center
        self._envelope = envelope
        self.__flag = False
        
        self.__sig = None
        self.__sig_size = 0
        self.__sx = None
        self.__sy = None
        self.__ndx_sig = 0
        
    @property
    def envelope(self) -> int:
        return self._envelope
    
    @envelope.setter
    def envelope(self, env: Union[Envelope, None]) -> None:
        if self.orbit_type.name == "SIG":
            assert self.__sig is not None, "[ERROR] signal not found!\n"
        if env is not None:
            self._envelope = env
            self._envelope.create_envelope()
            self.__flag = True
        else:
            self.__flag = False
    
    @property
    def orbit_sig(self) -> NDArray:
        return self.__sig
    
    @orbit_sig.setter
    def orbit_sig(self, path: str) -> None:
        sig, _ = lb.load(path, sr=None, mono=False)
        self.__sig = sig
        self.__sx = self.__sig[0, :]
        self.__sy = self.__sx if self.orbit_sig.ndim == 1 else self.__sig[1, :] 
        self.__sig_size = len(self.__sy)
        self.__ndx_sig = 0
        
    
    def calculate(self, phase: float, freqs: tuple[float, float], max_r: float) -> tuple[float, float]:
        
        """
        CALCULATE CURRENT COORDS
        
        Args
        ----
            phase: float
                current phase
            freqs: tuple[float, float]
                x and y freq in Hz
            max_r: float
                max radius 

        Returns
        -------
        tuple[float, float]   
            coords (x, y)
        """
        
        env_factor = self._envelope.generate_env_factor() if self.__flag else 1.0
        
        match self.orbit_type.name:
            case 'CIRCULAR':
                return self.__circular_orbit(phase=phase, freqs=freqs, max_r=max_r, envelope_factor=env_factor, mode="circ")
            case 'SPIRAL':
                return self.__circular_orbit(phase=phase, freqs=freqs, max_r=max_r, envelope_factor=env_factor, mode="spir")
            case 'CAOS':
                return self.__caos_orbit(phase=phase, freqs=freqs, max_r=max_r, envelope_factor=env_factor)
            case 'SIG':
               return self.__sig_orbit(phase=phase, freqs=freqs, max_r=max_r, envelope_factor=env_factor)
            case _:
                print("[ERROR] orbit type not implemented!\n")
                exit(1)
        
    def __circular_orbit(self, phase: float, freqs: tuple[float, float], max_r: float, envelope_factor: float, mode: str) -> tuple[float, float]:
        
        rx = max_r if max_r <= 1 - self.center[0] else 1 - self.center[0]
        ry = max_r if max_r <= 1 - self.center[1] else 1 - self.center[1]
        
        factor = envelope_factor if mode == "circ" else envelope_factor * phase
        
        rx = rx * factor
        ry = ry * factor
    
        x = self.center[0] + rx * np.cos(TWOPI * freqs[0] * phase)
        y = self.center[1] + ry * np.sin(TWOPI * freqs[1] * phase)
    
        return x, y
    
    def __caos_orbit(self, phase: float, freqs: tuple[float, float], max_r: float, envelope_factor: float) -> tuple[float, float]:
        
        rx = max_r if max_r <= 1 - self.center[0] else 1 - self.center[0]
        ry = max_r if max_r <= 1 - self.center[1] else 1 - self.center[1]
    
        x = self.center[0] + np.random.uniform(0, rx * envelope_factor) * np.cos(TWOPI * freqs[0] * phase)
        y = self.center[1] + np.random.uniform(0, ry * envelope_factor) * np.sin(TWOPI * freqs[1] * phase)
    
        return x, y
    
    def __sig_orbit(self, phase: float, freqs: tuple[float, float], max_r: float, envelope_factor: float) -> tuple[float, float]:
                
        assert self.__sig is not None, "[ERROR] signal not found!\n"
        
        rx = max_r if max_r <= 1 - self.center[0] else 1 - self.center[0]
        ry = max_r if max_r <= 1 - self.center[1] else 1 - self.center[1]
        
        rx = rx if self.__sx[self.__ndx_sig] > rx * envelope_factor else self.__sx[self.__ndx_sig]
        ry = ry if self.__sy[self.__ndx_sig] > ry * envelope_factor else self.__sy[self.__ndx_sig]

        x = self.center[0] + rx * np.cos(TWOPI * freqs[0] * phase)
        y = self.center[1] + ry * np.sin(TWOPI * freqs[1] * phase)
        
        self.__ndx_sig += 1
        self.__ndx_sig %= self.__sig_size
    
        return x, y
    
    def show_orbit(self, period: float) -> None:
        
        """
        SHOW ORBIT
        
        Args
        ----
            period: float
                sampling period in sec.
        """
        
        samples = int(1 / period)
        
        orbx = np.zeros(samples, dtype=np.float64)
        orby = np.zeros(samples, dtype=np.float64)
        phase = 0.0
        for i in range(samples):
            match self.orbit_type.name:
                case "CIRCULAR":
                    (x, y) = self.__circular_orbit(phase=phase, freqs=(1, 1), max_r=1, envelope_factor=1, mode="circ")
                case "SPIRAL":
                    (x, y) = self.__circular_orbit(phase=phase, freqs=(1, 1), max_r=1, envelope_factor=1, mode="spir")
                case "CAOS":
                    (x, y) = self.__caos_orbit(phase=phase, freqs=(1, 1), max_r=1, envelope_factor=1)
                case "SIG":
                    assert self.__sig is not None, "[ERROR] signal not found!\n"
                    (x, y) = self.__sig_orbit(phase=phase, freqs=(1, 1), max_r=1, envelope_factor=1)
                case _:
                    print(f"[ERROR] show orbit mode not yet implemented!\n")
                    exit(1)
                    
            orbx[i] = x
            orby[i] = y
            phase += period
        
        plt.plot(orbx, orby, lw=0.3)
        plt.show()
        