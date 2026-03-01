# gf3/utils.py

def message_to_gf3(message: str):
    symbols = []
    for ch in message:
        v = ord(ch)
        for _ in range(6):   # 6 trits per character (safe for ASCII)
            symbols.append(v % 3)
            v //= 3
    return symbols


def gf3_to_message(symbols):
    chars = []
    for i in range(0, len(symbols), 6):
        value = 0
        power = 1
        for s in symbols[i:i+6]:
            value += s * power
            power *= 3
        chars.append(chr(value))
    return "".join(chars)