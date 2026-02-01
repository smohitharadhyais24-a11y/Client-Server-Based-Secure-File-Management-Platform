# 🔥 Client–Server Based Secure File Management Platform using UNIX File System Concepts

**Operating System Concepts Implementation - OS Lab Part-B Project**

**COMPLETE FEATURE SET:** 🆕 Web Dashboard · 🆕 Demo Mode (6 Interactive Demos) · 🆕 Real-time OS Event Streaming · 🆕 Multi-Client Support · 🆕 User-Specific File Isolation · 🆕 Deadlock Analysis Tool

## 📋 Project Overview

A **production-grade, deadlock-free file management system** implementing core UNIX Operating System concepts with a modern web-based observability dashboard:

- ✅ **UNIX File I/O** (open, read, write, close, fcntl, stat, unlink)
- ✅ **File Locking with fcntl()** (F_RDLCK for shared reads, F_WRLCK for exclusive writes)
- ✅ **Readers-Writers Problem** (Multiple readers, exclusive writers)
- ✅ **Deadlock Prevention, Avoidance, and Recovery** (Coffman's 4 conditions analysis)
- ✅ **Multi-threaded Server** (pthread_create, one thread per client)
- ✅ **Thread Synchronization** (pthread_mutex for shared data protection)
- ✅ **TCP Socket-based IPC** (Client-server over network)
- ✅ **User Authentication & Authorization** (Session tokens, role-based access)
- ✅ **User-Specific File Isolation** (storage/user1/, storage/user2/ separate namespaces)
- ✅ **Real-time Audit Logging** (Mutex-protected, thread-safe event stream)
- ✅ **Security Event Tracking** (Auth failures, path traversal detection, access violations)
- ✅ **Web Dashboard** (Live monitoring, file operations, lock visualization)
- ✅ **Interactive Demo Mode** (6 guided demonstrations with explanations)

---

## 🆕 COMPLETE FEATURE SET (February 2026)

### **🎛️ Web Dashboard (Live System Observability)**
Modern, responsive HTML/CSS/JavaScript dashboard at `http://localhost:5000/` featuring:

**System Status Panel:**
- Real-time file count (user-specific)
- Total storage used (formatted: B, KB, MB)
- Active locks count (WRITE and READ)
- Security events counter
- C Server connection status

**File Operations Panel:**
- Upload files (creates FormData, triggers WRITE lock)
- Download files (triggers READ lock)
- Delete files (triggers exclusive lock)
- Current files list with download/delete buttons
- Real-time file list refresh after operations

**OS Audit Timeline:**
- 50 most recent operations with timestamps
- Filter tabs: All, Uploads, Downloads, Deletes, Locks, Failed/Security
- Color-coded rows (success=green, failed=red, locks=yellow)
- 🆕 **Clear History button** (truncates audit log file)
- Sortable and searchable

**Security & Threats:**
- Live security alert panel with severity badges
- Threat level indicator (SECURE/CAUTION/DANGER)
- Failed auth attempts, path traversal, access violations
- Auto-expiring alerts

**Live Lock Status:**
- Shows all active locks with file, type (READ/WRITE), and PID
- Updates every 3 seconds
- Color-coded by lock type

### **🎬 Interactive Demo Mode (NEW!)**
Dedicated demo page at `/demo.html` with **6 interactive demonstrations**:

**Demo 1: Exclusive WRITE Lock** ⭐⭐⭐
- Shows fcntl(F_WRLCK) in action
- One client uploads → lock acquired
- Second client blocked → lock denied
- Real console output with [LOCK] tags

**Demo 2: Shared READ Locks (Readers-Writers)** ⭐⭐⭐
- Multiple clients download same file
- Both acquire [LOCK] READ entries
- Demonstrates shared vs exclusive semantics
- Key OS concept: No reader-writer conflict

**Demo 3: Deadlock Detection & Recovery** ⭐⭐⭐⭐
- Simulates timeout scenario
- Shows [TIMEOUT] detection
- Demonstrates lock release + cleanup
- Recovery mechanism explained live

**Demo 4: Security Violation Detection** ⭐⭐⭐
- Path traversal attempt blocked
- Invalid token rejected
- Security events logged with [SECURITY] tags
- Access control in action

**Demo 5: Concurrent File Operations** ⭐⭐⭐
- 3 concurrent uploads (fileA, fileB, fileC)
- Each has independent lock
- No blocking/contention
- Demonstrates lock granularity

**Demo 6: Deadlock Conditions Analysis (VIVA GOLD)** ⭐⭐⭐⭐⭐
- 🆕 **NEW:** Shows 4 Coffman conditions
- Live checklist showing which conditions are BROKEN
- Explains why system avoids deadlock
- Includes viva answer template
- Perfect for "How is deadlock handled?" questions

**Demo Features:**
- 📚 **Explain Mode toggle** - Safe presentation (no execution)
- 🖥️ **Live OS Event Console** - Real-time terminal output
- 🔐 **Active Locks panel** - Live lock visualization
- ⚠️ **System Alerts panel** - Real-time alerts
- 📊 **Live Stats** - Files, locks, operations, security events
- 🎓 **OS Concepts Mapping** - Highlight demonstrated concepts
- 🧹 **Reset Demo State** - Clean up test files

### **👥 Multi-Client File Isolation**
- User1 uploads → stored in `storage/user1/`
- User2 uploads → stored in `storage/user2/`
- Each client only sees their own files
- C server auto-creates user directories
- Prevents unauthorized access to other user files

**Demo Credentials:**
- `user1` / `test123`
- `user2` / `secret`
- `admin` / `password`

### **📝 Audit Trail & Security Logging**
**Audit Log** (`logs/audit.log`):
- Every operation: UPLOAD, DOWNLOAD, DELETE, LOCK_ACQUIRED, LOCK_DENIED
- Format: `[timestamp] OPERATION=X FILE=Y STATUS=Z DETAILS=...`
- Mutex-protected writes (thread-safe)
- Readable in dashboard or via `/api/logs`
- 🆕 **Clear button** to truncate history

**Security Log** (`logs/security.log`):
- Authentication failures
- Invalid tokens
- Path traversal attempts
- Access violations
- IP-based rate limiting (3 failures → 600s block)
- Readable via `/api/security`

### **🔐 Authentication & Authorization**
- JWT-like token system (session-based)
- User credentials in `auth/users.db` (hashed)
- `@require_auth` decorator on all API endpoints
- Session attached to Flask request object
- 24-hour token expiry
- IP tracking for security alerts

---

## 🏗️ Architecture (3-Tier)
- DEADLOCK_RECOVERY events
- Real-time security dashboard panel

### **PHASE 4: Professional Web Dashboard** (In Progress)
7-panel cybersecurity-themed dashboard:
1. **System Status Cards** - Files, storage, locks, alerts
2. **File Operations** - Upload, download, delete with OS flow visualization
3. **Live Lock Visualization** - Real-time lock table with color coding
4. **Audit Timeline** - Chronological event log with filtering
5. **Security Alerts** - Failed auth, IP blocks, violations
6. **OS Concepts Reference** - Interactive system call explanations
7. **Terminal Event Feed** - Live OS event stream (monospace, cybersecurity style)

**Features:**
- Dark theme with professional styling
- Auto-polling every 2 seconds
- Multi-user support (independent sessions per browser)
- Click-to-execute OS commands
- Real-time lock status updates

### **PHASE 5: Demo Guide & Documentation** ✅
- 9 complete demo scenarios with expected outputs
- Viva Q&A scripts with OS concept explanations
- Step-by-step terminal commands (copy-paste ready)
- OS concept mapping for each operation

See: [DEMO_GUIDE.md](DEMO_GUIDE.md)

---

## 🏗️ System Architecture

### **Three-Tier Architecture: Core OS + API Layer + Web Observability**

```
┌──────────────────────────────────────────────────────────────────┐
│                        Web Dashboard                              │
│                   (HTML/CSS/JavaScript)                           │
│    Real-time OS State Visualization - NO filesystem access       │
└─────────────────────┬────────────────────────────────────────────┘
                      │ HTTP/JSON (Port 5000)
                      │ Polling every 2 seconds
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Python API Layer                             │
│                       (Flask app.py)                              │
│    Thin wrapper - forwards all operations to C server            │
└─────────────────────┬────────────────────────────────────────────┘
                      │ TCP Socket (Port 8888)
                      │ IPC Communication
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                       C OS Core Server                            │
│                      (file_server.c)                              │
│    ALL OS operations happen here:                                │
│    - File I/O (open, read, write, close, stat, unlink)          │
│    - File Locking (fcntl F_RDLCK, F_WRLCK)                      │
│    - Deadlock Prevention/Avoidance/Recovery                       │
│    - Multi-threading (pthread_create, mutex)                      │
└─────────────────────┬────────────────────────────────────────────┘
                      │ UNIX System Calls
                      │ Direct kernel interaction
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Linux Filesystem                               │
│              (storage/, logs/, metadata/)                         │
│                    (ext4/WSL2 Ubuntu)                             │
└──────────────────────────────────────────────────────────────────┘
```

**Architecture Philosophy:**
- **C Server**: Pure OS implementation - all system calls, locking, threading
- **Python API**: Thin IPC wrapper - only forwards commands to C server
- **Web Dashboard**: Visualization only - observes OS state without touching filesystem

This mirrors real-world system observability tools (Prometheus, Grafana, DataDog) where:
- Core system logic remains in low-level implementation
- API layer provides monitoring interface
- Dashboard visualizes internal state without interfering with operations

**Critical**: Web layer NEVER executes OS operations directly. All file operations route through C server to maintain pure OS implementation.

---

## 📂 Project Structure

```
NEW OS/
├── server/
│   └── file_server.c          # C-based OS core (ALL system calls here)
├── client/
│   └── client.py              # Python CLI client (terminal interface)
├── api_layer/
│   ├── app.py                 # Flask API (thin IPC wrapper)
│   └── requirements.txt       # Python dependencies
├── web_dashboard/
│   ├── index.html             # Web UI structure
│   ├── dashboard.js           # Frontend visualization logic
│   └── styles.css             # Professional technical styling
├── build/
│   └── file_server            # Compiled server binary
├── storage/                   # Uploaded files stored here
├── metadata/                  # File metadata (*.meta)
├── logs/
│   └── audit.log             # Audit logs (read by web dashboard)
├── test_files/               # Test files for demo
├── Makefile                  # Build automation
└── README.md                 # This file
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **Linux Environment** (Ubuntu/WSL/any Linux distro)
- **GCC Compiler** (for C code)
- **Python 3.8+** (for client and API layer)
- **Modern Web Browser** (Chrome/Firefox/Edge for dashboard)
- **pthread library** (usually pre-installed)
- **libssl-dev** (for SHA256: `sudo apt install libssl-dev`)

### Installation & Setup

```bash
# 1. Navigate to project directory
cd "NEW OS"

# 2. Build C server
make

# 3. Install Python API dependencies
cd api_layer
pip install -r requirements.txt
cd ..

# 4. Create test files (optional)
make test
```

---

## 🎬 **HOW TO START THE SYSTEM (STEP-BY-STEP)**

⚠️ **CRITICAL**: You MUST run BOTH servers simultaneously for the dashboard to work!

### **Step 1: Start C Server (Terminal 1)**

**Windows PowerShell:**
```powershell
wsl bash -c "cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS' && ./build/file_server"
```

**OR inside WSL terminal:**
```bash
cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS'
./build/file_server
```

**Expected output:**
```
=== SECURE FILE MANAGEMENT SERVER ===
Operating System Concepts: File I/O, IPC, Locking, Deadlock Prevention

[SERVER] Listening on port 8888...
```

✅ **Leave this terminal running!** Do NOT close it.

---

### **Step 2: Start Flask API (Terminal 2 - NEW TERMINAL)**

**Windows PowerShell:**
```powershell
wsl bash -c "export FILE_SERVER_AUTH=os-core-token && cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS/api_layer' && python3 app.py"
```

**OR inside WSL terminal:**
```bash
cd '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS/api_layer'
export FILE_SERVER_AUTH=os-core-token
python3 app.py
```

**Expected output:**
```
======================================================================
OS FILE SERVER - WEB API LAYER
======================================================================
C Server: 127.0.0.1:8888
API Server: http://localhost:5000
...
* Running on http://127.0.0.1:5000
```

✅ **Leave this terminal running too!**

---

### **Step 3: Open Dashboard (Browser)**

Open this file in your browser:
```
web_dashboard/index.html
```

**OR** from command line:
```bash
# Windows
start web_dashboard/index.html

# Linux/WSL
xdg-open web_dashboard/index.html
```

✅ **Dashboard should now show live data!**

---

## 🔐 **NEW: Authentication Quick Start**

The system now includes user authentication. Default test credentials:

| Username | Password | Role |
|----------|----------|------|
| `admin` | `password` | admin |
| `user1` | `test123` | user |
| `user2` | `secret` | user |

**How to Login (Web Dashboard):**
1. Dashboard detects no token → shows login form
2. Enter username/password
3. Click "Login"
4. Token saved to browser localStorage
5. Dashboard auto-loads with authenticated session

**How to Login (API):**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Response:
# {"success": true, "token": "...", "username": "admin"}
```

Then use token in subsequent requests:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/events
```

---

### **Troubleshooting Startup Issues**

| Problem | Solution |
|---------|----------|
| **"Address already in use" (port 8888)** | `wsl bash -c "lsof -ti:8888 \| xargs kill -9"` |
| **"Address already in use" (port 5000)** | `wsl bash -c "lsof -ti:5000 \| xargs kill -9"` |
| **Dashboard shows "Failed to fetch"** | Check BOTH servers are running (Terminals 1 & 2) |
| **"C server not running" in Flask logs** | Restart C server (Terminal 1) |
| **Build/file_server missing** | Run `make` or `make build` first |

---

### Running the System

#### **Option 1: Terminal-Only Mode (Original)**

```bash
# Terminal 1: Start C server
make run

# Terminal 2: Use Python CLI client
python3 client/client.py UPLOAD test_files/test1.txt
python3 client/client.py LIST
```

#### **Option 2: Full Stack with Web Dashboard (Engineering-Grade)**

```bash
# Terminal 1: Start C server
make run
# Output: [SERVER] Listening on port 8888...

# Terminal 2: Start Python API layer
cd api_layer
python3 app.py
# Output: Flask API running on http://localhost:5000

# Terminal 3 (or Browser): Open web dashboard
# Navigate to: web_dashboard/index.html
# Or use: xdg-open web_dashboard/index.html (Linux)
#         start web_dashboard/index.html (Windows)
```

**Web Dashboard Features:**
- Real-time system status (file count, storage, locks, logs)
- Upload/download/delete files via web interface
- Live lock visualization (read/write locks with OS concept labels)
- Audit timeline with filtering (all/upload/download/failed)
- OS concepts reference (explains each system call)
- Automatic polling every 2 seconds

**Architecture Verification:**
- Open browser DevTools → Network tab
- Upload a file → See HTTP POST to `/api/upload`
- Check C server terminal → See system call logs (open, write, fcntl)
- Check Python API terminal → See TCP socket communication
- This demonstrates proper 3-tier separation

---

## 🎯 Functional Operations

### **Terminal CLI Client (client.py)**

| Operation | Command | OS Concept |
|-----------|---------|-----------|
| **UPLOAD** | `python3 client/client.py UPLOAD test_files/test1.txt` | File locking (F_WRLCK), Bounded transfer, Timeout |
| **DOWNLOAD** | `python3 client/client.py DOWNLOAD test1.txt` | Read locks (F_RDLCK), Multiple readers |
| **LIST** | `python3 client/client.py LIST` | Directory traversal, stat() |
| **DELETE** | `python3 client/client.py DELETE test1.txt` | Lock before unlink(), File removal |
| **LOCKS** | `python3 client/client.py LOCKS` | fcntl() lock inspection |
| **LOGS** | `python3 client/client.py LOGS` | Thread-safe logging |

### **Web Dashboard (web_dashboard/index.html)**

| Feature | What It Does | Where OS Logic Executes |
|---------|--------------|------------------------|
| **Upload File** | Web form → API → C server | C server (open, write, fcntl) |
| **File List** | Displays files with size | C server (stat, readdir) |
| **Download** | Click button → API fetches from C server | C server (read, fcntl F_RDLCK) |
| **Delete** | Click trash → API sends delete to C server | C server (unlink) |
| **Lock Visualization** | Shows active fcntl locks | C server maintains lock state |
| **Audit Timeline** | Displays audit.log entries | C server writes logs (mutex-protected) |

**Critical**: Web dashboard NEVER touches filesystem directly - all operations forwarded to C server

---

## 🔐 Deadlock Handling (CRITICAL IMPLEMENTATION)

### 1️⃣ **Deadlock Prevention** ✅

**Problem:** Client waiting indefinitely for server EOF signal

**Solution:** Bounded file transfer protocol

```c
// Client sends exact file size
UPLOAD filename 1024\n
<exactly 1024 bytes>

// Server reads exactly N bytes (never waits for EOF)
while (total_read < filesize) {
    bytes_read = read(socket, buffer, to_read);
    total_read += bytes_read;
}
// Stops immediately after receiving filesize bytes
```

**Breaks:** Hold-and-wait condition

---

### 2️⃣ **Deadlock Avoidance** ✅

**Problem:** Multiple clients trying to lock same file → circular wait

**Solution:** Non-blocking locks

```c
// Uses F_SETLK (non-blocking) instead of F_SETLKW (blocking)
if (fcntl(fd, F_SETLK, &lock) == -1) {
    if (errno == EACCES || errno == EAGAIN) {
        // File already locked → reject immediately
        return "File is locked by another process";
    }
}
```

**Avoids:** Unsafe states, circular wait

---

### 3️⃣ **Deadlock Detection & Recovery** ✅

**Problem:** Client crashes during upload → file lock held forever

**Solution:** Timeout mechanism

```c
time_t start_time = time(NULL);
while (total_read < filesize) {
    time_t current_time = time(NULL);
    if (difftime(current_time, start_time) > UPLOAD_TIMEOUT) {
        // Timeout exceeded → DEADLOCK RECOVERY
        release_file_lock(fd);
        unlink(filepath);  // Remove incomplete file
        return "Upload timeout - deadlock recovery";
    }
    // Continue reading...
}
```

**Detects & Recovers:** Indefinite waits, resource leaks

---

## 🧵 Critical Section Design (OS Best Practice)

### ✅ Correct Order

```c
1. Acquire file lock (fcntl)
2. Write file data        ← ONLY THIS IS CRITICAL
3. Release file lock
4. Compute checksum       ← Outside critical section
5. Update metadata        ← Outside critical section
6. Write audit log        ← Outside critical section
7. Send response to client
```

### ❌ Wrong Order (Would cause performance issues)

```c
1. Acquire file lock
2. Write file
3. Compute checksum      ← Holding lock unnecessarily
4. Update metadata       ← Holding lock unnecessarily
5. Write logs            ← Holding lock unnecessarily
6. Release lock          ← Too late!
```

---

## 🧪 Demo Scenarios (For OS Lab Presentation)

### **Demo 1: Normal Upload/Download**

```bash
# Terminal 1 (Server)
make run

# Terminal 2 (Client 1)
python3 client/client.py UPLOAD test_files/test1.txt
python3 client/client.py LIST
python3 client/client.py DOWNLOAD test1.txt downloaded_test1.txt
```

**Expected Output:**
```
[UPLOAD] Acquiring write lock on test1.txt
[UPLOAD] Starting bounded transfer: 1024 bytes
[UPLOAD] Write lock released on test1.txt
[SUCCESS] File uploaded successfully!
```

---

### **Demo 2: Concurrent Access with Locking**

**What to show:** Two clients try uploading same file → second gets rejected (file locking in action)

**If you're in Windows PowerShell:**
```powershell
# Terminal 2: Start upload
wsl bash -c "curl -X POST http://localhost:5000/api/upload -F 'file=@test_files/test1.txt'"

# Terminal 3: Immediately try same file
wsl bash -c "curl -X POST http://localhost:5000/api/upload -F 'file=@test_files/test1.txt'"
```

**If you're already inside WSL/Ubuntu terminal:**
```bash
# Terminal 2: Start upload
curl -X POST http://localhost:5000/api/upload -F 'file=@test_files/test1.txt'

# Terminal 3: Immediately try same file (open new tab)
curl -X POST http://localhost:5000/api/upload -F 'file=@test_files/test1.txt'
```

**Expected Output (Terminal 3):**
```
[ERROR] File is locked by another process
```

**Demonstrates:** File locking (fcntl F_WRLCK) prevents concurrent writes

---

### **Demo 3: Multiple Readers (Shared Read Locks)**

**What to show:** Multiple clients downloading same file simultaneously (F_RDLCK shared locks)

**If you're in Windows PowerShell:**
```powershell
# Terminal 2: Start download
wsl bash -c "curl -O http://localhost:5000/api/download/test1.txt"

# Terminal 3: Simultaneously download same file
wsl bash -c "curl -O http://localhost:5000/api/download/test1.txt"
```

**If you're already inside WSL/Ubuntu terminal:**
```bash
# Terminal 2: Start download
curl -O http://localhost:5000/api/download/test1.txt

# Terminal 3: Simultaneously download (both succeed!)
curl -O http://localhost:5000/api/download/test1.txt
```

**Expected:** Both downloads succeed (read locks are shared, multiple readers allowed)

**Demonstrates:** F_RDLCK allows concurrent reads (readers-writers pattern)

---

### **Demo 4: View Audit Logs (Thread-Safe Logging)**

**What to show:** Real-time audit timeline with mutex-protected writes

**If you're in Windows PowerShell:**
```powershell
# View audit logs in JSON format
wsl bash -c "curl http://localhost:5000/api/logs"

# Or view raw log file
wsl bash -c "cat '/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS/logs/audit.log'"
```

**If you're already inside WSL/Ubuntu terminal:**
```bash
# View audit logs via API
curl http://localhost:5000/api/logs

# Or view raw log file
cat logs/audit.log
```

**Expected Output:**
```json
{
  "logs": [
    "[2026-01-27 21:46:55] OPERATION=UPLOAD FILE=demo.txt STATUS=SUCCESS DETAILS=Size: 32 bytes",
    "[2026-01-27 21:47:10] OPERATION=DOWNLOAD FILE=demo.txt STATUS=SUCCESS"
  ]
}
```

**Demonstrates:** Mutex-protected audit logging (pthread_mutex_lock/unlock)

---

### **Demo 5: Security Alerts (Authentication Failure)**

**What to show:** Failed auth attempts trigger security alerts and client blocking

**If you're in Windows PowerShell:**
```powershell
# Attempt with wrong token (simulate attack)
wsl bash -c "curl -H 'AUTH: wrong-token' http://localhost:5000/api/list"

# Try again (3 failures → blocked)
wsl bash -c "curl -H 'AUTH: wrong-token' http://localhost:5000/api/list"
wsl bash -c "curl -H 'AUTH: wrong-token' http://localhost:5000/api/list"

# Check security alerts
wsl bash -c "curl http://localhost:5000/api/security"
```

**If you're already inside WSL/Ubuntu terminal:**
```bash
# Attempt with wrong token
curl -H 'AUTH: wrong-token' http://localhost:5000/api/list

# Try again (3 failures → blocked for 600s)
curl -H 'AUTH: wrong-token' http://localhost:5000/api/list
curl -H 'AUTH: wrong-token' http://localhost:5000/api/list

# View security log
curl http://localhost:5000/api/security
```

**Expected Output:**
```json
{
  "alerts": [
    {
      "timestamp": "2026-01-27 21:50:15",
      "type": "AUTH_FAIL",
      "details": "Invalid token from 127.0.0.1",
      "severity": "warning"
    },
    {
      "timestamp": "2026-01-27 21:50:20",
      "type": "CLIENT_BLOCKED",
      "details": "IP 127.0.0.1 blocked for 600s (3 failures)",
      "severity": "critical"
    }
  ]
}
```

**Demonstrates:** Security hardening with failure tracking and auto-blocking

---

### **Demo 6: Delete File (Lock + Unlink)**

**What to show:** Delete operation acquires lock before calling unlink()

**If you're in Windows PowerShell:**
```powershell
# Delete a file
wsl bash -c "curl -X DELETE http://localhost:5000/api/delete/demo.txt"

# Verify deletion
wsl bash -c "curl http://localhost:5000/api/list"
```

**If you're already inside WSL/Ubuntu terminal:**
```bash
# Delete file
curl -X DELETE http://localhost:5000/api/delete/demo.txt

# List files (verify it's gone)
curl http://localhost:5000/api/list
```

**Expected Output:**
```json
{"status": "success", "message": "File deleted successfully"}
```

**Demonstrates:** Lock acquisition before unlink() system call

---

## � Quick Demo Script (Copy-Paste Ready)

**Complete end-to-end demo to populate all dashboard panels**

### **If you're in WSL/Ubuntu terminal:**

```bash
# ============================================
# COMPLETE DEMO SCRIPT - Run line by line
# ============================================

# 1. Upload a file (populates Audit Timeline + File List)
echo 'This is a demo file for OS presentation' > /tmp/demo.txt
curl -X POST http://localhost:5000/api/upload -F 'file=@/tmp/demo.txt'

# 2. View system status (check file count increased)
curl http://localhost:5000/api/status

# 3. List all files
curl http://localhost:5000/api/list

# 4. View audit logs (shows UPLOAD operation)
curl http://localhost:5000/api/logs

# 5. Download file (populates more audit entries)
curl -O http://localhost:5000/api/download/demo.txt

# 6. View locks (shows active fcntl locks)
curl http://localhost:5000/api/locks

# 7. Security test - Send wrong auth DIRECTLY to C server (port 8888)
# This populates Security Alerts panel
echo -e "AUTH wrong-token\nLIST\n" | nc localhost 8888
echo -e "AUTH bad-token\nLIST\n" | nc localhost 8888
echo -e "AUTH fake-token\nLIST\n" | nc localhost 8888

# 8. View security alerts (now populated!)
curl http://localhost:5000/api/security

# 9. Delete file
curl -X DELETE http://localhost:5000/api/delete/demo.txt

# 10. Verify deletion
curl http://localhost:5000/api/list
```

### **If you're in Windows PowerShell:**

```powershell
# ============================================
# COMPLETE DEMO SCRIPT - Windows Version
# ============================================

# 1. Upload a file
wsl bash -c "echo 'This is a demo file for OS presentation' > /tmp/demo.txt"
wsl bash -c "curl -X POST http://localhost:5000/api/upload -F 'file=@/tmp/demo.txt'"

# 2. View system status
wsl bash -c "curl http://localhost:5000/api/status"

# 3. List all files
wsl bash -c "curl http://localhost:5000/api/list"

# 4. View audit logs
wsl bash -c "curl http://localhost:5000/api/logs"

# 5. Download file
wsl bash -c "curl -O http://localhost:5000/api/download/demo.txt"

# 6. View locks
wsl bash -c "curl http://localhost:5000/api/locks"

# 7. Security test - Wrong auth to C server (triggers security alerts)
wsl bash -c "echo -e 'AUTH wrong-token\nLIST\n' | nc localhost 8888"
wsl bash -c "echo -e 'AUTH bad-token\nLIST\n' | nc localhost 8888"
wsl bash -c "echo -e 'AUTH fake-token\nLIST\n' | nc localhost 8888"

# 8. View security alerts (now populated!)
wsl bash -c "curl http://localhost:5000/api/security"

# 9. Delete file
wsl bash -c "curl -X DELETE http://localhost:5000/api/delete/demo.txt"

# 10. Verify deletion
wsl bash -c "curl http://localhost:5000/api/list"
```

### **Why Security Alerts Need Direct C Server Access**

⚠️ **Important:** Security alerts only trigger when sending **incorrect auth tokens directly to the C server (port 8888)**.

- ✅ **This works:** `echo -e "AUTH wrong-token\nLIST\n" | nc localhost 8888`
- ❌ **This won't work:** `curl -H 'AUTH: wrong-token' http://localhost:5000/api/list`

**Reason:** Flask API already authenticates with valid token (`os-core-token`) before forwarding to C server. To test security features, you must bypass Flask and talk directly to port 8888.

### **Expected Dashboard Results After Demo**

- ✅ **System Status**: Files Stored = 1 (or more)
- ✅ **File List**: Shows `demo.txt` with size
- ✅ **Audit Timeline**: Multiple entries (UPLOAD, DOWNLOAD, DELETE)
- ✅ **Security Alerts**: 3+ entries showing AUTH_FAILURE warnings
- ✅ **File Locks**: Shows active locks during operations

---

## �📊 OS Concepts Coverage

| Concept | Where Implemented | Line Reference |
|---------|-------------------|----------------|
| **UNIX File I/O** | open(), read(), write(), stat(), unlink() | Throughout server code |
| **File Locking** | fcntl(F_SETLK) with F_RDLCK/F_WRLCK | acquire_file_lock() |
| **TCP Sockets** | socket(), bind(), listen(), accept() | main() function |
| **Thread Management** | pthread_create(), pthread_detach() | main() client handler |
| **Thread Sync** | pthread_mutex_lock/unlock | update_metadata(), write_audit_log() |
| **Deadlock Prevention** | Bounded file transfer | handle_upload() |
| **Deadlock Avoidance** | Non-blocking locks (F_SETLK) | acquire_file_lock() |
| **Deadlock Recovery** | Timeout mechanism | handle_upload() timeout check |
| **Process Control** | getpid() for lock ownership | acquire_file_lock() |

---

## 🎓 Viva Questions & Answers

### Q1: How does your system prevent deadlock?

**Answer:** 
"We use three strategies:
1. **Prevention:** Bounded file transfers break the hold-and-wait condition by ensuring the server never waits indefinitely for data.
2. **Avoidance:** Non-blocking locks (F_SETLK) reject requests immediately if a file is locked, avoiding unsafe states.
3. **Recovery:** Timeout mechanism (30 seconds) detects and recovers from potential deadlocks by releasing locks and cleaning up."

---

### Q2: What is the difference between F_SETLK and F_SETLKW?

**Answer:**
"F_SETLK is non-blocking and returns immediately if the lock cannot be acquired, making it safer for deadlock avoidance. F_SETLKW is blocking and waits indefinitely until the lock is available, which can cause deadlock if not used with timeouts. We use F_SETLK for safety."

---

### Q3: Why do you release the file lock before updating metadata?

**Answer:**
"To minimize the critical section. The file lock only protects file data, not metadata. Holding the lock during metadata updates would unnecessarily block other operations. We use a separate mutex for metadata protection, following OS best practices for fine-grained locking."

---

### Q4: How does your system handle multiple readers?

**Answer:**
"We use F_RDLCK (read locks) which allows multiple clients to download the same file simultaneously. Read locks are shared and only conflict with write locks (F_WRLCK), implementing the readers-writers pattern from OS theory."

---

### Q5: What UNIX system calls does your project use?

**Answer:**
"Primary system calls: open(), read(), write(), close() for file I/O; fcntl() for locking; stat() for file information; unlink() for deletion; socket(), bind(), listen(), accept() for TCP IPC; pthread_create() for thread management; pthread_mutex_lock/unlock for synchronization."

---

## 🛠️ Compilation Details

### Compiler Flags Explained

```bash
gcc -Wall -Wextra -pthread -O2 server/file_server.c -o build/file_server
```

- `-Wall -Wextra`: Enable all warnings (good practice)
- `-pthread`: Link pthread library (for multi-threading)
- `-O2`: Optimization level 2 (balanced performance)

---

## 🔧 Troubleshooting

### Server won't start: "Address already in use"

**Solution:**
```bash
# Kill existing process on port 8888
lsof -ti:8888 | xargs kill -9

# Or wait 30 seconds for TCP TIME_WAIT to expire
```

---

### Client can't connect

**Solution:**
```bash
# Check if server is running
ps aux | grep file_server

# Check if port is listening
netstat -tuln | grep 8888

# Start server
make run
```

---

### Permission denied when writing files

**Solution:**
```bash
# Ensure directories exist and have write permissions
mkdir -p storage metadata logs
chmod 755 storage metadata logs
```

---

## 📝 Makefile Commands

```bash
make           # Setup and build
make build     # Compile server only
make run       # Start server
make clean     # Remove build artifacts
make clean-all # Remove all data (storage, logs, metadata)
make test      # Create test files
make help      # Show help
```

---

## � **DEMO MODE GUIDE (Interactive Learning Tool)**

### **What is Demo Mode?**
A dedicated web page (`/demo.html`) with **6 interactive demonstrations** designed specifically for evaluation and teaching. Each demo can run **live** with real file operations OR in **Explain Mode** for safe presentations.

### **How to Access Demo Mode**

From the main dashboard (http://localhost:5000/):
1. Look for the yellow **"🎬 Demo Mode"** button in the header
2. Click it → Navigate to `/demo.html`
3. You'll see the demo scenarios panel with 6 interactive cards

**OR** go directly to:
```
http://localhost:5000/demo.html
```

### **6 Interactive Demonstrations**

#### **Demo 1: Exclusive WRITE Lock** ⭐⭐⭐
Demonstrates `fcntl(F_WRLCK)` - mutual exclusion for file writes.

**What it does:**
- Client A uploads a file → Acquires WRITE lock
- Client B tries to upload same file → Lock rejected
- Console shows: `[LOCK] WRITE acquired`, `[LOCK] WRITE denied`

**Why it matters:** Shows that only one process can write at a time.

**For Viva:** "This demonstrates mutual exclusion using fcntl F_WRLCK."

---

#### **Demo 2: Shared READ Locks (Readers-Writers)** ⭐⭐⭐
Demonstrates `fcntl(F_RDLCK)` - multiple readers allowed, readers-writers problem.

**What it does:**
- Client A downloads file → Acquires READ lock
- Client B downloads same file → Also acquires READ lock (shared!)
- Both succeed simultaneously
- Console shows: `[LOCK] READ acquired` (×2)

**Why it matters:** Shows that readers don't block each other.

**For Viva:** "This is the readers-writers problem solved using shared read locks."

---

#### **Demo 3: Deadlock Detection & Recovery** ⭐⭐⭐⭐
Demonstrates deadlock recovery mechanism with timeout.

**What it does:**
- Simulates a stalled upload (client holds lock but doesn't complete)
- System detects timeout after 300 seconds
- Automatically releases lock and cleans up partial file
- Console shows: `[TIMEOUT]`, `[RECOVERY]`, `[CLEANUP]`

**Why it matters:** Shows proactive deadlock recovery.

**For Viva:** "If a client stalls, we detect it via timeout and forcefully recover resources."

---

#### **Demo 4: Security Violation Detection** ⭐⭐⭐
Demonstrates OS-level security: authentication, path traversal, access control.

**What it does:**
- Attempts path traversal attack → Blocked with validation
- Invalid auth token → Rejected with 401
- Access violations logged to security.log
- Console shows: `[SECURITY]`, `[BLOCKED]`

**Why it matters:** Shows defense-in-depth security model.

**For Viva:** "Security violations are detected at API layer and logged comprehensively."

---

#### **Demo 5: Concurrent File Operations** ⭐⭐⭐
Demonstrates lock granularity and concurrent access.

**What it does:**
- 3 simultaneous uploads (fileA, fileB, fileC)
- Each acquires independent lock
- All proceed without blocking each other
- Console shows: `[CLIENT A]`, `[CLIENT B]`, `[CLIENT C]`

**Why it matters:** Shows efficient fine-grained locking.

**For Viva:** "File-level locking allows different files to be accessed concurrently."

---

#### **Demo 6: Deadlock Conditions Analysis (VIVA GOLD)** ⭐⭐⭐⭐⭐
**NEW:** Shows Coffman's 4 deadlock conditions and how your system breaks them.

**What it does:**
- Shows all 4 necessary deadlock conditions:
  1. Mutual Exclusion ✅ Required
  2. Hold and Wait ❌ **BROKEN** (non-blocking locks)
  3. No Preemption ❌ **BROKEN** (timeout recovery)
  4. Circular Wait ❌ **BROKEN** (lock ordering)
  
- Explains would-be deadlock scenario
- Shows how system avoids it
- Includes viva answer template

**Why it matters:** Demonstrates deep understanding of deadlock theory.

**For Viva:** Perfect answer to "How is deadlock handled in your system?"

### **Demo Mode Features**

#### **📚 Explain Mode (Safe Presentation)**
Toggle in top-right corner. When enabled:
- ✅ Shows all explanations with color-coded concepts
- ✅ No actual operations execute
- ✅ Perfect for viva presentation (no risk of failure)
- ❌ Run buttons disabled

**Use case:** "Let me explain the concepts without actually running anything."

#### **🖥️ Live OS Event Console**
Real-time terminal output on right panel showing all events:
```
[STEP 1] Uploading demo-write-lock.txt...
[LOCK] WRITE lock acquired on demo-write-lock.txt
[UPLOAD] File uploaded successfully
[STEP 2] Lock released after operation completed
```

#### **🔐 Active Locks Panel**
Shows all currently held locks:
- Filename
- Lock type (READ or WRITE)
- PID of process holding lock

#### **⚠️ System Alerts**
Real-time alerts with severity levels and timestamps.

#### **📊 Live Stats**
Counters for:
- Files uploaded
- Active locks
- Operations performed
- Security events

#### **🎓 OS Concepts Mapping**
Highlights relevant OS concepts during each demo:
- UNIX File I/O
- File Locking
- Deadlock Prevention
- IPC via TCP
- Thread Synchronization
- Security

#### **🧹 Reset Demo State**
Button to clean up all demo-generated test files.

### **Demo Workflow for Evaluation**

**Scenario: Evaluator asks "Show me deadlock handling"**

1. **Login to dashboard** with user1/test123
2. **Click "🎬 Demo Mode"**
3. **Select Demo 3 OR Demo 6**
   - Demo 3: Shows practical recovery mechanism
   - Demo 6: Shows theoretical understanding
4. **Toggle "Explain Mode" ON** (for safe presentation)
5. **Click "📖 Explain" button**
6. **Evaluator sees:**
   - Detailed explanation with color coding
   - 4 deadlock conditions checklist
   - Which conditions your system breaks
   - Viva answer template
   - OS system calls used

**Result:** Evaluator is impressed with both theoretical and practical knowledge!

---

## �🎯 Scoring Points for Evaluation

✅ **Correct use of UNIX system calls** (20%)
- open(), read(), write(), fcntl(), stat(), unlink()

✅ **File locking implementation** (20%)
- fcntl() with F_RDLCK and F_WRLCK

✅ **Deadlock handling** (25%)
- Prevention, avoidance, and recovery mechanisms

✅ **Client-server communication** (15%)
- TCP sockets, proper protocol

✅ **Thread management** (10%)
- pthread_create(), proper synchronization

✅ **Demo quality** (10%)
- Terminal-based, fast, reliable, explainable

---

## 🚫 What This Project Does NOT Use

- ❌ No high-level file libraries (fopen, fread, fwrite)
- ❌ No GUI or web interface (pure terminal)
- ❌ No database servers
- ❌ No cloud services
- ❌ No blocking calls without timeouts
- ❌ No fsync() in critical sections

---

## 📚 References

- **Operating System Concepts** (Silberschatz, Galvin, Gagne)
- **Advanced Programming in UNIX Environment** (W. Richard Stevens)
- Linux Manual Pages: `man 2 open`, `man 2 fcntl`, `man 2 socket`

---

## 👨‍💻 Project Structure Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Server | C | Core OS implementation with system calls |
| Client | Python | Easy-to-demo terminal interface |
| Build System | Makefile | Compilation automation |
| Storage | Linux FS | File storage backend |
| IPC | TCP Sockets | Client-server communication |

---

## ✅ Checklist Before Demo

- [ ] Server compiles without errors (`make build`)
- [ ] Test files created (`make test`)
- [ ] Server starts successfully (`make run`)
- [ ] Client can connect (try `LIST` command)
- [ ] Upload works (try small file first)
- [ ] Download works
- [ ] Concurrent access shows locking
- [ ] Logs and locks commands work
- [ ] Can explain deadlock prevention
- [ ] Can explain OS concepts used

---

## 🎓 Final Tips for Viva

1. **Always mention OS concepts** when explaining code
2. **Show terminal output** during demo (it's verbose and educational)
3. **Explain deadlock prevention** clearly (it's the most important part)
4. **Know the difference** between F_SETLK and F_SETLKW
5. **Understand critical sections** and why we minimize them
6. **Be ready to show code** for specific functions
7. **Demonstrate concurrent access** with multiple terminals
8. **Explain bounded transfers** and why they prevent deadlock

---

## 📧 Contact

For questions or clarifications during evaluation, refer to:
- Code comments (extensive documentation)
- This README
- OS textbook concepts

---

**Good luck with your OS Lab evaluation! 🎯**

*This project is designed to score maximum marks by correctly implementing all core OS concepts with proper deadlock handling and terminal-based demonstration.*
