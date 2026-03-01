# GF(3) LDPC - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Backend
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Open the Frontend
Open your browser and go to:
```
http://localhost:8000
```

---

## 💻 Quick Usage

1. **Enter a message** (e.g., "test", "hello")
2. **Set error rate** (try 0.15 for 15% errors)
3. **Click "Start Full Process"**
4. **See the magic happen!** 🎉

---

## 🔌 API Endpoints (For Developers)

### Get System Info
```bash
curl http://localhost:8000/api/info
```

### Full Process for short message
(Encode → Corrupt → Decode) – single block
```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "error_probability": 0.15}'
```

### Send long message
Supports messages of any length; backend chunks automatically.
```bash
curl -X POST http://localhost:8000/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "hello world this is long", "error_probability": 0.15}'
```
### Just Encode
```bash
curl -X POST http://localhost:8000/api/encode \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

---

## 📊 Understanding the Output

**Original Message**: Your input text

**Encoded (GF3)**: Numbers in {0, 1, 2}
- Example: [1, 0, 2, 0, 1, 1, 2]

**Corrupted by Noise**: Errors added by simulation

**Decoded Message**: Recovered after error correction

**Error Analysis**:
- ✅ **Success**: Original == Decoded
- ⚠️ **Partial**: Errors detected but not fully corrected
- ❌ **Failed**: Errors not detected

---

## 🎓 Key Concepts

### GF(3) = Galois Field with 3 elements
- Elements: {0, 1, 2}
- All math is modulo 3
- 1 + 2 = 0 (in GF(3))

### LDPC = Low-Density Parity-Check
- Sparse matrix structure
- Great error correction performance
- Used in modern 5G networks

### Encoding
```
Message (4 symbols) → Multiply × Generator Matrix → Codeword (7 symbols)
```

### Decoding
```
Corrupted Codeword → Calculate Syndrome → Find Errors → Correct → Original Message
```

---

## 🧪 Try These Examples

### Low Noise (High Success Rate)
- Message: "test"
- Error Rate: 0.05 (5%)
- Expected: ✅ Nearly always successful

### Medium Noise (Mixed Results)
- Message: "gf3"
- Error Rate: 0.20 (20%)
- Expected: ⚠️ Sometimes successful

### High Noise (Low Success Rate)
- Message: "hi"
- Error Rate: 0.40 (40%)
- Expected: ❌ Often fails

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | Kill process or use different port |
| Module not found | Run `pip install -r requirements.txt` |
| Frontend not loading | Check backend is running on port 8000 |
| CORS errors | Already configured in main.py |

---

## 📁 Project Files

- **gf3_ldpc.py** - Core encoder/decoder logic
- **main.py** - FastAPI backend server
- **index.html** - Web interface
- **requirements.txt** - Python dependencies
- **README.md** - Full documentation

---

## 📚 Want to Learn More?

1. Read the **README.md** for detailed explanation
2. Study **gf3_ldpc.py** code (well-commented)
3. Check **main.py** for API integration
4. Modify parameters and experiment!

---

## ⚡ Performance Tips

- Smaller error rate = Faster success
- Larger blocks = Better error correction
- Use /api/process for full pipeline

---

**Happy error correcting! 🔐**
