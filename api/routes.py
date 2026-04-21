from fastapi import APIRouter
import numpy as np

from semantic.semantic_extractor import extract_semantics, semantic_summary
from gf3.utils import message_to_gf3
from gf3.crypto import encrypt_bytes, decrypt_bytes
from gf3.crc import append_crc, check_crc
from gf3.interleaver import interleave, deinterleave
from gf3.adaptive_codec import AdaptiveGF3Codec

# persistent codec instance so it can learn across requests
_GLOBAL_CODEC = AdaptiveGF3Codec()

router = APIRouter()

# In-memory store for messages received by the server UI
SERVER_MESSAGES = []


# -----------------------------------------
# Adaptive repetition (PRE-decoding)
# -----------------------------------------
def select_repetition(error_rate):
    if error_rate <= 0.15:
        return 11
    elif error_rate <= 0.30:
        return 17
    elif error_rate <= 0.45:
        return 25
    else:
        return 31


# -----------------------------------------
# SEND (Adaptive + Semantic-aware)
# -----------------------------------------
@router.post("/send")
def send_message(data: dict):
    message = data.get("message", "")
    error_rate = float(data.get("error_rate", 0.1))

    # 1️⃣ CRC append + encryption
    message_crc = append_crc(message)  # bytes
    encrypted = encrypt_bytes(message_crc)

    # 2️⃣ Encrypted bytes → GF(3) symbols
    symbols = []
    for b in encrypted:
        v = int(b)
        for _ in range(6):
            symbols.append(v % 3)
            v //= 3

    # 3️⃣ Adaptive redundancy + soft iterative decoding
    coder = _GLOBAL_CODEC
    encoded, R = coder.encode(symbols, error_rate)

    # 4️⃣ Add noise (channel)
    noisy = coder.add_noise(encoded, error_rate)

    # 5️⃣ Iterative soft decode (self-optimizing)
    decoded_symbols, avg_instability = coder.decode_iterative(noisy, R, error_rate)

    # 6️⃣ GF(3) → bytes (this should be the encrypted ciphertext)
    decoded_bytes = bytearray()
    for i in range(0, len(decoded_symbols), 6):
        val, power = 0, 1
        for s in decoded_symbols[i:i + 6]:
            val += s * power
            power *= 3
        # ensure byte range
        decoded_bytes.append(int(val % 256))

    # 7️⃣ Decrypt then CRC check
    try:
        decrypted = decrypt_bytes(bytes(decoded_bytes))
        crc_ok = check_crc(decrypted)
        decoded_msg = decrypted[:-1].decode("utf-8", errors="replace")
    except Exception:
        crc_ok = False
        decoded_msg = ""

    # 8️⃣ Confidence
    confidence = max(0.0, 1.0 - avg_instability)
    if not crc_ok:
        confidence = min(confidence, 0.5)

    # -----------------------------------------
    # 9️⃣ SEMANTIC-AWARE DECISION LAYER
    # -----------------------------------------
    if confidence >= 0.7:
        mode = "FULL"
        display_text = decoded_msg

    elif confidence >= 0.4:
        mode = "PARTIAL"
        display_text = decoded_msg + "\n\n⚠️ Some errors may be present."

    else:
        mode = "SEMANTIC"
        entities = extract_semantics(decoded_msg)
        display_text = semantic_summary(entities)

    # -----------------------------------------
    # Store message for server-side UI
    # -----------------------------------------
    msg_record = {
        "original": message,
        "display": display_text,
        "decoded": decoded_msg,
        "crc_status": "PASS" if crc_ok else "FAIL",
        "confidence": round(confidence, 3),
        "adaptive_level": f"Repeat-{R}"
    }

    # keep only recent 200 messages
    SERVER_MESSAGES.append(msg_record)
    if len(SERVER_MESSAGES) > 200:
        del SERVER_MESSAGES[0]

    # record result so codec can adapt
    try:
        coder.record_result(error_rate, crc_ok)
    except Exception:
        pass

    # Final response
    return msg_record


# -----------------------------------------
# GRAPH (STATIC, STABLE)
# -----------------------------------------
@router.get("/error-graph")
def error_graph(message: str):
    coder = AdaptiveGF3Codec()
    symbols = message_to_gf3(message)
    # Build encrypted-symbols pipeline for the graph
    # append CRC and encrypt once per test to emulate real flow
    msg_crc = append_crc(message)

    results = []
    for p in range(0, 51, 5):
        prob = p / 100
        encrypted = encrypt_bytes(msg_crc)

        # convert encrypted bytes to symbols
        sym = []
        for b in encrypted:
            v = int(b)
            for _ in range(6):
                sym.append(v % 3)
                v //= 3

        encoded, R = coder.encode(sym, prob)
        corrupted = coder.add_noise(encoded, prob)
        decoded, _ = coder.decode_iterative(corrupted, R, prob)

        # recover bytes from decoded trits
        decoded_bytes = bytearray()
        for i in range(0, len(decoded), 6):
            val, power = 0, 1
            for s in decoded[i:i + 6]:
                val += s * power
                power *= 3
            decoded_bytes.append(int(val % 256))

        try:
            plain = decrypt_bytes(bytes(decoded_bytes))
            # compare original plaintext bytes (without crc) for accuracy
            acc = 1.0 if plain[:-1] == message.encode() else 0.0
        except Exception:
            acc = 0.0

        results.append({"error_rate": prob, "accuracy": float(acc)})

    return results


# -----------------------------------------
# Server UI endpoints
# -----------------------------------------
@router.get("/server-messages")
def server_messages(limit: int = 50):
    # return the most recent `limit` messages (default 50)
    return list(reversed(SERVER_MESSAGES[-limit:]))


@router.post("/server-messages/clear")
def clear_server_messages():
    """Clear all stored server messages."""
    SERVER_MESSAGES.clear()
    return {"status": "ok", "cleared": True}


@router.get('/codec/status')
def codec_status():
    c = _GLOBAL_CODEC
    return {
        'iterations': c.iterations,
        'damping': c.damping,
        'check_weight': c.check_weight,
        'stats_bins': list(c.stats.keys())
    }


@router.get('/codec/logs')
def codec_logs(limit: int = 200):
    """Return the most recent codec log lines (JSON) from logs/codec_events.jsonl"""
    import os, json
    path = os.path.join('logs', 'codec_events.jsonl')
    if not os.path.exists(path):
        return []
    lines = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for ln in f:
                try:
                    lines.append(json.loads(ln))
                except Exception:
                    continue
    except Exception:
        return []

    return lines[-limit:]