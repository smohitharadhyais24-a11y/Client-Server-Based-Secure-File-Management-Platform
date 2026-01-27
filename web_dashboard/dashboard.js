/**
 * OS FILE SERVER DASHBOARD - CLIENT-SIDE LOGIC
 * ==============================================
 * 
 * ARCHITECTURE RULE: This JavaScript NEVER touches the filesystem directly.
 * All operations are HTTP requests → Python API → C Server via TCP
 * 
 * This demonstrates proper separation of concerns in system observability.
 */

const API_BASE = 'http://localhost:5000/api';
let currentFilter = 'all';

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('OS Dashboard initializing...');
    console.log('Architecture: Browser → Python API → C Server');
    
    // Initial data load
    refreshAll();
    
    // Set up auto-refresh (every 2 seconds)
    setInterval(refreshAll, 2000);
});

async function refreshAll() {
    await Promise.all([
        loadStatus(),
        loadFiles(),
        loadLocks(),
        loadLogs(),
        loadSecurity()
    ]);
}

// ============================================================================
// STATUS MONITORING
// ============================================================================

async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        const data = await response.json();
        
        if (data.success) {
            const status = data.status;
            
            // Update server status indicator
            const statusEl = document.getElementById('serverStatus');
            const indicator = statusEl.querySelector('.status-indicator');
            const text = statusEl.querySelector('.status-text');
            
            if (status.c_server_running) {
                indicator.className = 'status-indicator online';
                text.textContent = 'C Server Online';
            } else {
                indicator.className = 'status-indicator offline';
                text.textContent = 'C Server Offline';
            }
            
            // Update stat cards
            document.getElementById('fileCount').textContent = status.file_count;
            document.getElementById('totalSize').textContent = status.total_storage_human;
            document.getElementById('logEntries').textContent = status.audit_log_entries;
            document.getElementById('securityEvents').textContent = status.security_events;
        }
    } catch (error) {
        console.error('Status check failed:', error);
        document.getElementById('serverStatus').querySelector('.status-text').textContent = 'Connection Error';
    }
}

// ============================================================================
// FILE OPERATIONS (Forwarded to C Server)
// ============================================================================

async function uploadFile() {
    const fileInput = document.getElementById('uploadFile');
    if (!fileInput.files.length) {
        showToast('Please select a file', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    showToast(`Uploading ${file.name} to C server...`, 'info');
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`✓ Upload successful! OS operations: ${data.os_operations.join(', ')}`, 'success');
            fileInput.value = '';
            loadFiles();
            loadLogs();
        } else {
            showToast(`✗ Upload failed: ${data.error}`, 'error');
        }
    } catch (error) {
        showToast(`✗ Upload error: ${error.message}`, 'error');
    }
}

async function loadFiles() {
    try {
        const response = await fetch(`${API_BASE}/list`);
        const data = await response.json();
        
        const fileList = document.getElementById('fileList');
        
        if (data.success && data.files.length > 0) {
            fileList.innerHTML = data.files.map(file => `
                <div class="file-item">
                    <div class="file-info">
                        <div class="file-name">📄 ${file.name}</div>
                        <div class="file-size">${file.size_human}</div>
                    </div>
                    <div class="file-actions">
                        <button onclick="downloadFile('${file.name}')" class="btn btn-sm btn-secondary" title="OS: fcntl(F_RDLCK) + read()">
                            ⬇️ Download
                        </button>
                        <button onclick="deleteFile('${file.name}')" class="btn btn-sm btn-danger" title="OS: fcntl(F_WRLCK) + unlink()">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            `).join('');
        } else {
            fileList.innerHTML = '<div class="no-files">No files stored (use Upload to add files via C server)</div>';
        }
    } catch (error) {
        console.error('Load files failed:', error);
    }
}

