# GF3 Adaptive Redundancy Messaging Demo

This project demonstrates a fault-tolerant messaging pipeline that uses GF(3) symbol encoding, adaptive redundancy, soft iterative decoding, CRC validation, encryption, and a semantic fallback display layer. It is intended as an educational/demo system and a testbed for exploring redundancy vs. channel noise trade-offs.

**Core idea**: convert bytes → GF(3) symbols → add adaptive repetition/interleaving → simulate noisy channel → perform soft iterative decoding → decrypt + CRC → present decoded text (or semantic summary when confidence is low).

**Quick status**: runs as a FastAPI backend with a small frontend and an included stress test harness.

**Contents**
- **Features**: lists implemented capabilities and tunable parameters
- **Architecture & flow**: how data moves through the pipeline
- **How to run**: setup and common commands
- **API**: endpoints exposed by the backend
- **Developer notes**: important files, tuning knobs, and tests
- **Contributing & License**

**Features**
- **Adaptive redundancy**: `AdaptiveGF3Codec` selects repetition depths and runs soft iterative decoding to maximize recovery.
- **High-redundancy modes**: supports very large repetition depths (e.g., 101, 201) for very noisy channels (~40%+ error rates).
- **Soft decoding**: likelihood-based min-sum style decoding and iterative selection with damping and reinforcement.
- **Interleaving**: simple block interleaver/deinterleaver to scatter burst errors.
- **CRC + symmetric encryption**: messages are protected with a CRC and encrypted before GF(3) conversion so decoding correctness is verified end-to-end.
- **Semantic fallback**: when confidence is low, the system extracts and displays semantic summary rather than raw (possibly corrupted) text.
- **Runtime telemetry**: codec adapts parameters and logs events to `logs/codec_events.jsonl` for analysis.

**Architecture & Flow**

1. Client sends a plaintext message and requested `error_rate` (simulated channel noise).
2. Server appends a CRC and encrypts the bytes.
3. Each encrypted byte is converted to six base-3 symbols (trits).
4. `AdaptiveGF3Codec.encode()` applies repetition (R) and interleaves the symbols.
5. Channel noise is simulated with `add_noise()` using the requested error probability.
6. `AdaptiveGF3Codec.decode_iterative()` performs soft decoding (min-sum style), runs multiple iterations, and returns decoded symbols with an instability/confidence score.
7. Symbols → bytes → decrypt → CRC check. If CRC passes, the message is trusted; otherwise, semantic extraction may be used to display high-level info.

**How to run (developer)**

- Create and activate a Python virtual environment (Windows PowerShell example):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Start the server:

```powershell
python main.py
```

- Run the stress test (exercise adaptive learning):

```powershell
python scripts\stress_test.py
```

Or use the provided `run.bat` / `run.ps1` helper scripts.

**API summary**

- POST `/api/send` — full pipeline (preferred).
  - Request JSON: `{ "message": "...", "error_rate": 0.15 }`
  - Response fields: `original`, `display`, `decoded`, `crc_status`, `confidence`, `adaptive_level`.

- GET `/api/error-graph` — runs the pipeline across error-rate bins and returns accuracy per bin (useful for plotting).

- GET `/api/server-messages` — recent decoded messages stored for the server UI.

- POST `/api/server-messages/clear` — clear stored server messages.

- GET `/api/codec/status` — current adaptive codec parameters (`iterations`, `damping`, `check_weight`).

- GET `/api/codec/logs` — recent codec events read from `logs/codec_events.jsonl`.

For quick experimentation you can curl or use Python `requests` against the running server.

**Important files (developer map)**
- `api/routes.py` — HTTP endpoints and the high-level pipeline orchestration.
- `gf3/adaptive_codec.py` — adaptive codec, repetition selection, soft decoding, and parameter adaptation.
- `gf3/codec.py` — baseline repetition codec implementations and helpers.
- `gf3/interleaver.py` — interleave/deinterleave utilities.
- `gf3/crypto.py` — symmetric encrypt/decrypt helpers used around the channel.
- `gf3/crc.py` — CRC append/check helpers.
- `gf3/utils.py` — misc helpers for converting messages to/from GF(3) symbols.
- `semantic/semantic_extractor.py` — simple semantic extraction and summarization used when confidence is low.
- `scripts/stress_test.py` — automated tester that drives the codec across bins and triggers adaptation.

**Tuning & notes**
- Repetition choices in `AdaptiveGF3Codec.select_repetition()` include small (11), medium (17), and very large values (101, 201). Larger R increases fault tolerance at the cost of bandwidth.
- Decoder parameters in `AdaptiveGF3Codec` to tune:
  - `iterations` (integer): number of decoding trials/passes
  - `damping` (0.0–1.0): controls posterior smoothing and exploration
  - `check_weight` (float): controls random flips/nudges during iterative decoding
  - `max_iterations` (cap for `iterations`)
- The codec records per-bin success/failure and adjusts these parameters automatically every ~10 trials per bin.

**Testing & validation**
- Use `scripts/stress_test.py` to run many trials across error-rate bins; it will print codec parameter evolution and tail logs.
- Use `/api/error-graph` to produce a quick accuracy vs. error-rate curve for a sample message.

**Development tips**
- To add a new decoding strategy, implement it in `gf3/adaptive_codec.py` as a method returning `(decoded_symbols, instability_score)` and swap it into `decode_iterative()`.
- If experimenting with different interleavers, update `gf3/interleaver.py` and ensure `encode()`/`decode()` use the same depth.

**Contributing**
- Fork, create a feature branch, and submit a pull request. Describe the change and why it helps tolerance/performance.

**License**
- Educational / permissive. Reuse and adapt freely; attribute improvements back to the repository if you can.

---

If you want, I can:
- add a short example script showing how to call `/api/send` from Python, or
- run the stress test and summarize accuracy at 40% error rate.

Happy to continue — tell me which you'd like next.
