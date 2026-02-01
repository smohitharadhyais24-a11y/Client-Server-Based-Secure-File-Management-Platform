# 🚀 QUICK START - WEB DASHBOARD

## One-Command Launch

### Linux/WSL:
```bash
./start_full_stack.sh
```

### Windows:
```batch
start_full_stack.bat
```

---

## Manual Start (3 Steps)

### Step 1: C Server
```bash
make && ./build/file_server
```
**Wait for**: `[SERVER] Listening on port 8888...`

### Step 2: Python API
```bash
cd api_layer
pip install -r requirements.txt  # First time only
python3 app.py
```
**Wait for**: `Flask API running on http://localhost:5000`

### Step 3: Web Dashboard
Open in browser: `web_dashboard/index.html`

---

## Verify It's Working ✅

1. Dashboard shows **"Online"** (green indicator)
2. System status cards show numbers (not "Loading...")
3. No errors in browser DevTools Console (F12)

---

## Quick Demo (2 Minutes)

### Upload File
1. Click "Choose File" → Select `test_files/test1.txt`
2. Click "Upload File"
3. See file appear in list below

**Check C server terminal**: Should show system calls

### Download File
1. Click download icon (⬇) next to test1.txt
2. Browser downloads file

### Delete File
1. Click trash icon (🗑) next to test1.txt
2. Confirm deletion
3. File disappears

---

## Concurrency Demo (3 Minutes)

### Show Lock Rejection

**Terminal 1**:
```bash
python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10
```

**Dashboard**: 
- Refresh after 2 seconds
- Lock Visualization panel shows: 🔴 **test_100mb.bin [WRITE LOCK]**

**Terminal 2** (immediately):
```bash
python3 client/client.py UPLOAD test_files/test_100mb.bin
```

**Result**: 
- Terminal 2: `[ERROR] File is locked by another process`
- Dashboard Audit Timeline: Shows rejection event

**This proves**: fcntl locking + deadlock avoidance working!

---

## Architecture Proof

### Show Web Layer Doesn't Touch Filesystem

1. Open **Browser DevTools** (F12) → **Network tab**
2. Upload a file via dashboard
3. **Observe**:
   - Network shows: HTTP POST to `localhost:5000` ✅
   - NO `file://` URIs ✅
   - C server terminal: System call logs (`open()`, `write()`, `fcntl()`) ✅

**This proves**: Web → API → C server → Filesystem (proper separation!)

---

## Troubleshooting

### "Server Offline" (Red Indicator)

**Problem**: C server not running or API can't reach it

**Fix**:
```bash
# Check if C server is running
ps aux | grep file_server

# If not, start it
./build/file_server
```

### Dashboard Not Loading

**Problem**: CORS issues with `file://` protocol

**Fix**: Serve via HTTP instead
```bash
cd web_dashboard
python3 -m http.server 8080
# Open: http://localhost:8080
```

### Port Already in Use

**Problem**: Port 8888 or 5000 occupied

**Fix**:
```bash
# Find and kill processes
lsof -t -i:8888 | xargs kill
lsof -t -i:5000 | xargs kill
```

---

## Key Shortcuts

| Action | Command |
|--------|---------|
| **Build C server** | `make` |
| **Start C server** | `./build/file_server` |
| **Start API** | `cd api_layer && python3 app.py` |
| **Upload (CLI)** | `python3 client/client.py UPLOAD test_files/test1.txt` |
| **List files (CLI)** | `python3 client/client.py LIST` |
| **View locks (CLI)** | `python3 client/client.py LOCKS` |
| **View logs (CLI)** | `python3 client/client.py LOGS` |

---

## URLs

- **Web Dashboard**: `file:///.../web_dashboard/index.html`
- **API Health Check**: `http://localhost:5000/api/status`
- **C Server**: TCP port 8888 (not HTTP)

---

## File Paths

| Component | Location |
|-----------|----------|
| C Server | `server/file_server.c` |
| Python API | `api_layer/app.py` |
| Web UI | `web_dashboard/index.html` |
| Uploaded Files | `storage/` |
| Audit Logs | `logs/audit.log` |
| Test Files | `test_files/` |

---

## OS Concepts Demonstrated

| UI Feature | OS System Call | Where It Executes |
|------------|----------------|-------------------|
| Upload button | `open()`, `write()`, `fcntl(F_WRLCK)` | C server |
| Download button | `open()`, `read()`, `fcntl(F_RDLCK)` | C server |
| File list | `readdir()`, `stat()` | C server |
| Delete button | `unlink()` | C server |
| Lock visualization | `fcntl()` state tracking | C server |
| Audit timeline | Thread-safe `fprintf()` | C server |

**Critical**: Web layer NEVER executes OS operations directly!

---

## 5-Minute Presentation Flow

1. **Architecture** (1 min): Show README diagram, explain 3-tier
2. **Basic Ops** (1 min): Upload/download/delete via web
3. **Concurrency** (2 min): Demo lock rejection with slow upload
4. **Proof** (1 min): DevTools shows HTTP only, C terminal shows system calls

---

## Remember

✅ **This is still a C OS project** - all system calls in C
✅ **Web is observability layer** - like Prometheus/Grafana
✅ **Proper separation** - web never touches filesystem
✅ **Engineering-grade** - production-style architecture

**Questions?** Check:
- `WEB_DASHBOARD_GUIDE.md` - Full user guide
- `WEB_INTEGRATION_CHECKLIST.md` - Testing procedures
- `WEB_TRANSFORMATION_SUMMARY.md` - Complete technical documentation
