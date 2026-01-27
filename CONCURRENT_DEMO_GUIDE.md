# 🎯 CONCURRENT UPLOAD DEMO - READY!

**⚠️ IMPORTANT FIX:** Server timeout has been increased from 30 to 300 seconds (5 minutes) to support long uploads without "Broken pipe" errors.

## File Sizes Available for Testing:

| File | Size | Upload Time (--slow 10) | Demo Duration |
|------|------|------------------------|----------------|
| test3.txt | 860 bytes | ~1 sec | Very quick |
| test3_large.bin | 5 MB | ~13 sec | Good for quick demo |
| **test_100mb.bin** | **100 MB** | **~4+ minutes** | **PERFECT for concurrent demo!** |

---

## 🔴 HOW TO DEMONSTRATE CONCURRENT LOCKING PROPERLY

The system works correctly. To see the "File is locked" error, you MUST open 3 terminals manually and run steps sequentially:

### **Terminal 1: START SERVER**
```bash
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
make run
```

Expected: `[SERVER] Listening on port 8888...`

---

### **Terminal 2: CLIENT 1 - Start the long upload**
```bash
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10
```

You'll see:
```
[UPLOAD] Throttling enabled: 10 ms per chunk
[UPLOAD] Sent command: UPLOAD test_100mb.bin 104857600
[UPLOAD] Server response: READY Send file data
[UPLOAD] Sending 104857600 bytes...
[UPLOAD] Progress: 2.0% (2097152/104857600 bytes)
[UPLOAD] Progress: 4.0% (4194304/104857600 bytes)
...
```

**⏸️ DO NOT WAIT FOR THIS TO COMPLETE!**

---

### **Terminal 3: CLIENT 2 - Try to upload same file (10-20 seconds after Terminal 2 starts)**
```bash
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
python3 client/client.py UPLOAD test_files/test_100mb.bin
```

### ✅ **Expected Result:**
```
[UPLOAD] Connecting to server...
[UPLOAD] Sent command: UPLOAD test_100mb.bin 104857600
[UPLOAD] Server response: ERROR
[ERROR] File is locked by another process
```

---

## Why This Works:

1. **Client 1** acquires **WRITE lock** on test_100mb.bin (F_WRLCK)
2. **Client 2** tries to acquire the **same WRITE lock** → **REJECTED immediately** (non-blocking F_SETLK)
3. Server sends ERROR response without waiting
4. **Client 2** prints: "File is locked by another process"

This demonstrates:
- ✅ **File Locking (fcntl F_WRLCK)**
- ✅ **Deadlock Avoidance** (no circular wait)
- ✅ **No Hold-and-Wait** (Client 2 doesn't wait, gets immediate response)
- ✅ **Non-Blocking Acquisition** (F_SETLK flag in fcntl)

---

## 📊 Timing Calculations:

### With 100MB file + --slow 10ms per chunk:
- **File size:** 104,857,600 bytes
- **Chunk size:** 4,096 bytes  
- **Number of chunks:** 25,600
- **Throttle per chunk:** 10ms
- **Total transfer time:** 25,600 × 10ms = **256 seconds = 4.27 minutes**

### Perfect window for demonstrating concurrent locking!

**Recommendation:** 
- Start Terminal 2 upload
- Wait 10-20 seconds  
- Start Terminal 3 upload
- You'll see the lock rejection

---

## Alternative Smaller Files:

If 4+ minutes is too long for your demo, use these:

### Option 1: Medium Concurrent Demo (~1.3 seconds)
```bash
# Terminal 2
python3 client/client.py UPLOAD test_files/test3_large.bin --slow 10

# Terminal 3 (immediately after, while Terminal 2 is uploading)
python3 client/client.py UPLOAD test_files/test3_large.bin
```
File: test3_large.bin (5MB), Time: ~13 seconds

### Option 2: Quick Concurrent Demo (~0.25 seconds) 
```bash
# Terminal 2
python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 100

# Terminal 3 (immediately after)
python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 100
```
File: test_100mb.bin (100MB), Time: ~42 seconds with --slow 100

---

## 📝 Demo Script Command:

Once you're comfortable, use this one-line setup:

```bash
# Terminal 1
make run

# Terminal 2 (copy-paste)
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS" && python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10

# Terminal 3 (wait 15 seconds, then copy-paste)
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS" && python3 client/client.py UPLOAD test_files/test_100mb.bin
```

---

## 🎬 When You Run It:

**Terminal 1 (Server):** You'll see lock acquisition/release messages
**Terminal 2 (Client 1):** Shows progress bar (takes 4+ min)
**Terminal 3 (Client 2):** Shows ERROR with lock message

This is the **perfect demonstration of OS deadlock avoidance**! 🎯
