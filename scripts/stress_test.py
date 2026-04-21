"""Stress test script for the GF3 pipeline.

This script calls `api.routes.send_message` directly (no HTTP) many times
across error-rate bins to stimulate the self-optimizing codec and then
prints codec status and recent log summary.

Usage:
    python scripts/stress_test.py
"""
import time
import random
import importlib

routes = importlib.import_module('api.routes')
codec = routes._GLOBAL_CODEC

def run_trials(trials_per_bin=30, bins=None):
    if bins is None:
        bins = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]

    print('Starting stress test: bins=', bins, 'trials/bin=', trials_per_bin)
    start = time.time()
    for b in bins:
        for i in range(trials_per_bin):
            msg = f'stress-{b}-{i}-{random.randint(0,10000)}'
            try:
                routes.send_message({'message': msg, 'error_rate': b})
            except Exception as e:
                # should not happen; print for debugging
                print('send error', e)
        # brief pause between bins
        time.sleep(0.05)
        print(f'Completed bin {b} — codec params: it={codec.iterations} damp={codec.damping:.3f} weight={codec.check_weight:.3f}')

    dur = time.time() - start
    print('Stress test finished in', round(dur,2), 's')

    # show final codec status
    print('Final codec status:', importlib.import_module('api.routes')._GLOBAL_CODEC.__dict__)

    # show last 10 log entries
    import os, json
    path = os.path.join('logs', 'codec_events.jsonl')
    if os.path.exists(path):
        lines = open(path, 'r', encoding='utf-8').read().splitlines()
        last = lines[-10:]
        print('\nLast log entries:')
        for ln in last:
            try:
                print(json.dumps(json.loads(ln), indent=2))
            except Exception:
                print(ln)

if __name__ == '__main__':
    run_trials()
