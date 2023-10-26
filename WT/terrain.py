from perlin_noise import PerlinNoise
from numpy.typing import NDArray
import numpy as np


class Terrain():
    def __init__(self, size: tuple[int, int], xy_incr: tuple[float, float] = (0.01, 0.01), octaves: int = 1, seed: int = 0) -> None:
        
        """
        INIT TERRAIN
        
        Args
        ----
            size: tuple[int, int]
                size of terrain
            xy_incr: tuple[float, float]
                x and y increment (perlin noise coordinates, default = (0.01, 0.01))
            octaves: int
                number of octaves (default = 1)
            seed: int
                perlin noise seed (default = 0)
        """
        
        self.width = size[0]
        self.height = size[1]
        self.__xoff = xy_incr[0]
        self.__yoff = xy_incr[1]
        self.__startoff = 0.1
        
        self.pnoise = PerlinNoise(octaves=octaves, seed=seed)
        
    def generate_surface(self) -> NDArray:
        
        """
        GENERATE SURFACE
        
        Returns
        -------
            NDArray
                terrain surface
        """
        
        terrain = np.zeros((self.width, self.height), dtype=np.float64)
        y = self.__startoff
        for i in range(self.height):
            x = 0
            for j in range(self.width):
                terrain[i, j] = self.pnoise([y, x])
                x += self.__xoff
            y += self.__yoff
        return terrain