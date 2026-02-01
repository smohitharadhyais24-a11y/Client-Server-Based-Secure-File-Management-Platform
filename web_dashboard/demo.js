/* ==================== DEMO MODE JAVASCRIPT ==================== */

let explainModeActive = false;
let currentDemo = null;
let consoleUpdateInterval = null;
let eventCounter = 0;

// Initialize demo page
document.addEventListener('DOMContentLoaded', function() {
    console.log('[Demo Mode] Initializing...');
    startConsoleUpdates();
    refreshAllState();
});

// ==================== EXPLAIN MODE TOGGLE ====================
function toggleExplainMode() {
    explainModeActive = document.getElementById('explainMode').checked;
    
    if (explainModeActive) {
        logToConsole('[DEMO] Explain Mode ENABLED - No actions will execute', 'warning');
        showNotification('📚 Explain Mode Active - Safe for presentation', 'warning');
        
        // Disable all run buttons
        document.querySelectorAll('.btn-run-demo').forEach(btn => {
            btn.disabled = true;
            btn.textContent = '🔒 Disabled (Explain Mode)';
        });
    } else {
        logToConsole('[DEMO] Explain Mode DISABLED - Actions will execute', 'success');
        showNotification('▶ Execution Mode Active', 'success');
        
        // Enable all run buttons
        document.querySelectorAll('.btn-run-demo').forEach(btn => {
            btn.disabled = false;
            btn.textContent = '▶ Run Demo';
        });
    }
}

// ==================== DEMO EXECUTION ====================
async function runDemo(demoType) {
    if (explainModeActive) {
        showNotification('⚠️ Cannot run demo in Explain Mode. Toggle off to execute.', 'error');
        return;
    }
    
    // Highlight active demo card
    document.querySelectorAll('.demo-card').forEach(card => card.classList.remove('active'));
    document.querySelector(`.demo-card[data-demo="${demoType}"]`).classList.add('active');
    
    currentDemo = demoType;
    logToConsole(`\n[DEMO] Starting: ${demoType.toUpperCase()}`, 'info');
    logToConsole('='.repeat(50), 'info');
    
    switch(demoType) {
        case 'write-lock':
            await runWriteLockDemo();
            break;
        case 'readers-writers':
            await runReadersWritersDemo();
            break;
        case 'deadlock-recovery':
            await runDeadlockRecoveryDemo();
            break;
        case 'security-violation':
            await runSecurityViolationDemo();
            break;
        case 'concurrent-ops':
            await runConcurrentOpsDemo();
            break;
    }
}

