# GF(3) LDPC Error Correction System

A complete implementation of Galois Field (3) Low-Density Parity-Check (LDPC) codes for error detection and correction in digital communications. Supports messages of arbitrary length by internally chunking into 4-symbol blocks.

## 📚 What is GF(3) LDPC?

### Galois Field GF(3)
- A finite field with exactly 3 elements: **{0, 1, 2}**
- All arithmetic operations (addition, multiplication) are performed modulo 3
- Provides theoretical foundation for error-correcting codes

### LDPC (Low-Density Parity-Check) Codes
- Linear block codes characterized by a sparse parity-check matrix
- Excellent error correction performance
- Used in modern communication standards (WiFi, 5G, satellite communications)

### How It Works
1. **Encoding**: Message is multiplied by generator matrix in GF(3) to produce redundancy
2. **Transmission**: Codeword travels through noisy channel
3. **Corruption**: Random errors occur due to channel noise
4. **Decoding**: Receiver uses syndrome-based detection to find and correct errors
5. **Verification**: Original message is recovered

## 🏗️ System Architecture

```
Frontend (HTML)
    ↓ (HTTP/REST)
FastAPI Backend
    ↓
GF(3) LDPC Engine
    ├── Encoder (message → codeword)
    ├── Noise Simulator
    └── Decoder (codeword → message)
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Navigate to the project directory**:
   ```bash
   cd "C:\Users\admin\Desktop\GF3 demo"
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   # On Windows Command Prompt
   python -m venv venv
   venv\Scripts\activate
   
   # On Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the System

### Start the Backend Server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Access the Frontend

1. **Option A: Open in Browser**
   - Navigate to: `http://localhost:8000` in your web browser
   - Or directly to the frontend file if served locally

2. **Option B: Serve HTML Locally**
   ```bash
   # Using Python's built-in server (in the project directory)
   python -m http.server 8001
   ```
   Then visit: `http://localhost:8001`

## 🎯 How to Use the Demo

1. **Enter a message** (up to 4 characters)
   - Example: "test", "hello", "gf3"

2. **Set error rate** (0.0 - 1.0)
   - 0.15 = 15% chance of error at each bit position
   - Higher values introduce more corruption

3. **Click "Start Full Process"**

4. **Observe the results**:
   - **Original Message**: Your input
   - **Encoded (GF3)**: GF(3) symbols after encoding
   - **Corrupted by Noise**: Message after channel errors
   - **Decoded Message**: Recovered message after error correction
   - **Error Analysis**: Statistics on correction success

## 🔬 Technical Details

### Code Parameters
- **Message length (k)**: 4 information symbols
- **Codeword length (n)**: 7 coded symbols
- **Parity bits (m)**: 3 parity bits
- **Code rate**: 4/7 ≈ 0.57

### GF(3) Arithmetic
```python
Addition (mod 3):     0+1=1, 1+2=0, 2+2=1
Multiplication (mod 3): 1*2=2, 2*2=1
```

### Encoding Process
```
message [m₀, m₁, m₂, m₃] × Generator Matrix G (4×7)
                        ↓
         codeword [c₀, c₁, c₂, c₃, c₄, c₅, c₆]
```

### Decoding Process
```
received codeword × Parity-Check Matrix H (3×7)
                  ↓
             syndrome s
                  ↓
         (if s ≠ 0, errors detected)
                  ↓
         Find error position & correct
                  ↓
         recovered message
```

## 📊 API Endpoints

### GET `/` or `/api/info`
Get system information and status

### POST `/api/encode`
Encode a message
```json
{
  "message": "test",
  "error_probability": 0.15
}
```

### POST `/api/process`
Complete process for a single 4-symbol message block (legacy endpoint). Encodes, corrupts, and decodes one chunk.
```json
{
  "message": "test",
  "error_probability": 0.15
}
```

### POST `/api/send`
Full pipeline capable of handling messages of arbitrary length. The backend will automatically break the message into 4-symbol chunks, process each chunk through GF(3) LDPC, and return combined results.
```json
{
  "message": "this is a longer text message",
  "error_probability": 0.2
}
```
Response includes:
- `original_message`: Input message
- `encoded`: GF(3) encoded codeword
- `corrupted`: After adding noise
- `decoded`: After error correction
- `errors_introduced`: Number of errors added
- `error_corrected`: Whether errors were detected
- `success`: Overall correction success

