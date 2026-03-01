# gf3/codec.py
import numpy as np
from gf3.interleaver import interleave, deinterleave

class GF3Repetition11:
    REPEAT = 11

    def encode(self, symbols):
        encoded = []
        for s in symbols:
            encoded.extend([s] * self.REPEAT)
        return interleave(np.array(encoded), self.REPEAT)

    def add_noise(self, codeword, error_rate):
        noisy = codeword.copy()
        for i in range(len(noisy)):
            if np.random.rand() < error_rate:
                noisy[i] = (noisy[i] + np.random.randint(1, 3)) % 3
        return noisy

    def decode(self, received):
        received = deinterleave(received, self.REPEAT)
        decoded = []
        for i in range(0, len(received), self.REPEAT):
            block = received[i:i + self.REPEAT]
            decoded.append(int(np.bincount(block, minlength=3).argmax()))
        return decoded