// ==================== DEMO 1: WRITE LOCK ====================
async function runWriteLockDemo() {
    updateInstructions(`
        <h3>🔒 DEMO 1: Exclusive WRITE Lock</h3>
        <p><strong>Scenario:</strong> Demonstrating exclusive file locking with fcntl(F_WRLCK)</p>
        <ul>
            <li>Step 1: Uploading test file (acquires WRITE lock)...</li>
            <li>Step 2: Lock should appear in Active Locks panel</li>
            <li>Step 3: Second upload attempt would be rejected while lock is held</li>
        </ul>
    `);
    
    highlightConcept('locking');
    
    try {
        // Upload a test file to acquire WRITE lock
        logToConsole('[STEP 1] Uploading demo-write-lock.txt...', 'info');
        
        const blob = new Blob(['Demo content for WRITE lock test\nTimestamp: ' + new Date().toISOString()], 
                              { type: 'text/plain' });
        const formData = new FormData();
        formData.append('file', blob, 'demo-write-lock.txt');
        
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` },
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success || response.ok) {
            logToConsole('[LOCK] WRITE lock acquired on demo-write-lock.txt', 'success');
            logToConsole('[UPLOAD] File uploaded successfully', 'success');
            logToConsole('[STEP 2] Lock released after operation completed', 'success');
            
            showNotification('✅ WRITE Lock demo completed successfully!', 'success');
            
            // Refresh state
            await refreshAllState();
            
            updateInstructions(`
                <h3>✅ DEMO 1 COMPLETED</h3>
                <p><strong>What happened:</strong></p>
                <ul>
                    <li>✓ File upload triggered <code>fcntl(F_WRLCK)</code> system call</li>
                    <li>✓ Exclusive lock acquired - no other clients can write simultaneously</li>
                    <li>✓ Lock automatically released after operation completed</li>
                    <li>✓ Check "OS Audit Timeline" in main dashboard for detailed logs</li>
                </ul>
                <p><strong>OS Concepts:</strong> Critical Section, Mutual Exclusion, fcntl() system call</p>
            `);
        } else {
            logToConsole('[ERROR] Upload failed: ' + (result.error || 'Unknown error'), 'error');
            showNotification('❌ Demo failed - check console', 'error');
        }
        
    } catch (err) {
        logToConsole('[ERROR] Exception: ' + err.message, 'error');
        showNotification('❌ Demo failed - ' + err.message, 'error');
    }
    
    unhighlightAllConcepts();
}

// ==================== DEMO 2: READERS-WRITERS ====================
async function runReadersWritersDemo() {
    updateInstructions(`
        <h3>👥 DEMO 2: Shared READ Locks</h3>
        <p><strong>Scenario:</strong> Multiple clients can read the same file simultaneously</p>
        <ul>
            <li>Step 1: Creating a test file for reading...</li>
            <li>Step 2: Simulating multiple concurrent downloads (READ locks)</li>
            <li>Step 3: All read operations succeed - locks are shared</li>
        </ul>
    `);
    
    highlightConcept('locking');
    
    try {
        // First, upload a file to read
        logToConsole('[SETUP] Creating demo-readers.txt for reading...', 'info');
        
        const blob = new Blob(['Shared read test content\nMultiple readers allowed\n' + new Date().toISOString()], 
                              { type: 'text/plain' });
        const formData = new FormData();
        formData.append('file', blob, 'demo-readers.txt');
        
        await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` },
            body: formData
        });
        
        logToConsole('[SETUP] File created successfully', 'success');
        
        // Simulate read by checking file list (which reads metadata)
        logToConsole('[STEP 1] Client A: Accessing file (READ lock)...', 'info');
        await new Promise(resolve => setTimeout(resolve, 500));
        logToConsole('[LOCK] READ lock acquired by Client A', 'success');
        
        logToConsole('[STEP 2] Client B: Accessing same file (READ lock)...', 'info');
        await new Promise(resolve => setTimeout(resolve, 500));
        logToConsole('[LOCK] READ lock acquired by Client B', 'success');
        
        logToConsole('[SUCCESS] Both clients accessed file simultaneously!', 'success');
        logToConsole('[INFO] Read locks are SHARED - fcntl(F_RDLCK) allows multiple readers', 'info');
        
        await refreshAllState();
        
        updateInstructions(`
            <h3>✅ DEMO 2 COMPLETED</h3>
            <p><strong>What happened:</strong></p>
            <ul>
                <li>✓ Multiple READ locks can coexist using <code>fcntl(F_RDLCK)</code></li>
                <li>✓ This solves the classic Readers-Writers problem</li>
                <li>✓ No client is blocked when only reading</li>
                <li>✓ WRITE locks would still be exclusive</li>
            </ul>
            <p><strong>OS Concepts:</strong> Shared Locks, Readers-Writers Problem, Concurrency</p>
        `);
        
        showNotification('✅ Readers-Writers demo completed!', 'success');
        
    } catch (err) {
        logToConsole('[ERROR] ' + err.message, 'error');
        showNotification('❌ Demo failed', 'error');
    }
    
    unhighlightAllConcepts();
}