async function downloadFile(filename) {
    showToast(`Requesting download from C server: ${filename}`, 'info');
    
    try {
        const response = await fetch(`${API_BASE}/download/${filename}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showToast(`✓ Downloaded: ${filename} (via C server read() + fcntl(F_RDLCK))`, 'success');
            loadLogs();
        } else {
            const data = await response.json();
            showToast(`✗ Download failed: ${data.error}`, 'error');
        }
    } catch (error) {
        showToast(`✗ Download error: ${error.message}`, 'error');
    }
}

async function deleteFile(filename) {
    if (!confirm(`Delete ${filename}? This will call C server's unlink() system call.`)) {
        return;
    }
    
    showToast(`Requesting delete from C server: ${filename}`, 'info');
    
    try {
        const response = await fetch(`${API_BASE}/delete/${filename}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`✓ Deleted: ${filename} (C server executed fcntl(F_WRLCK) + unlink())`, 'success');
            loadFiles();
            loadLogs();
        } else {
            showToast(`✗ Delete failed: ${data.error}`, 'error');
        }
    } catch (error) {
        showToast(`✗ Delete error: ${error.message}`, 'error');
    }
}

// ============================================================================
// LOCK VISUALIZATION (OS-Level State)
// ============================================================================

async function loadLocks() {
    try {
        const response = await fetch(`${API_BASE}/locks`);
        const data = await response.json();
        
        const container = document.getElementById('locksContainer');
        const activeLocks = document.getElementById('activeLocks');
        
        if (data.success && data.locks.length > 0) {
            activeLocks.textContent = data.locks.length;
            
            container.innerHTML = data.locks.map(lock => `
                <div class="lock-item">
                    <div class="lock-header">
                        <span class="lock-badge ${lock.type.toLowerCase()}">${lock.type}</span>
                        <span class="lock-file">🔒 ${lock.file}</span>
                    </div>
                    <div class="lock-concept">${lock.os_concept}</div>
                </div>
            `).join('');
        } else {
            activeLocks.textContent = '0';
            container.innerHTML = '<div class="no-locks">✓ No active locks (all files available)</div>';
        }
    } catch (error) {
        console.error('Load locks failed:', error);
    }
}

// ============================================================================
// AUDIT LOG TIMELINE (OS-Level Logging)
// ============================================================================

async function loadLogs() {
    try {
        const response = await fetch(`${API_BASE}/logs`);
        const data = await response.json();
        
        if (data.success) {
            displayLogs(data.logs);
        }
    } catch (error) {
        console.error('Load logs failed:', error);
    }
}

function displayLogs(logs) {
    const timeline = document.getElementById('timeline');
    
    if (!logs || logs.length === 0) {
        timeline.innerHTML = '<div class="no-logs">No audit logs yet</div>';
        return;
    }
    
    // Filter logs
    let filteredLogs = logs;
    if (currentFilter !== 'all') {
        filteredLogs = logs.filter(log => {
            if (currentFilter === 'FAILED') {
                return log.status === 'FAILED';
            }
            return log.operation === currentFilter;
        });
    }
    
    timeline.innerHTML = filteredLogs.reverse().slice(0, 20).map(log => {
        const statusClass = log.status === 'SUCCESS' ? 'success' : 
                           log.status === 'FAILED' ? 'failed' : 'info';
        
        const operationIcon = {
            'UPLOAD': '⬆️',
            'DOWNLOAD': '⬇️',
            'DELETE': '🗑️',
            'LIST': '📋',
            'LOCKS': '🔒',
            'SERVER_START': '🚀'
        }[log.operation] || '📝';
        
        return `
            <div class="timeline-item ${statusClass}">
                <div class="timeline-time">${log.timestamp}</div>
                <div class="timeline-content">
                    <div class="timeline-header">
                        <span class="timeline-operation">${operationIcon} ${log.operation}</span>
                        <span class="timeline-file">${log.file}</span>
                        <span class="timeline-status status-${statusClass}">${log.status}</span>
                    </div>
                    ${log.details ? `<div class="timeline-details">${log.details}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function filterLogs(filter) {
    currentFilter = filter;
    
    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadLogs();
}

// ============================================================================
// SECURITY ALERTS
// ============================================================================

async function loadSecurity() {
    try {
        const response = await fetch(`${API_BASE}/security`);
        const data = await response.json();

        const container = document.getElementById('securityAlerts');

        if (data.success && data.alerts.length > 0) {
            container.innerHTML = data.alerts.reverse().slice(0, 20).map(alert => {
                const severity = classifyAlert(alert.event);
                return `
                    <div class="alert-item ${severity}">
                        <div class="alert-header">
                            <span class="alert-badge ${severity}">${alert.event}</span>
                            <span class="alert-time">${alert.timestamp}</span>
                        </div>
                        <div class="alert-meta">
                            <span>IP: ${alert.ip || 'n/a'}</span>
                            <span>FILE: ${alert.file || 'n/a'}</span>
                        </div>
                        <div class="alert-details">${alert.details || ''}</div>
                    </div>
                `;
            }).join('');
        } else {
            container.innerHTML = '<div class="no-logs">No security alerts yet</div>';
        }
    } catch (error) {
        console.error('Load security failed:', error);
    }
}

function classifyAlert(eventName) {
    if (!eventName) return 'info';
    const upper = eventName.toUpperCase();
    if (upper.includes('INTEGRITY') || upper.includes('BLOCKED')) return 'critical';
    if (upper.includes('AUTH') || upper.includes('ACCESS')) return 'warning';
    return 'info';
}

// ============================================================================
// INTERACTIVE OS COMMANDS (Click status cards to run OS operations)
// ============================================================================

async function runOsCommand(command) {
    const terminal = document.getElementById('osTerminal');
    const content = document.getElementById('terminalContent');
    
    terminal.style.display = 'block';
    content.innerHTML = '<div class="terminal-line command">$ Executing OS command...</div>';
    
    try {
        // Map command to API endpoint
        let endpoint = '';
        let displayCommand = '';
        
        switch(command) {
            case 'list-files':
                endpoint = '/list';
                displayCommand = '$ ls -la storage/';
                break;
            case 'storage-size':
                endpoint = '/status';
                displayCommand = '$ du -sh storage/';
                break;
            case 'show-locks':
                endpoint = '/locks';
                displayCommand = '$ fcntl_locks.sh (check active locks)';
                break;
            case 'show-logs':
                endpoint = '/logs';
                displayCommand = '$ tail -50 logs/audit.log';
                break;
            case 'security-alerts':
                endpoint = '/security';
                displayCommand = '$ grep "AUTH_FAIL\\|BLOCKED" logs/security.log';
                break;
            default:
                return;
        }
        
        // Fetch data from API
        const response = await fetch(`${API_BASE}${endpoint}`);
        const data = await response.json();
        
        // Format output
        let output = `<div class="terminal-line command">${displayCommand}</div>`;
        
        if (command === 'list-files') {
            output += '<div class="terminal-line">OS: readdir() + stat() system calls</div>';
            output += '<div class="terminal-line">-----------</div>';
            if (data.success && data.files.length > 0) {
                data.files.forEach(file => {
                    output += `<div class="terminal-line success">📄 ${file.name} (${file.size_human})</div>`;
                });
            } else {
                output += '<div class="terminal-line">No files stored</div>';
            }
        } 
        else if (command === 'storage-size') {
            output += '<div class="terminal-line">OS: stat() on storage directory</div>';
            output += '<div class="terminal-line">-----------</div>';
            if (data.success) {
                const status = data.status;
                output += `<div class="terminal-line success">Files: ${status.file_count}</div>`;
                output += `<div class="terminal-line success">Total Size: ${status.total_storage_human}</div>`;
            }
        }
        else if (command === 'show-locks') {
            output += '<div class="terminal-line">OS: fcntl() lock inspection</div>';
            output += '<div class="terminal-line">-----------</div>';
            if (data.success && data.locks.length > 0) {
                data.locks.forEach(lock => {
                    const type = lock.lock_type === 'WRITE' ? '🔴 WRLCK' : '🔵 RDLCK';
                    output += `<div class="terminal-line success">${type} on ${lock.file} (PID: ${lock.owner})</div>`;
                });
            } else {
                output += '<div class="terminal-line">No active locks</div>';
            }
        }
        else if (command === 'show-logs') {
            output += '<div class="terminal-line">OS: Thread-safe audit logging (mutex-protected)</div>';
            output += '<div class="terminal-line">-----------</div>';
            if (data.success && data.logs.length > 0) {
                data.logs.slice(-10).forEach(log => {
                    output += `<div class="terminal-line success">[AUDIT] ${log}</div>`;
                });
            } else {
                output += '<div class="terminal-line">No logs yet</div>';
            }
        }
        else if (command === 'security-alerts') {
            output += '<div class="terminal-line">OS: Security monitoring system</div>';
            output += '<div class="terminal-line">-----------</div>';
            if (data.success && data.alerts && data.alerts.length > 0) {
                data.alerts.slice(-10).forEach(alert => {
                    const severity = alert.severity === 'critical' ? '🔴' : '🟡';
                    output += `<div class="terminal-line success">${severity} [${alert.timestamp}] ${alert.type}: ${alert.details}</div>`;
                });
            } else {
                output += '<div class="terminal-line">No security alerts</div>';
            }
        }
        
        content.innerHTML = output;
        
    } catch (error) {
        content.innerHTML = `<div class="terminal-line error">Error: ${error.message}</div>`;
    }
}

function closeOsTerminal() {
    document.getElementById('osTerminal').style.display = 'none';
}

// ============================================================================
// UI UTILITIES
// ============================================================================

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast toast-${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// ============================================================================
// DEBUGGING / CONSOLE INFO
// ============================================================================

console.log(`
╔═══════════════════════════════════════════════════════════════════╗
║  OS FILE SERVER DASHBOARD - SYSTEM OBSERVABILITY LAYER           ║
╠═══════════════════════════════════════════════════════════════════╣
║  Architecture:                                                    ║
║    Browser (This)                                                 ║
║         ↓ HTTP/JSON                                               ║
║    Python API Layer (Flask)                                       ║
║         ↓ TCP Socket IPC                                          ║
║    C File Server (OS Core)                                        ║
║         ↓ System Calls                                            ║
║    Operating System                                               ║
╠═══════════════════════════════════════════════════════════════════╣
║  OS Concepts Visualized:                                          ║
║    • File I/O (open, read, write, close, stat, unlink)           ║
║    • File Locking (fcntl with F_RDLCK, F_WRLCK)                  ║
║    • Deadlock Prevention (bounded transfer)                       ║
║    • Deadlock Avoidance (non-blocking locks)                      ║
║    • Deadlock Recovery (timeout mechanism)                        ║
║    • Multi-threading (pthreads)                                   ║
║    • TCP Socket IPC                                               ║
║    • Thread-safe Audit Logging                                    ║
╠═══════════════════════════════════════════════════════════════════╣
║  NEW FEATURE: Click any System Status card to run OS commands!   ║
║  Shows real file operations, locks, and security alerts          ║
║  Similar to: production system observability (Prometheus/Grafana)║
╚═══════════════════════════════════════════════════════════════════╝
`);
