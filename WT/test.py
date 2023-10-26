# import section
from wave_terrain import WaveTerrainSynthesis
from orbits import OrbitTypes, Orbit
from envelopes import EnvelopeTypes, Envelope
from terrain import Terrain
import numpy as np
import soundfile as sf

# main scripts
WIDTH, HEIGHT = 512, 512
DUR = 2
SR = 44100
SAMPLE_DUR = int(DUR * SR)

ENVELOPE_DUR = 0.1

FREQX = 9000
FREQY = 125

HAPTIC_FREQ = 3

# main function
def main() -> None:
    terrain = Terrain(size=(WIDTH, HEIGHT), xy_incr=(0.01, 0.01))
    
    envelope = Envelope(
        envelope_type=EnvelopeTypes.ADSR, 
        dur=ENVELOPE_DUR,
        sr=SR,
        atk=0.001, 
        decay=0, 
        release=ENVELOPE_DUR - 0.001, 
        sustain_amp=1.0, 
        initial_amp=0.0001, 
        end_amp=0.0001, 
        mode="exp"
    )
    
    # envelope.show_env()
    # return 
    
    orbit = Orbit(orbit_type=OrbitTypes.SPIRAL, center=(0.5, 0.5))
    orbit.envelope = envelope
    
    # orbit.show_orbit(period=1 / SR)
    
    wt = WaveTerrainSynthesis(sr=SR)
    wt.terrain = terrain
    wt.orbit = orbit
    
    y = np.zeros(SAMPLE_DUR, dtype=np.float64)
    for i in range(SAMPLE_DUR):
        sample = wt.get_sample(freqs=(FREQX, FREQY), haptic_freq=HAPTIC_FREQ, max_r=0.707)
        y[i] = sample
    
    # master envelope
    y *= np.hanning(SAMPLE_DUR)
    
    sf.write("wt.wav", y, SR, "PCM_16")


# [MAIN PROGRAM]: if the module is being run as the main program, it calls the "main()" function
if __name__ == "__main__":
    main()