## 🧪 Example Usage

### Via Web Frontend
1. Enter "test" as message
2. Set error rate to 0.20 (20%)
3. Click "Start Full Process"
4. System will:
   - Encode "test" to 7 GF(3) symbols
   - Add ~1-2 random errors
   - Decode and correct errors
   - Display results

### Via Python (Direct API Call)
```python
import requests

response = requests.post(
    'http://localhost:8000/api/process',
    json={
        'message': 'hello',
        'error_probability': 0.15
    }
)

result = response.json()
print(f"Errors introduced: {result['errors_introduced']}")
print(f"Correction successful: {result['success']}")
```

## 📈 Performance Characteristics

| Metric | Value |
|--------|-------|
| Code Type | Linear Block LDPC |
| Field | GF(3) |
| Block Length (n) | 7 |
| Information Length (k) | 4 |
| Parity Bits (m) | 3 |
| Code Rate (k/n) | 0.571 |
| Error Correction Capability | Up to 1-2 errors per block |

## 🔧 Customization

### Change Code Parameters
Edit `gf3_ldpc.py`:
```python
ldpc = GF3LDPC(message_length=6, codeword_length=10)  # Customize dimensions
```

### Modify Parity-Check Matrix
In `GF3LDPC._create_parity_check_matrix()`:
```python
# Define your own H matrix
H = np.array([
    [1, 0, 1, ...],
    [0, 1, 0, ...],
    ...
])
```

### Adjust Error Correction Algorithm
Replace `decode_simple()` with `decode_iterative()` for advanced decoding.

## 🐛 Troubleshooting

### "Connection refused" error
- Ensure backend is running: `python main.py`
- Check if port 8000 is not in use: `netstat -an | findstr 8000`

### CORS errors
- Frontend must be on same origin or CORS is enabled (already configured)
- Check browser console (F12) for detailed error messages

### Low correction success rate
- Reduce error probability (lower noise level)
- Or increase code block length for better performance

## 📚 References

- **LDPC Codes**: D. J. C. MacKay, "Information Theory, Inference, and Learning Algorithms"
- **Galois Fields**: R. J. McEliece, "Finite Fields for Computer Scientists and Engineers"
- **Error Correction**: E. Huffman & V. Pless, "Fundamentals of Error-Correcting Codes"

## 💡 Why FastAPI over Flask?

| Aspect | FastAPI | Flask |
|--------|---------|-------|
| Speed | ⚡ Native async/await | Sequential |
| Validation | ✅ Automatic (Pydantic) | Manual |
| Documentation | 🔍 Auto-generated (Swagger) | Manual |
| Learning Curve | Easy | Easier |
| Performance | ~2-3x faster | Baseline |
| Modern Stack | Python 3.7+ focused | General purpose |

**Choice**: FastAPI provides better performance, cleaner code, and automatic API docs - ideal for this project.

## 📝 Project Structure

```
GF3 demo/
├── main.py              # FastAPI backend
├── gf3_ldpc.py         # LDPC encoder/decoder
├── index.html          # Web frontend
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🎓 Learning Path

1. Start with the frontend's visual demo
2. Read through `gf3_ldpc.py` to understand encoding/decoding
3. Explore `main.py` to see API integration
4. Experiment with different error rates
5. Customize the code for your use case

## 📄 License

Educational Project - Free to use and modify

## ✨ Features Implemented

- ✅ GF(3) arithmetic operations
- ✅ LDPC encoder with generator matrix
- ✅ LDPC decoder with syndrome calculation
- ✅ Iterative and simple decoding algorithms
- ✅ Channel noise simulation
- ✅ Error detection and correction
- ✅ FastAPI REST backend
- ✅ Interactive web frontend
- ✅ Real-time visual feedback
- ✅ Comprehensive API documentation

---

**Ready to explore error correction? Run `python main.py` and open the demo! 🚀**
