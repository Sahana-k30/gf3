from fastapi import APIRouter
import numpy as np

from semantic.semantic_extractor import extract_semantics, semantic_summary
from gf3.utils import message_to_gf3
from gf3.crc import append_crc, check_crc
from gf3.interleaver import interleave, deinterleave
from gf3.codec import GF3Repetition11

router = APIRouter()


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

    # 1️⃣ CRC append
    message_crc = append_crc(message)

    # 2️⃣ Bytes → GF(3)
    symbols = []
    for b in message_crc:
        v = b
        for _ in range(6):
            symbols.append(v % 3)
            v //= 3

    # 3️⃣ Adaptive redundancy
    R = select_repetition(error_rate)

    encoded = []
    for s in symbols:
        encoded.extend([s] * R)
    encoded = interleave(np.array(encoded), R)

    # 4️⃣ Add noise
    noisy = encoded.copy()
    for i in range(len(noisy)):
        if np.random.rand() < error_rate:
            noisy[i] = (noisy[i] + np.random.randint(1, 3)) % 3

    # 5️⃣ Decode
    noisy = deinterleave(noisy, R)
    decoded_symbols = []
    instability = []

    for i in range(0, len(noisy), R):
        block = noisy[i:i + R]
        counts = np.bincount(block, minlength=3)
        decoded_symbols.append(int(np.argmax(counts)))
        instability.append(1 - counts.max() / R)

    avg_instability = float(np.mean(instability))

    # 6️⃣ GF(3) → bytes
    decoded_bytes = bytearray()
    for i in range(0, len(decoded_symbols), 6):
        val, power = 0, 1
        for s in decoded_symbols[i:i + 6]:
            val += s * power
            power *= 3
        decoded_bytes.append(val)

    # 7️⃣ CRC check
    crc_ok = check_crc(bytes(decoded_bytes))
    decoded_msg = decoded_bytes[:-1].decode("utf-8", errors="replace")

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
    # FINAL RESPONSE (ONLY ONE RETURN)
    # -----------------------------------------
    return {
        "mode": mode,
        "display": display_text,
        "decoded": decoded_msg,
        "crc_status": "PASS" if crc_ok else "FAIL",
        "confidence": round(confidence, 3),
        "adaptive_level": f"Repeat-{R}"
    }


# -----------------------------------------
# GRAPH (STATIC, STABLE)
# -----------------------------------------
@router.get("/error-graph")
def error_graph(message: str):
    coder = GF3Repetition11()
    symbols = message_to_gf3(message)
    encoded = coder.encode(symbols)

    results = []
    for p in range(0, 51, 5):
        prob = p / 100
        corrupted = coder.add_noise(encoded, prob)
        decoded = coder.decode(corrupted)

        acc = np.mean(np.array(symbols) == np.array(decoded))
        results.append({
            "error_rate": prob,
            "accuracy": float(acc)
        })

    return results