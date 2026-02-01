# Web Dashboard User Guide

## Overview

The web dashboard provides real-time visualization of the OS file server's internal state. It demonstrates **system observability** - monitoring low-level OS operations without interfering with them.

**Critical Understanding**: This web layer is a **visualization tool only**. All actual OS operations (file I/O, locking, threading) still execute in the C server. The dashboard simply observes and displays the state.

---

## Architecture Flow

When you click "Upload File" in the web dashboard:

1. **Browser** → HTTP POST with file → **Python API** (port 5000)
2. **Python API** → Saves temp file, opens TCP socket → **C Server** (port 8888)
3. **C Server** → Executes `open()`, `write()`, `fcntl()` system calls → **Filesystem**
4. **C Server** → Sends result → **Python API**
5. **Python API** → Returns JSON response → **Browser**
6. **Dashboard** → Updates UI with operation results

**Every file operation goes through the C server** - the web layer is just a frontend.

---

## Dashboard Sections

### 1. System Status Panel

**What it shows:**
- **File Count**: Total files in storage/ directory (via C server's LIST)
- **Total Storage**: Sum of all file sizes (C server uses `stat()`)
- **Active Locks**: Number of fcntl locks held (C server tracks this)
- **Log Entries**: Total operations logged (reads audit.log)

**OS Concepts:**
- File count: `readdir()` directory traversal
- Storage: `stat()` system call for file sizes
- Locks: `fcntl()` lock state tracking
- Logs: Thread-safe append-only file writes

**Refresh Rate**: Auto-updates every 2 seconds

---

### 2. File Operations Panel

#### Upload
- **UI**: File input + "Upload File" button
- **Flow**: Browser → API → C server `UPLOAD` command
- **C Server Actions**:
  1. Acquire global lock (deadlock avoidance)
  2. `open()` with `O_WRONLY | O_CREAT | O_TRUNC`
  3. `fcntl()` apply F_WRLCK (write lock)
  4. `write()` file data in 4KB chunks
  5. Release locks, `close()` file
- **Timeout**: 300 seconds (5 minutes)
- **Concurrency**: If file is locked, upload rejected

#### File List
- **UI**: Scrollable list with file names, sizes, action buttons
- **Data Source**: C server `LIST` command
- **C Server Actions**:
  1. `opendir()` on storage/ directory
  2. `readdir()` to iterate files
  3. `stat()` each file for size/metadata
  4. Return formatted list
- **Features**: Real-time updates, click to download/delete

#### Download
- **UI**: Download button on each file
- **Flow**: Click → API `/api/download/<filename>` → C server
- **C Server Actions**:
  1. `open()` file with O_RDONLY
  2. `fcntl()` apply F_RDLCK (read lock) - non-exclusive
  3. `read()` file data
  4. Send to API, release lock
- **Multiple Readers**: Multiple downloads can happen simultaneously (shared read locks)

#### Delete
- **UI**: Red trash icon button
- **Flow**: Click → Confirmation → API DELETE → C server
- **C Server Actions**:
  1. Acquire global lock (prevent concurrent access)
  2. `unlink()` system call removes file
  3. Remove metadata file
  4. Release lock
- **Safety**: Cannot delete locked files

---

### 3. Lock Visualization Panel

**What it shows:**
- List of currently locked files
- Lock type: Read (F_RDLCK) or Write (F_WRLCK)
- Thread ID holding the lock

**Color Coding:**
- 🟢 **Green**: Read lock (F_RDLCK) - multiple readers allowed
- 🔴 **Red**: Write lock (F_WRLCK) - exclusive access

**OS Concepts Explained:**
- **Deadlock Prevention**: Bounded file transfers (fixed timeout)
- **Deadlock Avoidance**: Non-blocking lock acquisition (`F_SETLK`)
- **Deadlock Recovery**: 300-second timeout, automatic thread termination

**Testing Lock Rejection:**
1. Open two terminals
2. Terminal 1: `python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10`
3. Quickly in Terminal 2: `python3 client/client.py UPLOAD test_files/test_100mb.bin`
4. Terminal 2 receives: "ERROR: File is locked by another process"
5. Dashboard shows: Lock visualization with test_100mb.bin locked

---

### 4. Audit Timeline Panel

**What it shows:**
- Chronological log of all operations
- Timestamp, operation type, filename, status, details

**Filtering:**
- **All**: Show everything
- **Uploads**: Only UPLOAD operations
- **Downloads**: Only DOWNLOAD operations
- **Failed**: Only failed operations (errors)

**Data Source**: 
- C server writes to `logs/audit.log` (mutex-protected)
- Dashboard reads log file via API (no direct filesystem access)

**Log Format:**
```
2024-01-15 14:32:45 | UPLOAD | test1.txt | 1024 bytes | SUCCESS | Client: 127.0.0.1
```

**OS Concept**: Thread-safe logging with `pthread_mutex_t log_mutex`

---

### 5. OS Concepts Reference

Educational grid explaining each OS concept implemented:

- **File I/O**: open(), read(), write(), close()
- **File Locking**: fcntl() with F_RDLCK, F_WRLCK
- **Deadlock Prevention**: Bounded transfers, timeouts
- **Deadlock Avoidance**: Non-blocking locks, global tracking
- **Deadlock Recovery**: Timeout mechanism
- **Multi-threading**: pthread_create(), pthread_detach()
- **IPC**: TCP sockets for client-server communication
- **Thread-Safe Logging**: Mutex-protected log writes

---

## Technical Details

### Polling Mechanism
```javascript
setInterval(refreshAll, 2000); // Poll every 2 seconds

async function refreshAll() {
    await Promise.all([
        loadStatus(),   // GET /api/status
        loadFiles(),    // GET /api/list
        loadLocks(),    // GET /api/locks
        loadLogs()      // GET /api/logs
    ]);
}
```

### API Endpoints

| Endpoint | Method | Purpose | C Server Command |
|----------|--------|---------|------------------|
| `/api/upload` | POST | Upload file | `UPLOAD <filename> <size>` |
| `/api/download/<name>` | GET | Download file | `DOWNLOAD <filename>` |
| `/api/delete/<name>` | DELETE | Delete file | `DELETE <filename>` |
| `/api/list` | GET | List files | `LIST` |
| `/api/locks` | GET | Read lock state | Reads C server's locked_files[] |
| `/api/logs` | GET | Read audit log | Reads logs/audit.log |
| `/api/status` | GET | System health | Checks all components |

### Architecture Validation

To verify proper 3-tier separation:

1. **Open Browser DevTools** (F12)
2. **Network Tab** → See HTTP requests to `localhost:5000`
3. **C Server Terminal** → See system call logs
4. **Python API Terminal** → See TCP socket communication

This proves:
- Browser never touches filesystem
- API forwards requests via TCP
- C server executes all OS operations

---

## Real-World Comparison

This architecture mirrors production monitoring systems:

| Tool | Purpose | Comparison |
|------|---------|------------|
| **Prometheus** | Metrics collection | Python API scraping C server state |
| **Grafana** | Visualization | Web dashboard displaying OS state |
| **DataDog APM** | Application monitoring | Real-time operation tracking |
| **New Relic** | Performance monitoring | Lock contention visualization |

**Key Similarity**: Monitoring layer observes system state without executing business logic.

---

## Demo Scenarios

### Scenario 1: Concurrent Upload Rejection

**Objective**: Demonstrate file locking and deadlock avoidance

**Steps**:
1. Open web dashboard
2. Terminal 1: `python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10`
3. Watch dashboard: Lock visualization shows test_100mb.bin locked
4. Terminal 2: Try same upload → Rejected immediately
5. Dashboard audit log: Shows rejection event

**OS Concepts**: Global lock tracking, deadlock avoidance (non-blocking locks)

### Scenario 2: Multiple Concurrent Downloads

**Objective**: Demonstrate shared read locks

**Steps**:
1. Upload a file: `python3 client/client.py UPLOAD test_files/test3_large.bin`
2. Terminal 1: `python3 client/client.py DOWNLOAD test3_large.bin`
3. Terminal 2: `python3 client/client.py DOWNLOAD test3_large.bin` (simultaneously)
4. Dashboard: Shows multiple read locks on same file

**OS Concepts**: F_RDLCK shared locks, multiple readers allowed

### Scenario 3: Real-Time Status Updates

**Objective**: Demonstrate observability without interference

**Steps**:
1. Open dashboard, note file count
2. Use CLI to upload: `python3 client/client.py UPLOAD test_files/test1.txt`
3. Watch dashboard: File count increments within 2 seconds
4. Dashboard shows: New file in list, audit log entry

**OS Concepts**: State observation via polling, no direct filesystem access

---

## Troubleshooting

### Dashboard shows "Server Offline"
- **Cause**: C server not running or API can't reach it
- **Fix**: 
  1. Check C server: `ps aux | grep file_server`
  2. Restart: `make run`
  3. Check port 8888: `netstat -tuln | grep 8888`

### API returns errors
- **Cause**: Python API can't communicate with C server
- **Fix**:
  1. Check Flask running: `http://localhost:5000/api/status`
  2. Restart API: `cd api_layer && python3 app.py`
  3. Check logs in API terminal

### Dashboard not updating
- **Cause**: Browser console errors or CORS issues
- **Fix**:
  1. Open DevTools (F12) → Console tab
  2. Check for JavaScript errors
  3. Verify Flask-CORS installed: `pip show Flask-CORS`

### Upload fails
- **Cause**: File locked or C server error
- **Fix**:
  1. Check C server terminal for error logs
  2. View locks: `python3 client/client.py LOCKS`
  3. Check storage directory: `ls -la storage/`

---

## Educational Value

**For OS Lab Evaluation:**

This project demonstrates understanding of:
1. **UNIX System Calls**: Not abstract - actual open(), fcntl(), pthread_create()
2. **Real-World Architecture**: Production-style monitoring separation
3. **Observability**: Visualizing internal state without breaking encapsulation
4. **Engineering Maturity**: Not just "it works" - professional instrumentation

**Why Web Dashboard?**

Modern systems engineering requires understanding how to:
- Monitor low-level operations in real-time
- Visualize concurrency and contention
- Debug distributed systems
- Build observability into OS-level components

This goes beyond "CLI prints to terminal" to demonstrate industry-standard practices.

---

## Summary

**What the Dashboard IS:**
- Visualization tool for OS state
- Monitoring interface (like Grafana/DataDog)
- Educational aid for understanding OS concepts
- Real-time system observability layer

**What the Dashboard IS NOT:**
- Alternative file server implementation
- OS logic moved to web layer
- Direct filesystem access
- Replacement for C server

**Core Principle**: All OS operations execute in C. Web layer only observes and displays state.
