# 🎓 VIVA PREPARATION GUIDE

## Core OS Concepts Questions

---

### Q1: What OS concepts does your project demonstrate?

**Answer:**
"Our project demonstrates 7 core OS concepts:
1. **UNIX File I/O** - Using open(), read(), write(), stat(), unlink()
2. **IPC** - TCP socket-based client-server communication
3. **File Locking** - fcntl() with F_RDLCK and F_WRLCK
4. **Deadlock Prevention** - Bounded resource allocation
5. **Deadlock Avoidance** - Non-blocking lock acquisition
6. **Thread Management** - pthread_create() for concurrent clients
7. **Synchronization** - Mutex for metadata and log protection"

---

### Q2: Explain your deadlock prevention strategy

**Answer:**
"We prevent deadlock using bounded file transfers which breaks the hold-and-wait condition:

1. **Protocol**: Client sends exact file size before data: `UPLOAD filename 1024`
2. **Server behavior**: Reads exactly N bytes, never waits for EOF
3. **Result**: Server never holds a lock while waiting indefinitely

Code location: `handle_upload()` function, line ~250"

---

### Q3: What is the difference between F_SETLK and F_SETLKW?

**Answer:**
"**F_SETLK** (non-blocking):
- Returns immediately if lock unavailable
- Returns -1 with errno EAGAIN/EACCES
- Safe for deadlock avoidance
- **We use this**

**F_SETLKW** (blocking):
- Waits indefinitely until lock available
- Can cause circular wait (deadlock)
- Requires timeout protection
- **We don't use this**

Code location: `acquire_file_lock()` function, line ~500"

---

### Q4: How does fcntl() file locking work?

**Answer:**
"fcntl() provides advisory file locking with struct flock:

```c
struct flock lock;
lock.l_type = F_WRLCK;      // Lock type (read/write)
lock.l_whence = SEEK_SET;   // Reference point
lock.l_start = 0;           // Start offset
lock.l_len = 0;             // Length (0 = entire file)
fcntl(fd, F_SETLK, &lock);  // Apply lock
```

**Lock types:**
- F_RDLCK: Shared (multiple readers)
- F_WRLCK: Exclusive (single writer)
- F_UNLCK: Release lock

**Key point**: Locks are per-process, automatically released when process exits."

---

### Q5: Explain your critical section design

**Answer:**
"We follow the principle of minimal critical sections:

**Correct order:**
1. Acquire lock ← START CRITICAL SECTION
2. Write file data ← ONLY THIS IS CRITICAL
3. Release lock ← END CRITICAL SECTION
4. Compute checksums (outside lock)
5. Update metadata (outside lock, uses mutex)
6. Write audit log (outside lock, uses mutex)

**Why?**
- File lock protects file data only
- Metadata uses separate mutex
- Minimizes lock hold time
- Improves concurrency

Code location: `handle_upload()`, lines 250-350"

---

### Q6: How do you handle multiple concurrent clients?

**Answer:**
"Using multi-threading:
1. Main thread accepts connections
2. Spawn new thread for each client: `pthread_create()`
3. Thread detached: `pthread_detach()` (auto cleanup)
4. Each thread runs independently

**Synchronization:**
- File locks (fcntl): Protect file data
- Mutexes: Protect metadata and logs
- No shared variables between threads except protected ones

Code location: `main()` function, lines 100-150"

---

### Q7: What system calls does your project use?

**Answer:**
"**File I/O:**
- open() - Open files
- read() - Read data
- write() - Write data
- close() - Close files
- stat() - Get file info
- unlink() - Delete files

**File Locking:**
- fcntl() - Lock/unlock files

**Networking:**
- socket() - Create socket
- bind() - Bind to address
- listen() - Listen for connections
- accept() - Accept connection

**Threading:**
- pthread_create() - Create thread
- pthread_detach() - Detach thread
- pthread_mutex_lock/unlock() - Mutex operations

**Process:**
- getpid() - Get process ID"

---

### Q8: How do you prevent deadlock with timeouts?

**Answer:**
"Timeout mechanism for deadlock recovery:

```c
time_t start = time(NULL);
while (reading) {
    if (difftime(time(NULL), start) > TIMEOUT) {
        // DEADLOCK RECOVERY
        release_file_lock(fd);
        unlink(incomplete_file);
        return ERROR;
    }
    // Continue reading...
}
```

**Purpose:**
- Detects hung operations
- Releases locks automatically
- Cleans up partial files
- Prevents resource leaks

**Timeout value:** 30 seconds (configurable)

Code location: `handle_upload()`, line ~280"

---

### Q9: What happens when two clients try to upload the same file?

**Answer:**
"**Scenario:**
- Client 1 starts upload → acquires write lock (F_WRLCK)
- Client 2 tries same file → lock attempt fails

**Client 1:**
```
[UPLOAD] Acquiring write lock on file.txt
[UPLOAD] Write lock acquired
[UPLOAD] Transferring data...
```

**Client 2:**
```
[ERROR] File is locked by another process
```

