# 🎬 DETAILED DEMO PROCESS - COMPLETE WALKTHROUGH

**Complete step-by-step guide to demonstrate all features with different file sizes**

---

## 📋 TABLE OF CONTENTS

1. [Pre-Demo Setup](#pre-demo-setup)
2. [Feature 1: Basic Upload/Download](#feature-1-basic-uploaddownload)
3. [Feature 2: Multiple File Operations](#feature-2-multiple-file-operations)
4. [Feature 3: Concurrent Access & Locking](#feature-3-concurrent-access--locking)
5. [Feature 4: Audit Logs & Locks Inspection](#feature-4-audit-logs--locks-inspection)
6. [Feature 5: Delete Operations](#feature-5-delete-operations)
7. [Demo Summary](#demo-summary)

---

## PRE-DEMO SETUP

### Terminal Arrangement:
You'll need **3 terminals open**:

```
┌─────────────────────────────────────────┐
│  Terminal 1: SERVER                     │
│  (Running: make run)                    │
│  Status: Should show "Listening on 8888"│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Terminal 2: CLIENT (Main Demo)         │
│  (Running: python3 client/client.py)    │
│  Status: Interactive menu                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Terminal 3: CLIENT (Concurrent Demo)   │
│  (Optional - for concurrent access demo)│
│  Status: For 2nd client simultaneous    │
└─────────────────────────────────────────┘
```

---

### Step 0: Start Server

**Terminal 1:**
```bash
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
make run
```

**Expected Output:**
```
=== SECURE FILE MANAGEMENT SERVER ===
Operating System Concepts: File I/O, IPC, Locking, Deadlock Prevention

[SERVER] Listening on port 8888...
```

✅ **Server is now running and ready for clients**

### Step 0.5: Prep a Large File for Concurrency Demo (one-time)

**Terminal 1 or 2:**
```bash
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
dd if=/dev/zero bs=1M count=100 of=test_files/test_100mb.bin
```

This creates a ~100 MB file so the concurrent upload demo has PLENTY of time to overlap (4+ minutes with throttle).

---

## FEATURE 1: BASIC UPLOAD/DOWNLOAD

### Test File Sizes Used:
- **test1.txt** (~100 bytes) - Small file
- **test2.txt** (~200 bytes) - Medium file
- **test3.txt** (~1000 bytes) - Large file

---

### Step 1A: Upload Small File (test1.txt - ~100 bytes)

**Terminal 2:**
```bash
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
python3 client/client.py UPLOAD test_files/test1.txt
```

**Expected Output:**
```
[UPLOAD] Connecting to server...
[UPLOAD] Sent command: UPLOAD test1.txt 120
[UPLOAD] Server response: READY Send file data
[UPLOAD] Sending 120 bytes...
[UPLOAD] Progress: 100.0% (120/120 bytes)
[UPLOAD] Server response: SUCCESS File uploaded successfully!
[SUCCESS] File uploaded successfully!
```

**What This Demonstrates:**
- ✅ File I/O (reading local file)
- ✅ TCP socket communication
- ✅ Bounded transfer protocol (server knows exact size)
- ✅ File locking (write lock acquired)
- ✅ Proper completion

**Server Terminal Output (Terminal 1):**
```
[SERVER] New client connected from 127.0.0.1:xxxxx
[THREAD-1] Handling client
[THREAD-1] Received command: UPLOAD test1.txt 120
[UPLOAD] Acquiring write lock on test1.txt
[UPLOAD] Starting bounded transfer: 120 bytes
[UPLOAD] Write lock released on test1.txt
[UPLOAD] Successfully received 120 bytes
[THREAD-1] Client handler finished
```

✅ **File uploaded successfully!**

---

### Step 1B: Upload Medium File (test2.txt - ~200 bytes)

**Terminal 2:**
```bash
python3 client/client.py UPLOAD test_files/test2.txt
```

**Expected Output:**
```
[UPLOAD] Connecting to server...
[UPLOAD] Sent command: UPLOAD test2.txt 210
[UPLOAD] Server response: READY Send file data
[UPLOAD] Sending 210 bytes...
[UPLOAD] Progress: 100.0% (210/210 bytes)
[SUCCESS] File uploaded successfully!
```

✅ **Medium file uploaded!**

---

### Step 1C: Upload Large File (test3.txt - ~1000 bytes)

**Terminal 2:**
```bash
python3 client/client.py UPLOAD test_files/test3.txt
```

**Expected Output:**
```
[UPLOAD] Connecting to server...
[UPLOAD] Sent command: UPLOAD test3.txt 980
[UPLOAD] Server response: READY Send file data
[UPLOAD] Sending 980 bytes...
[UPLOAD] Progress: 50.0% (490/980 bytes)
[UPLOAD] Progress: 100.0% (980/980 bytes)
[SUCCESS] File uploaded successfully!
```

✅ **Large file uploaded!**

---

### Step 1D: Download Small File (test1.txt)

**Terminal 2:**
```bash
python3 client/client.py DOWNLOAD test1.txt downloaded_test1.txt
```

**Expected Output:**
```
[DOWNLOAD] Connecting to server...
[DOWNLOAD] Sent command: DOWNLOAD test1.txt
[DOWNLOAD] Server response: SUCCESS 120
[DOWNLOAD] Receiving 120 bytes...
[DOWNLOAD] Progress: 100.0% (120/120 bytes)
[SUCCESS] File downloaded successfully to downloaded_test1.txt
```

**What This Demonstrates:**
- ✅ File download with read lock (F_RDLCK)
- ✅ Multiple readers allowed (shared locks)
- ✅ Proper file transfer protocol

**Verify Download:**
```bash
cat downloaded_test1.txt
```

Should show the same content as test_files/test1.txt

✅ **File downloaded successfully!**

---

### Step 1E: Download Medium File (test2.txt)

**Terminal 2:**
```bash
python3 client/client.py DOWNLOAD test2.txt downloaded_test2.txt
```

**Expected Output:**
```
[DOWNLOAD] Connecting to server...
[DOWNLOAD] Sent command: DOWNLOAD test2.txt
[DOWNLOAD] Server response: SUCCESS 210
[DOWNLOAD] Receiving 210 bytes...
[DOWNLOAD] Progress: 100.0% (210/210 bytes)
[SUCCESS] File downloaded successfully to downloaded_test2.txt
```

✅ **Medium file downloaded!**

---

### Step 1F: Download Large File (test3.txt)

**Terminal 2:**
```bash
python3 client/client.py DOWNLOAD test3.txt downloaded_test3.txt
```

**Expected Output:**
```
[DOWNLOAD] Connecting to server...
[DOWNLOAD] Sent command: DOWNLOAD test3.txt
[DOWNLOAD] Server response: SUCCESS 980
[DOWNLOAD] Receiving 980 bytes...
[DOWNLOAD] Progress: 50.0% (490/980 bytes)
[DOWNLOAD] Progress: 100.0% (980/980 bytes)
[SUCCESS] File downloaded successfully to downloaded_test3.txt
```

✅ **Large file downloaded!**

---

## FEATURE 2: MULTIPLE FILE OPERATIONS

### Step 2A: List All Uploaded Files

**Terminal 2:**
```bash
python3 client/client.py LIST
```

**Expected Output:**
```
==================================================
SUCCESS
test1.txt (120 bytes)
test2.txt (210 bytes)
test3.txt (980 bytes)
==================================================
```

**What This Demonstrates:**
- ✅ Directory traversal (readdir)
- ✅ File stat operations
- ✅ Multiple files handling
- ✅ No locking needed for read-only operations

✅ **All 3 files shown!**

---

### Step 2B: Check Server Storage Directory

**Terminal 2:**
```bash
ls -lh storage/
```

**Expected Output:**
```
-rw-r--r-- 1 root root 120 Jan 27 10:30 test1.txt
-rw-r--r-- 1 root root 210 Jan 27 10:31 test2.txt
-rw-r--r-- 1 root root 980 Jan 27 10:32 test3.txt
```

✅ **Files physically stored on disk!**

---

### Step 2C: Check Metadata Files

**Terminal 2:**
```bash
ls -lh metadata/
cat metadata/test1.txt.meta
```

**Expected Output:**
```
Filename: test1.txt
Size: 120
UploadTime: Mon Jan 27 10:30:15 2026
```

**What This Demonstrates:**
- ✅ Metadata storage
- ✅ Thread-safe file operations
- ✅ Proper metadata management

✅ **Metadata created!**

---

## FEATURE 3: CONCURRENT ACCESS & LOCKING

### This Demonstrates Deadlock Avoidance!

---

### Step 3A: Client 1 Starts Upload (Large File + Throttled)

**Terminal 2:**
```bash
python3 client/client.py UPLOAD test_files/test_100mb.bin --slow 10
```

**Expected Output (note the MUCH larger size):**
```
[UPLOAD] Connecting to server...
[UPLOAD] Throttling enabled: 10 ms per chunk
[UPLOAD] Sent command: UPLOAD test_100mb.bin 104857600
[UPLOAD] Server response: READY Send file data
[UPLOAD] Sending 104857600 bytes...
[UPLOAD] Progress: 5.0% (5242880/104857600 bytes)
[UPLOAD] Progress: 10.0% (10485760/104857600 bytes)
... (keeps printing for ~4+ minutes) ...
```

⏸️ **Keep this running!** The 100MB file + 10ms throttle = 4+ minute upload. Perfect time for Client 2 to collide!

---

### Step 3B: Client 2 Tries Upload Same File (IMMEDIATELY)

**Terminal 3:** (Open new terminal while Terminal 2 is STILL UPLOADING - give it 10-20 seconds first)
```bash
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
python3 client/client.py UPLOAD test_files/test_100mb.bin
```

**Expected Output:**
```
[UPLOAD] Connecting to server...
[UPLOAD] Sent command: UPLOAD test_100mb.bin 104857600
[UPLOAD] Server response: ERROR
[ERROR] File is locked by another process
```

✅ **Client 2 REJECTED immediately!**

**What This Demonstrates:**
- ✅ **File Locking** - File locked by Client 1
- ✅ **Deadlock Avoidance** - Non-blocking lock (F_SETLK)
- ✅ **Circular Wait Prevention** - Client 2 rejected immediately
- ✅ **No Indefinite Blocking** - Client 2 gets response instantly

**Server Terminal Output (Terminal 1):**
```
[THREAD-1] Handling client
[THREAD-1] Received command: UPLOAD test3_large.bin 5242880
[UPLOAD] Acquiring write lock on test3_large.bin
[UPLOAD] Write lock released on test3_large.bin
[THREAD-1] Client handler finished

[THREAD-2] Handling client
[THREAD-2] Received command: UPLOAD test3_large.bin 5242880
[UPLOAD] Acquiring write lock on test3_large.bin
[LOCK] File already locked by another process
[THREAD-2] Client handler finished
```

✅ **Perfect deadlock avoidance demonstration!**

---

### Step 3C: Multiple Readers (Download While Upload)

Once Client 1 finishes upload, try multiple downloads:

**Terminal 2:**
```bash
python3 client/client.py DOWNLOAD test1.txt client1_download.txt
```

**Terminal 3:**
```bash
python3 client/client.py DOWNLOAD test1.txt client2_download.txt
```

**Expected Output (Both succeed):**
```
[SUCCESS] File downloaded successfully!
```

**What This Demonstrates:**
- ✅ **Read Locks (F_RDLCK)** - Multiple readers allowed
- ✅ **Shared Locks** - Both clients read simultaneously
- ✅ **Reader-Writer Pattern** - Read locks don't conflict

✅ **Multiple concurrent readers successful!**

---

## FEATURE 4: AUDIT LOGS & LOCKS INSPECTION

### Step 4A: View Current File Locks

**Terminal 2:**
```bash
python3 client/client.py LOCKS
```

**Expected Output:**
```
==================================================
SUCCESS
File Locks Status:
  LOCKED: test3.txt (PID: 12345)
==================================================
```

**Or if no locks:**
```
==================================================
SUCCESS
File Locks Status:
  No locked files
==================================================
```

**What This Demonstrates:**
- ✅ **fcntl() Lock Inspection** - Query lock status
- ✅ **Process ID Tracking** - Shows which process locked file
- ✅ **Lock Status Monitoring** - Real-time lock view

✅ **Lock inspection working!**

---

### Step 4B: View Complete Audit Log

**Terminal 2:**
```bash
python3 client/client.py LOGS
```

**Expected Output:**
```
==================================================
SUCCESS
=== AUDIT LOGS ===
[2026-01-27 10:30:15] OPERATION=UPLOAD FILE=test1.txt STATUS=SUCCESS DETAILS=Size: 120 bytes
[2026-01-27 10:30:45] OPERATION=DOWNLOAD FILE=test1.txt STATUS=SUCCESS DETAILS=Size: 120 bytes
[2026-01-27 10:31:20] OPERATION=UPLOAD FILE=test2.txt STATUS=SUCCESS DETAILS=Size: 210 bytes
[2026-01-27 10:31:45] OPERATION=UPLOAD FILE=test3.txt STATUS=SUCCESS DETAILS=Size: 980 bytes
[2026-01-27 10:32:15] OPERATION=UPLOAD FILE=test3.txt STATUS=FAILED DETAILS=File locked by another process
[2026-01-27 10:32:45] OPERATION=DOWNLOAD FILE=test1.txt STATUS=SUCCESS DETAILS=Size: 120 bytes
[2026-01-27 10:32:50] OPERATION=DOWNLOAD FILE=test1.txt STATUS=SUCCESS DETAILS=Size: 120 bytes
==================================================
```

**What This Demonstrates:**
- ✅ **Thread-Safe Logging** - Mutex protection
- ✅ **Audit Trail** - Complete operation history
- ✅ **Append-Only Log** - Never overwrites
- ✅ **Timestamps** - All operations timestamped
- ✅ **Success/Failure Tracking** - Both recorded

**Check Raw Log File:**
```bash
cat logs/audit.log
```

✅ **Audit logging working perfectly!**

---

## FEATURE 5: DELETE OPERATIONS

### Step 5A: Delete Small File (test1.txt)

**Terminal 2:**
```bash
python3 client/client.py DELETE test1.txt
```

**Expected Output:**
```
[DELETE] Connecting to server...
[DELETE] Sent command: DELETE test1.txt
[DELETE] Server response: SUCCESS File deleted successfully!
[SUCCESS] File deleted successfully!
```

**What This Demonstrates:**
- ✅ **File Deletion** - unlink() system call
- ✅ **Write Lock Before Delete** - Prevents deletion while in use
- ✅ **Proper Cleanup** - File physically removed

✅ **File deleted!**

---

### Step 5B: Verify Deletion

**Terminal 2:**
```bash
python3 client/client.py LIST
```

**Expected Output:**
```
==================================================
SUCCESS
test2.txt (210 bytes)
test3.txt (980 bytes)
==================================================
```

✅ **test1.txt no longer in list!**

---

### Step 5C: Try to Delete Non-Existent File

**Terminal 2:**
```bash
python3 client/client.py DELETE test1.txt
```

**Expected Output:**
```
[ERROR] File not found
```

**What This Demonstrates:**
- ✅ **Error Handling** - Proper error messages
- ✅ **State Management** - System knows what files exist

✅ **Error handling working!**

---

### Step 5D: Delete Remaining Files

**Terminal 2:**
```bash
python3 client/client.py DELETE test2.txt
python3 client/client.py DELETE test3.txt
```

**Verify All Deleted:**
```bash
python3 client/client.py LIST
```

**Expected Output:**
```
==================================================
SUCCESS
No files found
==================================================
```

✅ **All files deleted!**

---

## COMPLETE DEMO SEQUENCE (Copy-Paste Ready)

### For Quick Full Demo (5 minutes):

```bash
# Terminal 1: Start Server
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
make run

# Terminal 2: Run all operations
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"

# Step 1: Upload 3 files (different sizes)
python3 client/client.py UPLOAD test_files/test1.txt
sleep 1
python3 client/client.py UPLOAD test_files/test2.txt
sleep 1
python3 client/client.py UPLOAD test_files/test3.txt
sleep 1

# Step 2: List files
python3 client/client.py LIST
sleep 1

# Step 3: Download files
python3 client/client.py DOWNLOAD test1.txt downloaded1.txt
sleep 1
python3 client/client.py DOWNLOAD test2.txt downloaded2.txt
sleep 1
python3 client/client.py DOWNLOAD test3.txt downloaded3.txt
sleep 1

# Step 4: View logs
python3 client/client.py LOGS
sleep 1

# Step 5: View locks
python3 client/client.py LOCKS
sleep 1

# Step 6: Delete files
python3 client/client.py DELETE test1.txt
sleep 1
python3 client/client.py DELETE test2.txt
sleep 1
python3 client/client.py DELETE test3.txt
sleep 1

# Step 7: Verify empty
python3 client/client.py LIST
```

---

## DEMO SUMMARY

### Features Demonstrated:

| Feature | Command | File Size | Time |
|---------|---------|-----------|------|
| **Upload Small** | `UPLOAD test1.txt` | ~100 bytes | 1 sec |
| **Upload Medium** | `UPLOAD test2.txt` | ~200 bytes | 1 sec |
| **Upload Large** | `UPLOAD test3.txt` | ~1000 bytes | 1 sec |
| **List Files** | `LIST` | N/A | 1 sec |
| **Download Small** | `DOWNLOAD test1.txt` | ~100 bytes | 1 sec |
| **Download Medium** | `DOWNLOAD test2.txt` | ~200 bytes | 1 sec |
| **Download Large** | `DOWNLOAD test3.txt` | ~1000 bytes | 1 sec |
| **Concurrent Lock** | Two uploads same file (test_100mb.bin with --slow) | ~100 MB (throttled) | ~4-5 min |
| **View Locks** | `LOCKS` | N/A | 1 sec |
| **View Logs** | `LOGS` | N/A | 1 sec |
| **Delete** | `DELETE` | N/A | 3 sec |

**Total Demo Time:** ~20-25 minutes for full walkthrough (mostly from 100MB concurrent upload demo)

---

## OS CONCEPTS DEMONSTRATED

### During Demo, Point Out:

1. **UNIX File I/O** (Step 1)
   - open() - File opening
   - read() - Reading file
   - write() - Writing to server
   - stat() - File information

2. **TCP Sockets** (All steps)
   - Connection establishment
   - Data transfer
   - Proper closure

3. **File Locking** (Step 3)
   - F_WRLCK - Write lock acquired
   - F_RDLCK - Read lock for downloads
   - fcntl() - System call

4. **Deadlock Prevention** (Step 3B)
   - Bounded transfer (server knows size)
   - Client rejects immediately if locked
   - No circular wait

5. **Thread Safety** (Step 4)
   - Mutex for logging
   - Audit trail integrity
   - Concurrent client handling

6. **Critical Sections** (All)
   - Lock held only during write
   - Metadata/logs outside critical section

---

## VIVA POINTS TO EXPLAIN

While demonstrating:

1. **"See how Client 2 was rejected immediately?"**
   - Shows non-blocking lock (F_SETLK)
   - No deadlock because no circular wait
   - Deadlock avoidance in action

2. **"Notice the bounded transfer protocol"**
   - Server reads exactly N bytes
   - Never waits for socket EOF
   - Breaks hold-and-wait condition

3. **"The audit log shows everything"**
   - Thread-safe with mutex
   - Append-only (never overwrites)
   - Timestamps for all operations

4. **"Multiple readers work simultaneously"**
   - Read locks are shared
   - Only write blocks others
   - Reader-writer pattern

5. **"Lock is released immediately after write"**
   - Minimal critical section
   - Metadata updated outside lock
   - Improves concurrency

---

## TROUBLESHOOTING DURING DEMO

### Problem: "Cannot connect to server"
**Solution:** Check Terminal 1 is still running `make run`

### Problem: "File is locked" error
**This is expected!** Shows locking works. Just wait and try again.

### Problem: Server crashes
**Solution:**
```bash
killall file_server
make run
```

### Problem: Files not appearing in LIST
**Solution:** Check storage directory:
```bash
ls -lh storage/
```

---

## SUCCESS INDICATORS

✅ All operations complete without errors  
✅ Server shows lock acquisition/release messages  
✅ Concurrent access shows locking  
✅ Logs display all operations  
✅ Can explain each feature  
✅ Demo runs smoothly start to finish  

---

## QUICK REFERENCE - FILE SIZES

Create custom test files if needed:

```bash
# Create 1 KB file
dd if=/dev/zero bs=1024 count=1 of=test_files/test_1kb.txt

# Create 10 KB file
dd if=/dev/zero bs=1024 count=10 of=test_files/test_10kb.txt

# Create 100 KB file
dd if=/dev/zero bs=1024 count=100 of=test_files/test_100kb.txt
```

Then upload these larger files to show system performance with bigger transfers!

---

**This demo process covers ALL features and OS concepts. Use it for your evaluation!** 🎯