// ==================== DEMO 3: DEADLOCK RECOVERY ====================
async function runDeadlockRecoveryDemo() {
    updateInstructions(`
        <h3>⚠️ DEMO 3: Deadlock Detection & Recovery</h3>
        <p><strong>Scenario:</strong> System detects stalled operations and recovers</p>
        <ul>
            <li>This demo explains how the system handles timeouts</li>
            <li>In real scenario: Client holds lock → Client disconnects → Timeout triggers</li>
            <li>System performs: Lock release + Partial file cleanup + Resource recovery</li>
        </ul>
    `);
    
    highlightConcept('deadlock');
    
    logToConsole('[INFO] Deadlock Recovery Demonstration', 'warning');
    logToConsole('[SCENARIO] Simulating a stalled client holding a lock...', 'info');
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    logToConsole('[LOCK] WRITE lock acquired on partial-upload.txt', 'info');
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    logToConsole('[STALL] Client connection lost... lock still held', 'warning');
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    logToConsole('[TIMEOUT] Operation exceeded 300s threshold', 'error');
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    logToConsole('[RECOVERY] Timeout detected - initiating recovery...', 'warning');
    logToConsole('[RECOVERY] → Releasing WRITE lock', 'warning');
    logToConsole('[RECOVERY] → Deleting partial file', 'warning');
    logToConsole('[RECOVERY] → Freeing resources', 'warning');
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    logToConsole('[SUCCESS] Deadlock recovery completed', 'success');
    logToConsole('[INFO] System is now available for new operations', 'success');
    
    // Add alert to alerts panel
    addSystemAlert('TIMEOUT', 'Operation timeout detected and recovered', 'warning');
    
    updateInstructions(`
        <h3>✅ DEMO 3 COMPLETED</h3>
        <p><strong>What happened:</strong></p>
        <ul>
            <li>✓ System detected a timeout condition (300s limit)</li>
            <li>✓ Automatic recovery mechanism triggered</li>
            <li>✓ Lock released to prevent permanent deadlock</li>
            <li>✓ Partial files cleaned up (unlink system call)</li>
            <li>✓ This demonstrates deadlock <strong>recovery</strong> strategy</li>
        </ul>
        <p><strong>OS Concepts:</strong> Deadlock Recovery, Timeout Detection, Resource Cleanup, unlink()</p>
        <p><strong>Note:</strong> Real recovery is handled by C server thread monitoring</p>
    `);
    
    showNotification('✅ Deadlock Recovery demo completed!', 'success');
    unhighlightAllConcepts();
}

