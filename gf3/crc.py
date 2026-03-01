def crc8(data: bytes, poly=0x07):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ poly) if crc & 0x80 else (crc << 1)
            crc &= 0xFF
    return crc

def append_crc(msg: str):
    b = msg.encode()
    return b + bytes([crc8(b)])

def check_crc(b: bytes):
    return crc8(b[:-1]) == b[-1]