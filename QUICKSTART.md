# 🚀 QUICK START GUIDE - Complete System with Web Dashboard

## 📋 Prerequisites Check

```bash
# In WSL terminal
gcc --version       # Should show GCC 7+
python3 --version   # Should show Python 3.6+

# Install OpenSSL dev library (one-time only)
sudo apt-get update
sudo apt-get install -y libssl-dev
```

---

## ⚡ Complete Setup & Run

### 🔨 Step 1: Build (One-Time)

```bash
# Open WSL
wsl

# Navigate to project
cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS'

# Build C server
make clean build

# Install Python dependencies
cd api_layer
pip install -r requirements.txt
cd ..
```

**Expected output:**
```
✓ Build directory cleaned
✓ Server built successfully: build/file_server
```

---

## 🖥️ Step 2: Start Services (Need TWO Terminals)

### Terminal 1: C Server

```bash
wsl
cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS/build'
./file_server
```

**Expected:**
```
=== SECURE FILE MANAGEMENT SERVER ===
[SERVER] Listening on port 8888...
```

✅ **Keep this terminal running**

---

### Terminal 2: Flask API

```bash
wsl
export FILE_SERVER_AUTH=os-core-token
cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS/api_layer'
python3 app.py
```

**Expected:**
```
OS FILE SERVER - WEB API LAYER
* Running on http://127.0.0.1:5000
```

✅ **Keep this terminal running**

---

## 🌐 Step 3: Open Dashboard

**Double-click:**
```
C:\Users\S Mohith\Desktop\PROJECTS\3RD SEM\NEW OS\web_dashboard\index.html
```

**Dashboard shows:**
- ✅ C Server Online
- 📊 System Status (files, locks, logs)
- 🔒 Lock Visualization
- 🛡️ Security Alerts
- 📜 Audit Timeline
- 🎓 OS Concepts Reference

✅ **Server is ready when you see "Listening on port 8888"**

---

### Step 3: Run Client (Terminal 2)

```bash
# Interactive mode
python3 client/client.py
```

**Or command-line mode:**

```bash
# Upload a file
python3 client/client.py UPLOAD test_files/test1.txt

# List files
python3 client/client.py LIST

# Download a file
python3 client/client.py DOWNLOAD test1.txt

# View logs
python3 client/client.py LOGS
```

---

## Quick Demo (3 minutes)

```bash
# Upload
python3 client/client.py UPLOAD test_files/test1.txt

# List
python3 client/client.py LIST

# Download
python3 client/client.py DOWNLOAD test1.txt downloaded.txt

# Logs
python3 client/client.py LOGS

# Delete
python3 client/client.py DELETE test1.txt
```

---

## Concurrent Access Demo (Shows Locking)

### Terminal 1: Server
```bash
make run
```

### Terminal 2: Client 1
```bash
# Start upload (this will take a few seconds)
python3 client/client.py UPLOAD test_files/test3.txt
```

### Terminal 3: Client 2 (Run immediately after Terminal 2)
```bash
# Try to upload same file
python3 client/client.py UPLOAD test_files/test3.txt
```

**Expected:** Client 2 gets "ERROR - File is locked by another process"

✅ **This demonstrates file locking and deadlock avoidance!**

---

## Troubleshooting

### "Cannot connect to server"
```bash
# Check if server is running
ps aux | grep file_server

# If not, start it
make run
```

---

### "Address already in use"
```bash
# Kill existing server
killall file_server

# Or
lsof -ti:8888 | xargs kill -9

# Then restart
make run
```

---

### "Permission denied"
```bash
# Make demo scripts executable
chmod +x *.sh

# Ensure directories are writable
chmod 755 storage metadata logs
```

---

## One-Command Full Demo

```bash
# Run automated demo (requires server running)
bash demo_full.sh
```

---

## What to Show During Evaluation

1. ✅ **Server starts** → Shows proper initialization
2. ✅ **Upload works** → Demonstrates file I/O and locking
3. ✅ **List shows files** → Directory traversal
4. ✅ **Download works** → Read locks
5. ✅ **Concurrent access blocked** → File locking in action
6. ✅ **Logs display** → Audit trail
7. ✅ **Server output verbose** → Shows OS operations clearly

---

## Key Points to Mention

- **"Uses only UNIX system calls"** (open, read, write, fcntl)
- **"Bounded file transfers prevent deadlock"** (client sends size)
- **"Non-blocking locks avoid circular wait"** (F_SETLK not F_SETLKW)
- **"Timeout mechanism for recovery"** (30-second upload timeout)
- **"Minimal critical sections"** (lock only during write)
- **"Thread-safe logging"** (mutex for metadata/logs)

---

## Files to Show in Code Walkthrough

1. **server/file_server.c** → Main implementation
   - Line ~200: `handle_upload()` → Shows deadlock prevention
   - Line ~500: `acquire_file_lock()` → Shows non-blocking locks
   - Line ~600: `write_audit_log()` → Shows thread safety

2. **client/client.py** → Client protocol
   - Line ~50: Upload sends size first (bounded transfer)

---

## Emergency Commands

```bash
# Clean everything and restart
make clean-all
make
make run

# Create fresh test files
make test

# Check server logs
cat logs/audit.log

# Check what's in storage
ls -lh storage/
```

---

## Success Checklist ✅

Before demo:
- [ ] Server compiles (`make build`)
- [ ] Server starts (`make run`)
- [ ] Client can connect
- [ ] Upload works
- [ ] Download works
- [ ] Concurrent upload shows lock
- [ ] Logs work
- [ ] You can explain deadlock prevention

---

## Time Estimates

- Setup: **30 seconds**
- Single operation demo: **30 seconds each**
- Concurrent access demo: **2 minutes**
- Full walkthrough: **5 minutes**
- Code explanation: **3-5 minutes**

**Total demo time: ~10 minutes**

---

## Most Important Demo Points

1. **Terminal output is verbose** → Shows everything clearly
2. **Bounded transfer protocol** → Core deadlock prevention
3. **Non-blocking locks** → Deadlock avoidance
4. **Timeout mechanism** → Deadlock recovery
5. **Multiple clients blocked** → Locking in action

**These 5 points cover all major OS concepts!**
