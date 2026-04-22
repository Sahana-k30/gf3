# gf3/adaptive_codec.py
import numpy as np
from gf3.interleaver import interleave, deinterleave

class AdaptiveGF3Codec:

    def select_repetition(self, error_rate):
        # stronger repetition choices to increase tolerance up to ~40% channel errors
        if error_rate <= 0.15:
            return 11
        elif error_rate <= 0.30:
            return 17
        elif error_rate <= 0.40:
            # large repetition for very noisy channels (~40% errors)
            return 101
        else:
            # extreme redundancy when channel is very bad
            return 201

    def __init__(self):
        # self-optimizing hyperparameters
        # increase default effort for hard channels
        self.iterations = 2
        self.damping = 0.35
        self.check_weight = 1.1
        self.max_iterations = 12

        # statistics: map bin -> {'trials', 'failures'}
        self.stats = {}

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

    def decode_min_sum(self, received, R, error_rate):
        """
        Soft min-sum style decoding using negative log-likelihoods per symbol value.
        Treats each repeated observation as an independent noisy observation with
        P(obs==s) = 1-p, P(obs!=s) = p/2 for the two other symbols.
        Returns decoded symbols and average instability (1 - posterior conf).
        """
        received = deinterleave(received, R)
        decoded = []
        instability = []

        p = float(error_rate)
        # avoid zero probabilities
        good = max(1e-12, 1.0 - p)
        bad = max(1e-12, p / 2.0)
        log_good = -np.log(good)
        log_bad = -np.log(bad)

        posteriors = []
        for i in range(0, len(received), R):
            block = received[i:i+R]
            # compute negative log-likelihood (cost) for each candidate symbol 0,1,2
            costs = np.zeros(3, dtype=float)
            for s in range(3):
                # cost: sum_j -log P(obs_j | s)
                # if obs == s -> log_good contribution, else log_bad
                equal = (block == s)
                costs[s] = equal.sum() * log_good + (~equal).sum() * log_bad

            # convert costs to (unnormalized) likelihoods
            lik = np.exp(-costs - costs.max())  # stability trick
            posterior = lik / lik.sum()
            best = int(np.argmax(posterior))

            decoded.append(best)
            posteriors.append(posterior)
            instability.append(1.0 - float(posterior[best]))

        return decoded, float(np.mean(instability)), posteriors
    
    def decode_iterative(self, received, R, error_rate):
        """
        Iterative decoding wrapper that runs multiple min-sum passes, applies
        damping and a simple reinforcement adaptation. Chooses the best decoding
        based on lowest average instability.
        """
        best_decoded = None
        best_inst = 1.0

        # run multiple trials (simulate iterations)
        for it in range(max(1, self.iterations)):
            decoded, inst, post = self.decode_min_sum(received, R, error_rate)

            # apply a simple damping "smoothing" on posterior (ad-hoc)
            if self.damping > 0 and it > 0:
                # nudge decoded choice towards previous using check_weight
                for i in range(len(decoded)):
                    if np.random.rand() < self.damping * 0.5 * self.check_weight:
                        # randomly flip to reduce overconfidence (exploration)
                        decoded[i] = (decoded[i] + np.random.randint(1, 3)) % 3

            if inst < best_inst:
                best_inst = inst
                best_decoded = decoded[:]

        return best_decoded, float(best_inst)

    def record_result(self, error_rate, success: bool):
        """Record whether a decoding succeeded at given error rate and adapt params."""
        bin_key = round(error_rate, 2)
        s = self.stats.setdefault(bin_key, {'trials': 0, 'failures': 0})
        s['trials'] += 1
        if not success:
            s['failures'] += 1

        # Adjust parameters every 10 trials in this bin
        if s['trials'] >= 10:
            fail_rate = s['failures'] / s['trials']
            self._adjust_params(fail_rate)
            # reset stats for next window
            s['trials'] = 0
            s['failures'] = 0
        # log event to disk for later analysis
        try:
            import os, json, time
            os.makedirs('logs', exist_ok=True)
            entry = {
                'ts': time.time(),
                'bin': bin_key,
                'success': bool(success),
                'iterations': self.iterations,
                'damping': self.damping,
                'check_weight': self.check_weight
            }
            with open(os.path.join('logs', 'codec_events.jsonl'), 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception:
            pass

    def _adjust_params(self, fail_rate: float):
        """Simple reinforcement rule to increase effort on failure and reduce on success."""
        if fail_rate > 0.2:
            # increase iterations/damping/check_weight up to caps
            self.iterations = min(self.max_iterations, self.iterations + 1)
            self.damping = min(0.95, self.damping + 0.05)
            self.check_weight = min(2.0, self.check_weight + 0.1)
        else:
            # slowly decay complexity
            self.iterations = max(1, self.iterations - 1)
            self.damping = max(0.05, self.damping - 0.02)
            self.check_weight = max(0.5, self.check_weight - 0.05)