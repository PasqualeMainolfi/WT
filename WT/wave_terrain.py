import numpy as np
from terrain import Terrain
from orbits import  Orbit
from envelopes import Envelope
from typing import Union

TWOPI = 2 * np.pi
DBLOCK_ORDER = 3
DBLOCK_FREQ = 10

class WaveTerrainSynthesis():
    def __init__(self, sr: int = 44100) -> None:
        
        """
        INIT WAVA TERRAIN
        
        Args
        ----
            sr: int
                sampling frequency in Hz
        """
        
        self.sr = sr
        self._terrain = None
        self._surface = None
        self._surface_width = None
        self._surface_height = None
        self._orbit = None
        
        self.__delayed_samples = np.zeros((2, DBLOCK_ORDER), dtype=np.float64)
        self.__phase = 0
        self.__count_terrain_update = 0
        self.__dcblock_coeff = 1 - (TWOPI * DBLOCK_FREQ / self.sr)
    
    @property
    def terrain(self) -> Terrain:
        return self.terrain
    
    @terrain.setter
    def terrain(self, terrain: Terrain) -> None:
        self._terrain = terrain
        self._surface = self._terrain.generate_surface()
        self._surface_width = self._terrain.width
        self._surface_height = self._terrain.height
    
    @property
    def orbit(self) -> Terrain:
        return self._orbit
    
    @orbit.setter
    def orbit(self, orbit: Orbit) -> None:
        self._orbit = orbit
        

    def get_sample(self, freqs: tuple[float, float], haptic_freq: float, max_r: float) -> float:
        
        """
        GET CURRENT SAMPLE VALUE
        
        Args
        ----
            freqs: tuple[float, float]
                signal x and y frequencies
            haptic_freqs: float
                haptic frequency in Hz. How many times the terrain change in one second
            max_r: float
                max orbit radius [0, 1]
        
        Returns
        -------
            float
                current sample
        """
        
        self.__count_terrain_update += 1
        haptic_sample = int((1 / haptic_freq) * self.sr)
        self._surface = self._surface if self.__count_terrain_update != 0 else self._terrain.generate_terrain()
        
        coords = self._orbit.calculate(phase=self.__phase, freqs=freqs, max_r=max_r)
        x = int(coords[0] * self._terrain.width) % self._terrain.width
        y = int(coords[1] * self._terrain.height) % self._terrain.height
        
        sample = self._surface[y, x]
        sample_out = self.__dcblock(sample=sample)
        
        
        self.__count_terrain_update %= haptic_sample
        self.__phase += 1 / self.sr
        
        return sample_out
    
    
    def __dcblock(self, sample: float) -> float:
        xtemp = sample
        yout = 0
        for i in range(DBLOCK_ORDER):
            yout = xtemp - self.__delayed_samples[0, i] + self.__dcblock_coeff * self.__delayed_samples[1, i]
            self.__delayed_samples[0, i] = xtemp
            self.__delayed_samples[1, i] = yout
            xtemp = yout
        return yout
    