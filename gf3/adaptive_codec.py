# gf3/adaptive_codec.py
import numpy as np
from gf3.interleaver import interleave, deinterleave

class AdaptiveGF3Codec:

    def select_repetition(self, error_rate):
        if error_rate <= 0.15:
            return 11
        elif error_rate <= 0.30:
            return 17
        elif error_rate <= 0.45:
            return 25
        else:
            return 31

    def encode(self, symbols, error_rate):
        R = self.select_repetition(error_rate)
        encoded = []
        for s in symbols:
            encoded.extend([s] * R)
        return interleave(np.array(encoded), R), R

    def add_noise(self, codeword, error_rate):
        noisy = codeword.copy()
        for i in range(len(noisy)):
            if np.random.rand() < error_rate:
                noisy[i] = (noisy[i] + np.random.randint(1, 3)) % 3
        return noisy

    def decode(self, received, R):
        received = deinterleave(received, R)
        decoded = []
        instability = []

        for i in range(0, len(received), R):
            block = received[i:i+R]
            counts = np.bincount(block, minlength=3)
            decoded.append(int(np.argmax(counts)))
            instability.append(1 - counts.max() / R)

        return decoded, float(np.mean(instability))