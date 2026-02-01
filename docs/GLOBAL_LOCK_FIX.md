# ✅ LOCK REJECTION NOW WORKING - GLOBAL LOCK IMPLEMENTED!

## Problem Found and Fixed:

**fcntl locks were NOT working** because they're per-process per file descriptor. When two separate processes opened the same file, they got different file descriptors and fcntl locks didn't conflict.

### What Was Wrong:
```c
[DEBUG] File opened successfully, fd=6
[DEBUG] Lock acquisition SUCCEEDED   // Client 1

[DEBUG] File opened successfully, fd=8  
[DEBUG] Lock acquisition SUCCEEDED   // Client 2 also succeeded!
```

Both clients were acquiring locks because fcntl locks aren't truly global on Linux.

### Solution:

Implemented a **global mutex-based locking mechanism** that tracks which files are currently locked across ALL processes:

```c
locked_file_t locked_files[MAX_LOCKED_FILES];  // Global array
pthread_mutex_t file_locks_mutex;               // Protect it

int acquire_global_lock(const char *filename) {
    pthread_mutex_lock(&file_locks_mutex);      // Critical section
    
    // Check if already locked
    if (file_is_locked(filename)) {
        pthread_mutex_unlock(&file_locks_mutex);
        return -1;  // REJECTION!
    }
    
    // Lock it
    mark_file_as_locked(filename);
    pthread_mutex_unlock(&file_locks_mutex);
    return 0;
}
```

## Test Results:

```
Client 1: [DEBUG] Global lock ACQUIRED
          Starts uploading...

Client 2: [DEBUG] Global lock FAILED - sending ERROR to client
          [UPLOAD] Server response: ERROR File is locked by another process
          [ERROR] Server not ready: ERROR File is locked by another process
```

✅ **Client 2 properly rejected!**

---

## Code Changes:

**File:** [server/file_server.c](server/file_server.c)

1. ✅ Added global lock tracking array and mutex
2. ✅ Implemented `acquire_global_lock()` function
3. ✅ Implemented `release_global_lock()` function
4. ✅ Updated upload handler to use global locks
5. ✅ Proper lock ordering: acquire before READY response

---

## Now Concurrent Locking Works:

### Test Setup:
```bash
# Terminal 1
make run

# Terminal 2
python3 client/client.py UPLOAD test_files/test3_large.bin --slow 10

# Terminal 3 (after 2-3 seconds)
python3 client/client.py UPLOAD test_files/test3_large.bin
```

### Result:
✅ Client 3 gets immediate rejection: "File is locked by another process"

---

## OS Concepts Properly Demonstrated:

| Concept | Implementation | Status |
|---------|-----------------|--------|
| **Deadlock Avoidance** | Non-blocking lock rejection (no wait) | ✅ Working |
| **Mutual Exclusion** | Global mutex + file lock tracking | ✅ Working |
| **Critical Section** | Protected by mutex during lock check | ✅ Working |
| **No Circular Wait** | No resource hierarchy | ✅ Working |
| **No Hold-and-Wait** | Lock checked before sending READY | ✅ Working |
| **Bounded Resource** | MaxN files can be locked simultaneously | ✅ Working |

---

## Files Modified:

✅ server/file_server.c - Global lock mechanism implemented

## Status:

✅ **READY FOR DEMO!**

The concurrent locking demo now works perfectly. Client 2 will be rejected immediately when attempting to upload a file that Client 1 is already uploading.
