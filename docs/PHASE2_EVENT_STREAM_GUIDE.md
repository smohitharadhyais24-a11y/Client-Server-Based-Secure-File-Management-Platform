# PHASE 2 Implementation Guide: OS Event Stream in C Server

## Overview
Modify the existing C server to emit structured OS events to `logs/events.log` file.
These events are parsed by Flask API and displayed in real-time on the web dashboard.

## Event Format
```
[YYYY-MM-DD HH:MM:SS] EVENT_TYPE filename lock_type pid user status
```

**Example events:**
```
[2026-01-27 22:31:05] UPLOAD report.txt WRITE 4321 user1 SUCCESS
[2026-01-27 22:31:06] LOCK_REJECT report.txt WRITE 4322 user2 BLOCKED
[2026-01-27 22:31:35] TIMEOUT report.txt WRITE 4321 user1 DEADLOCK_RECOVERY
[2026-01-27 22:31:40] DOWNLOAD report.txt READ 4323 user2 SUCCESS
[2026-01-27 22:31:45] AUTH_FAIL - - 4324 unknown FAILED
```

## Event Types
- `UPLOAD` - File upload started
- `DOWNLOAD` - File download started
- `DELETE` - File deletion
- `LOCK_ACQUIRED` - File lock acquired
- `LOCK_REJECTED` - Lock request rejected (file already locked)
- `LOCK_RELEASED` - File lock released
- `TIMEOUT` - Upload/operation timeout
- `AUTH_FAIL` - Authentication failure
- `HASH_VERIFY` - Hash verification result
- `DEADLOCK_RECOVERY` - Timeout-based recovery

## Implementation Steps

### Step 1: Add Event Logging Mutex
In `server/file_server.c`, add to global declarations:
```c
pthread_mutex_t events_log_mutex = PTHREAD_MUTEX_INITIALIZER;
#define EVENTS_LOG_FILE "logs/events.log"
```

### Step 2: Create Event Logging Function
```c
void log_event(const char *event_type, const char *filename, const char *lock_type, 
               pid_t pid, const char *user, const char *status) {
    pthread_mutex_lock(&events_log_mutex);
    
    FILE *f = fopen(EVENTS_LOG_FILE, "a");
    if (!f) {
        pthread_mutex_unlock(&events_log_mutex);
        return;
    }
    
    time_t now = time(NULL);
    struct tm *timeinfo = localtime(&now);
    char timestamp[32];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", timeinfo);
    
    fprintf(f, "[%s] %s %s %s %d %s %s\n", 
            timestamp, event_type, filename, lock_type, pid, user, status);
    
    fclose(f);
    pthread_mutex_unlock(&events_log_mutex);
}
```

### Step 3: Call log_event() at Key Points

**In handle_upload():**
```c
// When upload starts
log_event("UPLOAD", filename, "WRITE", getpid(), client_user, "INITIATED");

// When lock acquired
log_event("LOCK_ACQUIRED", filename, "WRITE", getpid(), client_user, "SUCCESS");

// If lock fails
log_event("LOCK_REJECTED", filename, "WRITE", other_pid, client_user, "BLOCKED");

// When timeout occurs
log_event("TIMEOUT", filename, "WRITE", getpid(), client_user, "DEADLOCK_RECOVERY");

// On success
log_event("UPLOAD", filename, "WRITE", getpid(), client_user, "SUCCESS");
```

**In handle_download():**
```c
log_event("DOWNLOAD", filename, "READ", getpid(), client_user, "INITIATED");
log_event("LOCK_ACQUIRED", filename, "READ", getpid(), client_user, "SUCCESS");
log_event("DOWNLOAD", filename, "READ", getpid(), client_user, "SUCCESS");
```

**In handle_delete():**
```c
log_event("DELETE", filename, "WRITE", getpid(), client_user, "INITIATED");
log_event("LOCK_ACQUIRED", filename, "WRITE", getpid(), client_user, "SUCCESS");
log_event("DELETE", filename, "WRITE", getpid(), client_user, "SUCCESS");
```

**In authenticate_client():**
```c
if (auth_failed) {
    log_event("AUTH_FAIL", "-", "-", getpid(), "unknown", "FAILED");
}
```

### Step 4: Ensure Backward Compatibility
- Keep existing audit.log functionality (for text-based logs)
- Add events.log in parallel (for structured, machine-readable logs)
- Do NOT remove existing functionality

### Step 5: Testing Events.log
After modification, test:
```bash
# Start C server
./build/file_server

# In another terminal, perform operations
curl -X POST http://localhost:5000/api/upload -F 'file=@test.txt'

# Check events.log was created and contains events
cat logs/events.log
# Should see structured events
```

## Flask API Integration
The Flask API already has:
- `@app.route('/api/events')` endpoint that reads events.log
- `parse_event_line()` function that parses each event

No Flask changes needed - just ensure C server writes to `../logs/events.log`.

## Files to Modify
1. `server/file_server.c` - Add event logging
2. `Makefile` - Ensure logs directory created

## Files NOT to Modify
1. `api_layer/app.py` - Already has event parsing
2. `web_dashboard/` - Will be updated in Phase 4
3. Any existing OS logic - Only ADD event logging

## Validation Checklist
- [ ] events.log file is created in logs/ directory
- [ ] Each operation generates structured events
- [ ] Mutex protects all writes (no concurrent corruption)
- [ ] Format matches: `[timestamp] EVENT_TYPE filename lock_type pid user status`
- [ ] Flask API can parse all event types
- [ ] Backward compatible: audit.log still works
- [ ] No performance degradation from event logging