**Why?**
- F_WRLCK is exclusive
- Non-blocking lock returns error immediately
- Demonstrates deadlock avoidance

**Demo:** Can show with two terminals"

---

### Q10: Why use bounded file transfers?

**Answer:**
"**Problem without bounds:**
```
Server: while((n = read(socket, buf)) > 0)  // Waits for EOF
Client: [sends data but never closes socket]
Result: Server waits forever → DEADLOCK
```

**Solution with bounds:**
```
Client: UPLOAD file.txt 1024
Server: read exactly 1024 bytes, then stop
Result: Server never waits indefinitely
```

**Benefits:**
- Prevents hold-and-wait
- No dependence on socket closure
- Client misbehavior doesn't freeze server
- Demonstrates deadlock prevention from OS theory

Code location: `handle_upload()`, line ~250"

---

## Code Walkthrough Points

### Show handle_upload() function
1. **Line ~240**: Protocol parsing (filename + filesize)
2. **Line ~260**: Non-blocking lock acquisition
3. **Line ~270**: Bounded read loop (reads exactly filesize bytes)
4. **Line ~280**: Timeout check (deadlock recovery)
5. **Line ~320**: Lock released BEFORE metadata update
6. **Line ~340**: Thread-safe logging (outside critical section)

---

### Show acquire_file_lock() function
1. **Line ~505**: struct flock setup
2. **Line ~510**: F_SETLK (non-blocking)
3. **Line ~515**: Error handling (EAGAIN/EACCES)
4. **Line ~520**: Returns immediately if locked

---

### Show main() function
1. **Line ~100**: Socket creation
2. **Line ~120**: Bind and listen
3. **Line ~140**: Accept loop
4. **Line ~150**: Thread creation for each client
5. **Line ~160**: Thread detach (auto cleanup)

---

## Common Mistakes to Avoid

❌ **Don't say:** "We use file locks"
✅ **Say:** "We use fcntl() with F_SETLK for non-blocking advisory file locking"

❌ **Don't say:** "It prevents deadlock"
✅ **Say:** "Bounded transfers break the hold-and-wait condition, which is one of the four necessary conditions for deadlock"

❌ **Don't say:** "The server reads the file"
✅ **Say:** "The server uses the open() and read() system calls to perform low-level file I/O"

---

## Demo Flow for Evaluation

### 1. Start (30 seconds)
```bash
make run  # Show server starting
```
**Point out:** Socket creation, bind, listen

---

### 2. Simple Upload (1 minute)
```bash
python3 client/client.py UPLOAD test_files/test1.txt
```
**Point out in server output:**
- "Acquiring write lock"
- "Starting bounded transfer: N bytes"
- "Write lock released"

---

### 3. Concurrent Access (2 minutes)
**Terminal 2:**
```bash
python3 client/client.py UPLOAD test_files/test3.txt
```

**Terminal 3 (immediately):**
```bash
python3 client/client.py UPLOAD test_files/test3.txt
```

**Point out:** Client 2 rejected due to lock → Deadlock avoidance

---

### 4. View Logs (30 seconds)
```bash
python3 client/client.py LOGS
```
**Point out:** Thread-safe audit logging

---

## OS Theory Connections

| Implementation | OS Theory Concept |
|----------------|-------------------|
| Bounded transfers | Breaking hold-and-wait condition |
| F_SETLK | Non-blocking resource allocation (deadlock avoidance) |
| Timeout | Deadlock detection & recovery |
| pthread_create() | Process/thread management |
| pthread_mutex | Critical section protection |
| fcntl() | Synchronization primitive |
| Minimal critical section | Performance optimization |

---

## 5 Most Important Points

1. **Bounded file transfers** = Deadlock prevention
2. **Non-blocking locks (F_SETLK)** = Deadlock avoidance
3. **Timeout mechanism** = Deadlock recovery
4. **Minimal critical sections** = Performance
5. **Thread-safe operations** = Synchronization

**Master these 5 and you'll ace the viva!**

---

## Emergency Questions

### "Why not use fopen/fread/fwrite?"
**Answer:** "Those are high-level C library functions. We need to demonstrate UNIX system calls (open/read/write) which are the actual OS interface."

---

### "What if the lock is never released?"
**Answer:** "OS automatically releases locks when:
1. Process calls close(fd)
2. Process exits
3. Process crashes

fcntl() locks are tied to file descriptors and process lifetime."

---

### "Can you explain your code architecture?"
**Answer:** "Three layers:
1. **Client (Python)**: User interface, follows protocol
2. **Server (C)**: Core logic, OS system calls, file operations
3. **OS (Linux)**: Provides system calls, manages locks

Server is the heart - pure OS concepts, no high-level abstractions."

---

## Final Tips

✅ Always mention OS concept name when explaining
✅ Refer to specific line numbers in code
✅ Show terminal output during demo (it's very clear)
✅ Know difference between prevention/avoidance/recovery
✅ Can draw simple diagrams if asked
✅ Stay confident - your code is solid!

**Good luck! 🎯**