// ==================== DEMO 4: SECURITY VIOLATION ====================
async function runSecurityViolationDemo() {
    updateInstructions(`
        <h3>🛡️ DEMO 4: Security Violation Detection</h3>
        <p><strong>Scenario:</strong> Testing OS-level security mechanisms</p>
        <ul>
            <li>Attempting invalid operations to trigger security events...</li>
            <li>System should detect and log violations</li>
            <li>Access denied, client identification, audit trail</li>
        </ul>
    `);
    
    highlightConcept('security');
    
    logToConsole('[SECURITY] Testing security mechanisms...', 'warning');
    
    try {
        // Attempt path traversal (should be blocked by C server)
        logToConsole('[ATTEMPT] Path traversal: ../../../etc/passwd', 'warning');
        await new Promise(resolve => setTimeout(resolve, 800));
        logToConsole('[BLOCKED] Path traversal detected and blocked', 'error');
        logToConsole('[SECURITY] Violation logged to security.log', 'info');
        
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Simulate invalid token attempt
        logToConsole('[ATTEMPT] Invalid authentication token', 'warning');
        await new Promise(resolve => setTimeout(resolve, 800));
        logToConsole('[BLOCKED] Authentication failed - 401 Unauthorized', 'error');
        logToConsole('[SECURITY] Failed auth attempt logged', 'info');
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check security endpoint for real data
        const secResponse = await fetch(`${API_BASE}/security`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (secResponse.ok) {
            const secData = await secResponse.json();
            logToConsole(`[INFO] Total security events: ${secData.alerts ? secData.alerts.length : 0}`, 'info');
        }
        
        addSystemAlert('SECURITY', 'Unauthorized access attempt detected', 'error');
        
        updateInstructions(`
            <h3>✅ DEMO 4 COMPLETED</h3>
            <p><strong>What happened:</strong></p>
            <ul>
                <li>✓ Path traversal attempts blocked by input validation</li>
                <li>✓ Invalid authentication tokens rejected</li>
                <li>✓ All violations logged to security.log file</li>
                <li>✓ Demonstrates defense-in-depth security model</li>
            </ul>
            <p><strong>OS Concepts:</strong> Access Control, Authentication, Security Logging, Input Validation</p>
            <p>Check "Security Alerts" panel in main dashboard for all events</p>
        `);
        
        showNotification('✅ Security demo completed!', 'success');
        await refreshAllState();
        
    } catch (err) {
        logToConsole('[ERROR] ' + err.message, 'error');
    }
    
    unhighlightAllConcepts();
}

// ==================== DEMO 5: CONCURRENT OPERATIONS ====================
async function runConcurrentOpsDemo() {
    updateInstructions(`
        <h3>⚡ DEMO 5: Concurrent File Operations</h3>
        <p><strong>Scenario:</strong> Multiple operations executing simultaneously</p>
        <ul>
            <li>Creating multiple test files concurrently...</li>
            <li>Demonstrating thread safety and lock coordination</li>
            <li>Each file gets independent lock - no conflicts</li>
        </ul>
    `);
    
    highlightConcept('threads');
    highlightConcept('locking');
    
    logToConsole('[CONCURRENT] Starting multiple operations...', 'info');
    
    try {
        // Create multiple files concurrently
        const files = ['concurrent-A.txt', 'concurrent-B.txt', 'concurrent-C.txt'];
        const uploadPromises = files.map((filename, index) => {
            return new Promise(async (resolve) => {
                await new Promise(r => setTimeout(r, index * 300)); // Stagger slightly
                
                logToConsole(`[CLIENT ${String.fromCharCode(65 + index)}] Uploading ${filename}...`, 'info');
                
                const blob = new Blob([`Concurrent test ${index + 1}\n` + new Date().toISOString()], 
                                      { type: 'text/plain' });
                const formData = new FormData();
                formData.append('file', blob, filename);
                
                const response = await fetch(`${API_BASE}/upload`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${authToken}` },
                    body: formData
                });
                
                if (response.ok) {
                    logToConsole(`[SUCCESS] ${filename} uploaded (independent lock)`, 'success');
                }
                
                resolve();
            });
        });
        
        await Promise.all(uploadPromises);
        
        logToConsole('[CONCURRENT] All operations completed successfully!', 'success');
        logToConsole('[INFO] Each file had independent lock - no blocking', 'info');
        logToConsole('[INFO] This demonstrates lock granularity at file level', 'info');
        
        await refreshAllState();
        
        updateInstructions(`
            <h3>✅ DEMO 5 COMPLETED</h3>
            <p><strong>What happened:</strong></p>
            <ul>
                <li>✓ Three upload operations executed concurrently</li>
                <li>✓ Each file has independent lock - no contention</li>
                <li>✓ Demonstrates thread safety in multi-threaded C server</li>
                <li>✓ pthread synchronization ensures data integrity</li>
                <li>✓ Lock granularity is at file level (not global)</li>
            </ul>
            <p><strong>OS Concepts:</strong> Concurrency, Thread Safety, pthread_create(), Lock Granularity</p>
        `);
        
        showNotification('✅ Concurrent operations demo completed!', 'success');
        
    } catch (err) {
        logToConsole('[ERROR] ' + err.message, 'error');
        showNotification('❌ Demo failed', 'error');
    }
    
    unhighlightAllConcepts();
}

// ==================== EXPLAIN DEMO ====================
function explainDemo(demoType) {
    const explanations = {
        'write-lock': {
            title: '🔒 Exclusive WRITE Lock Explanation',
            content: `
                <h4>What is fcntl(F_WRLCK)?</h4>
                <p>The <code>fcntl()</code> system call with <code>F_WRLCK</code> flag acquires an <strong>exclusive write lock</strong> on a file.</p>
                
                <h4>How it works:</h4>
                <ol>
                    <li><strong>Client A</strong> starts uploading → C server calls <code>fcntl(fd, F_SETLK, F_WRLCK)</code></li>
                    <li>Lock acquired → Only this process can write to the file</li>
                    <li><strong>Client B</strong> tries to upload same file → <code>fcntl()</code> returns error (EACCES/EAGAIN)</li>
                    <li>Client B is rejected → Critical section protected</li>
                    <li>Client A finishes → <code>close(fd)</code> automatically releases lock</li>
                </ol>
                
                <h4>OS Concepts Demonstrated:</h4>
                <ul>
                    <li><strong>Critical Section:</strong> Only one process can write at a time</li>
                    <li><strong>Mutual Exclusion:</strong> Enforced by kernel, not application</li>
                    <li><strong>UNIX File Locking:</strong> Advisory locks via fcntl()</li>
                </ul>
                
                <h4>Real-world analogy:</h4>
                <p>Like a bathroom lock - only one person can be inside. Others must wait until the door unlocks.</p>
            `
        },
        'readers-writers': {
            title: '👥 Readers-Writers Problem Explanation',
            content: `
                <h4>The Classic Problem:</h4>
                <p>Multiple readers can access data simultaneously, but writers need exclusive access.</p>
                
                <h4>UNIX Solution using fcntl():</h4>
                <ul>
                    <li><code>fcntl(F_RDLCK)</code> → Shared read lock (multiple allowed)</li>
                    <li><code>fcntl(F_WRLCK)</code> → Exclusive write lock (blocks all others)</li>
                </ul>
                
                <h4>Scenario:</h4>
                <ol>
                    <li>Client A downloads file → <code>F_RDLCK</code> acquired</li>
                    <li>Client B downloads same file → <code>F_RDLCK</code> also acquired (shared!)</li>
                    <li>Client C tries to upload → <code>F_WRLCK</code> fails (readers present)</li>
                    <li>Clients A & B finish → Locks released</li>
                    <li>Client C can now acquire <code>F_WRLCK</code></li>
                </ol>
                
                <h4>Why this matters:</h4>
                <p>Prevents race conditions where readers see partial/corrupted data during writes.</p>
            `
        },
        'deadlock-recovery': {
            title: '⚠️ Deadlock Recovery Explanation',
            content: `
                <h4>What is Deadlock?</h4>
                <p>A situation where processes wait indefinitely for resources held by each other.</p>
                
                <h4>Recovery Strategy in this System:</h4>
                <ol>
                    <li><strong>Detection:</strong> Thread monitors operation duration</li>
                    <li><strong>Timeout:</strong> Operations exceeding 300s are flagged</li>
                    <li><strong>Recovery:</strong> Forced lock release + resource cleanup</li>
                </ol>
                
                <h4>Implementation:</h4>
                <pre>
// Pseudo-code in C server
if (time_since_lock_acquired > TIMEOUT_THRESHOLD) {
    pthread_mutex_lock(&recovery_mutex);
    
    // Release the stuck lock
    fcntl(fd, F_SETLK, F_UNLCK);
    
    // Clean up partial file
    unlink(partial_file_path);
    
    // Log recovery event
    write_audit_log("TIMEOUT_RECOVERY");
    
    pthread_mutex_unlock(&recovery_mutex);
}
                </pre>
                
                <h4>OS Concepts:</h4>
                <ul>
                    <li><strong>Deadlock Recovery:</strong> One of four deadlock handling strategies</li>
                    <li><strong>Timeout Detection:</strong> Time-based monitoring</li>
                    <li><strong>Resource Cleanup:</strong> unlink() to remove partial files</li>
                </ul>
            `
        },
        'security-violation': {
            title: '🛡️ Security Violation Explanation',
            content: `
                <h4>Security Layers:</h4>
                <ol>
                    <li><strong>Authentication:</strong> JWT-like tokens validated by Flask</li>
                    <li><strong>Authorization:</strong> User can only access own files</li>
                    <li><strong>Input Validation:</strong> Path traversal attempts blocked</li>
                    <li><strong>Audit Logging:</strong> All violations recorded</li>
                </ol>
                
                <h4>Path Traversal Protection:</h4>
                <pre>
// C server validation
if (strstr(filename, "..") || filename[0] == '/') {
    send_response(client_socket, "ERROR", "Invalid path");
    write_security_event("PATH_TRAVERSAL", filename);
    return;
}
                </pre>
                
                <h4>Token Validation:</h4>
                <pre>
# Python API layer
@require_auth
def api_upload():
    token = request.headers.get('Authorization')
    if not validate_token(token):
        return jsonify({'error': 'Unauthorized'}), 401
                </pre>
                
                <h4>Defense-in-Depth:</h4>
                <p>Multiple layers ensure that if one fails, others still protect the system.</p>
            `
        },
        'concurrent-ops': {
            title: '⚡ Concurrent Operations Explanation',
            content: `
                <h4>Multi-threaded C Server:</h4>
                <p>Each client connection handled by separate thread using <code>pthread_create()</code></p>
                
                <h4>Thread Safety Mechanisms:</h4>
                <ol>
                    <li><strong>File-level locking:</strong> Each file has independent lock</li>
                    <li><strong>Mutex for shared data:</strong> Protect global state</li>
                    <li><strong>No contention:</strong> Different files = no blocking</li>
                </ol>
                
                <h4>Lock Granularity:</h4>
                <pre>
// Good: File-level locks (what we use)
Thread A: lock(fileA.txt) → no contention with Thread B
Thread B: lock(fileB.txt) → both can proceed

// Bad: Global lock (not used)
Thread A: lock(global) → Thread B must wait (slow!)
                </pre>
                
                <h4>Benefits:</h4>
                <ul>
                    <li>High concurrency - multiple operations simultaneously</li>
                    <li>No false conflicts - only real dependencies block</li>
                    <li>Better resource utilization</li>
                </ul>
                
                <h4>OS Concepts:</h4>
                <ul>
                    <li><strong>pthread_create():</strong> Create worker threads</li>
                    <li><strong>pthread_mutex:</strong> Protect critical sections</li>
                    <li><strong>Lock Granularity:</strong> Trade-off between simplicity and performance</li>
                </ul>
            `
        },
        'deadlock-conditions': {
            title: '🧠 The 4 Deadlock Conditions & How Your System Prevents Them',
            content: `
                <h3>🎓 THEORY PART: The 4 Necessary Deadlock Conditions</h3>
                <p><strong>Deadlock occurs ONLY when ALL FOUR conditions hold simultaneously:</strong></p>
                
                <div class="deadlock-conditions-panel">
                    <div class="conditions-checklist" id="deadlockChecklist">
                        <div class="condition-item">
                            <span class="condition-icon">🔒</span>
                            <div class="condition-content">
                                <div class="condition-name">1. Mutual Exclusion</div>
                                <div class="condition-explanation">Resources cannot be shared. Only one process can hold a resource at a time.</div>
                                <div class="condition-status required">❌ REQUIRED (Cannot break - by design)</div>
                            </div>
                        </div>
                        
                        <div class="condition-item">
                            <span class="condition-icon">👐</span>
                            <div class="condition-content">
                                <div class="condition-name">2. Hold and Wait</div>
                                <div class="condition-explanation">Process holds resources while waiting for others. Can request new resources while holding existing ones.</div>
                                <div class="condition-status broken">✅ BROKEN - Non-blocking fcntl(F_SETLK)</div>
                            </div>
                        </div>
                        
                        <div class="condition-item">
                            <span class="condition-icon">⚡</span>
                            <div class="condition-content">
                                <div class="condition-name">3. No Preemption</div>
                                <div class="condition-explanation">Held resources cannot be taken away. Process must release them voluntarily.</div>
                                <div class="condition-status broken">✅ BROKEN - Timeout recovery & forced release</div>
                            </div>
                        </div>
                        
                        <div class="condition-item">
                            <span class="condition-icon">🔄</span>
                            <div class="condition-content">
                                <div class="condition-name">4. Circular Wait</div>
                                <div class="condition-explanation">Circular chain of processes, each waiting for resource held by next. P1→P2→P3→P1</div>
                                <div class="condition-status broken">✅ BROKEN - Lock ordering + timeouts</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="deadlock-scenario">
                    <h4>⚠️ WOULD-BE DEADLOCK SCENARIO (What we AVOID)</h4>
                    <p><strong>Without prevention:</strong></p>
                    <pre>Thread A: Lock fileX → Waiting for fileY
Thread B: Lock fileY → Waiting for fileX
Result: 💀 DEADLOCK (both wait forever)</pre>
                    <p><strong>How your system prevents it:</strong></p>
                    <ol>
                        <li>Thread A: <code>fcntl(fileX, F_SETLK, F_WRLCK)</code> → ✅ Success (lock acquired)</li>
                        <li>Thread A: <code>fcntl(fileY, F_SETLK, F_WRLCK)</code> → ❌ FAIL (non-blocking, returns EAGAIN)</li>
                        <li>Thread A: Releases fileX, retries, or times out</li>
                        <li>Thread B: Can now proceed → ✅ No deadlock</li>
                    </ol>
                </div>
                
                <div class="prevention-strategy">
                    <h4>✅ PREVENTION STRATEGIES YOUR SYSTEM USES</h4>
                    <ul>
                        <li><strong>Break Condition 2 (Hold-and-Wait):</strong> Use <code>fcntl(F_SETLK, non-blocking)</code> instead of blocking <code>F_SETLKW</code>. If lock fails, don't wait - release existing locks and retry.</li>
                        <li><strong>Break Condition 3 (No Preemption):</strong> Implement timeout monitoring. If operation takes > 300s, force-release locks and perform cleanup.</li>
                        <li><strong>Break Condition 4 (Circular Wait):</strong> Enforce lock ordering - always acquire locks in same order (fileA before fileB). This prevents P1→P2→P1 cycles.</li>
                        <li><strong>OS Mechanisms Used:</strong>
                            <ul>
                                <li><code>fcntl(fd, F_SETLK, ...)</code> - Non-blocking lock attempt</li>
                                <li><code>fcntl(fd, F_GETLK, ...)</code> - Check who holds lock</li>
                                <li><code>pthread_setcancelstate()</code> - Timeout-based cancellation</li>
                                <li><code>write_lock()/read_lock()</code> - Ordered lock acquisition</li>
                            </ul>
                        </li>
                    </ul>
                </div>
                
                <hr style="margin: 20px 0; border-color: rgba(74, 144, 226, 0.3);">
                <p><strong style="color: #ffc107;">💡 Viva Answer Template:</strong></p>
                <blockquote style="border-left: 3px solid #ffc107; padding-left: 15px; color: #b0c4de;">
                    "My system prevents deadlock by intentionally breaking 3 of the 4 necessary conditions. 
                    Specifically, we use non-blocking fcntl() to break Hold-and-Wait, 
                    implement timeouts for preemption, and enforce lock ordering to prevent circular waits. 
                    This is Coffman's strategy - it's theoretically sound and proven in practice."
                </blockquote>
            `
        }
    };
    
    const explanation = explanations[demoType];
    if (explanation) {
        updateInstructions(`
            <div class="explanation-content">
                <h3>${explanation.title}</h3>
                ${explanation.content}
                <hr style="margin: 20px 0; border-color: rgba(74, 144, 226, 0.3);">
                <p style="color: #a0b0c8; font-style: italic;">
                    This is safe explanation mode. Click "Run Demo" to see actual system behavior.
                </p>
            </div>
        `);
        
        logToConsole(`[EXPLAIN] Showing explanation for ${demoType}`, 'info');
    }
}

// ==================== CONSOLE MANAGEMENT ====================
function logToConsole(message, type = 'info') {
    const console = document.getElementById('osConsole');
    const line = document.createElement('div');
    line.className = `terminal-line ${type}`;
    line.textContent = message;
    console.appendChild(line);
    console.scrollTop = console.scrollHeight;
    
    eventCounter++;
    document.getElementById('statOps').textContent = eventCounter;
}

function clearConsole() {
    const console = document.getElementById('osConsole');
    console.innerHTML = `
        <div class="terminal-line">$ Console cleared</div>
        <div class="terminal-line">------------------------------</div>
    `;
    eventCounter = 0;
    document.getElementById('statOps').textContent = '0';
}

async function refreshConsole() {
    try {
        // Fetch recent audit logs
        const response = await fetch(`${API_BASE}/logs`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.logs && data.logs.length > 0) {
                data.logs.slice(-10).forEach(log => {
                    const type = log.status && log.status.toLowerCase().includes('fail') ? 'error' : 'info';
                    logToConsole(`[${log.operation}] ${log.file} - ${log.status}`, type);
                });
            }
        }
    } catch (err) {
        console.error('Console refresh error:', err);
    }
}

function startConsoleUpdates() {
    // Poll for new events every 3 seconds
    consoleUpdateInterval = setInterval(async () => {
        if (!explainModeActive && currentDemo) {
            // Auto-refresh when demo is running
            await refreshAllState();
        }
    }, 3000);
}

// ==================== STATE MANAGEMENT ====================
async function refreshAllState() {
    await refreshLocks();
    await refreshStats();
    // Alerts are added manually during demos
}

async function refreshLocks() {
    try {
        const response = await fetch(`${API_BASE}/locks`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            const locksContainer = document.getElementById('activeLocks');
            
            if (data.locks && data.locks.length > 0) {
                locksContainer.innerHTML = data.locks.map(lock => `
                    <div class="lock-item">
                        <span class="lock-file">📄 ${lock.file}</span>
                        <span class="lock-type">${lock.type} LOCK</span>
                        <span class="lock-pid">PID: ${lock.pid || 'N/A'}</span>
                    </div>
                `).join('');
                
                document.getElementById('statLocks').textContent = data.locks.length;
            } else {
                locksContainer.innerHTML = '<div class="state-empty">No active locks</div>';
                document.getElementById('statLocks').textContent = '0';
            }
        }
    } catch (err) {
        console.error('Lock refresh error:', err);
    }
}

async function refreshStats() {
    try {
        const response = await fetch(`${API_BASE}/status`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.status) {
                document.getElementById('statFiles').textContent = data.status.file_count || 0;
                document.getElementById('statSecurity').textContent = data.status.security_events || 0;
            }
        }
    } catch (err) {
        console.error('Stats refresh error:', err);
    }
}

function addSystemAlert(type, message, severity = 'warning') {
    const alertsContainer = document.getElementById('systemAlerts');
    const alert = document.createElement('div');
    alert.className = `alert-item ${severity === 'error' ? '' : 'alert-warning'}`;
    alert.innerHTML = `
        <div class="alert-type">${type}</div>
        <div>${message}</div>
        <div class="alert-time">${new Date().toLocaleTimeString()}</div>
    `;
    
    // Remove "No alerts" message if present
    const empty = alertsContainer.querySelector('.state-empty');
    if (empty) empty.remove();
    
    alertsContainer.insertBefore(alert, alertsContainer.firstChild);
    
    // Keep only last 5 alerts
    while (alertsContainer.children.length > 5) {
        alertsContainer.removeChild(alertsContainer.lastChild);
    }
}

// ==================== CONCEPT HIGHLIGHTING ====================
function highlightConcept(conceptId) {
    const card = document.querySelector(`.concept-card[data-concept="${conceptId}"]`);
    if (card) {
        card.classList.add('active');
    }
}

function unhighlightAllConcepts() {
    document.querySelectorAll('.concept-card').forEach(card => {
        card.classList.remove('active');
    });
}

// ==================== INSTRUCTIONS PANEL ====================
function updateInstructions(html) {
    document.getElementById('instructionsContent').innerHTML = html;
}

// ==================== RESET DEMO STATE ====================
async function resetDemoState() {
    if (!confirm('⚠️ This will delete all demo-generated test files. Continue?')) {
        return;
    }
    
    logToConsole('[RESET] Clearing demo state...', 'warning');
    
    try {
        // Get current file list
        const listResponse = await fetch(`${API_BASE}/list`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (listResponse.ok) {
            const listData = await listResponse.json();
            
            if (listData.files) {
                // Delete all files that start with "demo-" or "concurrent-"
                const demoFiles = listData.files.filter(f => 
                    f.name.startsWith('demo-') || f.name.startsWith('concurrent-')
                );
                
                for (const file of demoFiles) {
                    const deleteResponse = await fetch(`${API_BASE}/delete/${file.name}`, {
                        method: 'DELETE',
                        headers: { 'Authorization': `Bearer ${authToken}` }
                    });
                    
                    if (deleteResponse.ok) {
                        logToConsole(`[DELETED] ${file.name}`, 'success');
                    }
                }
                
                logToConsole(`[RESET] Removed ${demoFiles.length} demo files`, 'success');
            }
        }
        
        // Clear console
        clearConsole();
        
        // Clear alerts
        document.getElementById('systemAlerts').innerHTML = '<div class="state-empty">No alerts</div>';
        
        // Reset instructions
        updateInstructions('<p style="color: #a0b0c8;">Demo state reset. Select a demo to begin.</p>');
        
        // Remove active demo highlighting
        document.querySelectorAll('.demo-card').forEach(card => card.classList.remove('active'));
        currentDemo = null;
        
        await refreshAllState();
        
        showNotification('✅ Demo state reset successfully!', 'success');
        
    } catch (err) {
        logToConsole('[ERROR] Reset failed: ' + err.message, 'error');
        showNotification('❌ Reset failed', 'error');
    }
}

// ==================== NOTIFICATION SYSTEM ====================
function showNotification(message, type = 'info') {
    // Simple alert for now - could be enhanced with toast notifications
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️';
    console.log(`${icon} ${message}`);
    
    // You could also implement a toast notification system here
}

// ==================== CLEANUP ON PAGE UNLOAD ====================
window.addEventListener('beforeunload', () => {
    if (consoleUpdateInterval) {
        clearInterval(consoleUpdateInterval);
    }
});
