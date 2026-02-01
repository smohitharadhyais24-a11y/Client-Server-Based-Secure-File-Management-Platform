/**
 * PHASE 4b-4c: Dashboard Logic & Interactivity
 * =============================================
 * Real-time polling, live visualization, and user interactions
 * 
 * ARCHITECTURE RULE: This JavaScript NEVER touches the filesystem directly.
 * All operations are HTTP requests → Python API → C Server via TCP
 */

// ==================== GLOBAL STATE ====================
const API_BASE = 'http://localhost:5000/api';
let authToken = null;
let currentUser = null;
let autoPollEnabled = true;
let pollInterval = null;
let eventPollInterval = null;

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Dashboard] Initializing...');
    
    // Check if already logged in (from session storage)
    const savedToken = sessionStorage.getItem('authToken');
    if (savedToken) {
        authToken = savedToken;
        currentUser = sessionStorage.getItem('username');
        loginSuccess();
    }
    
    // Setup polling checkbox
    const autoPollCheckbox = document.getElementById('autoPoll');
    if (autoPollCheckbox) {
        autoPollCheckbox.addEventListener('change', function() {
            autoPollEnabled = this.checked;
            if (autoPollEnabled) {
                startAutoPolling();
                console.log('[Dashboard] Auto-polling enabled');
            } else {
                stopAutoPolling();
                console.log('[Dashboard] Auto-polling disabled');
            }
        });
    }
    
    console.log('[Dashboard] Initialized');
});

// ==================== AUTHENTICATION ====================
function showLoginModal() {
    console.log('[Auth] Showing login modal');
    const modal = document.getElementById('loginModal');
    if (modal) modal.style.display = 'flex';
}

function hideLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) modal.style.display = 'none';
}

async function login() {
    const username = document.getElementById('loginUsername')?.value || '';
    const password = document.getElementById('loginPassword')?.value || '';
    
    if (!username || !password) {
        alert('Please enter username and password');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: username, password: password})
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.token;
            currentUser = username;
            sessionStorage.setItem('authToken', authToken);
            sessionStorage.setItem('username', currentUser);
            loginSuccess();
        } else {
            alert('Login failed: ' + (await response.text()));
        }
    } catch (err) {
        console.error('[Auth] Login error:', err);
        alert('Connection error: ' + err.message);
    }
}

function logout() {
    console.log('[Auth] Logging out');
    authToken = null;
    currentUser = null;
    sessionStorage.removeItem('authToken');
    sessionStorage.removeItem('username');
    stopAutoPolling();
    showLoginModal();
}

function loginSuccess() {
    console.log(`[Auth] Login successful for ${currentUser}`);
    hideLoginModal();
    const userDisplay = document.getElementById('username');
    if (userDisplay) userDisplay.textContent = currentUser || 'User';
    startAutoPolling();
    refreshAll();
}

// ==================== API WRAPPER ====================
async function apiCall(endpoint, method = 'GET', body = null) {
    if (!authToken) {
        console.error('[API] No auth token');
        showStatus('Not authenticated', 'error');
        return null;
    }
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();
        
        if (response.status === 401) {
            logout();
            return null;
        }
        
        return data;
    } catch (err) {
        console.error('[API] Error:', err);
        return null;
    }
}

// ==================== FILE OPERATIONS ====================
async function uploadFile() {
    const filename = document.getElementById('uploadName')?.value || 'file.txt';
    const content = document.getElementById('uploadContent')?.value || '';
    
    if (!content) {
        showStatus('Please enter file content', 'error');
        return;
    }
    
    showStatus(`Uploading ${filename}...`, 'info');
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({filename: filename, content: content})
        });
        
        const data = await response.json();
        if (data.success || response.ok) {
            showStatus(`✓ Uploaded: ${filename}`, 'success');
            document.getElementById('uploadContent').value = '';
            document.getElementById('uploadName').value = '';
            refreshFileList();
            refreshAuditLog();
        } else {
            showStatus(`✗ Upload failed: ${data.error || 'Unknown error'}`, 'error');
        }
    } catch (err) {
        console.error('[Upload] Error:', err);
        showStatus('Upload error: ' + err.message, 'error');
    }
}

async function downloadFile() {
    const filename = document.getElementById('downloadName')?.value || '';
    
    if (!filename) {
        showStatus('Enter filename to download', 'error');
        return;
    }
    
    showStatus(`Downloading ${filename}...`, 'info');
    
    try {
        const response = await fetch(`${API_BASE}/download/${filename}`, {
            headers: {'Authorization': `Bearer ${authToken}`}
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            showStatus(`✓ Downloaded: ${filename}`, 'success');
            refreshAuditLog();
        } else {
            showStatus('Download failed', 'error');
        }
    } catch (err) {
        showStatus('Download error: ' + err.message, 'error');
    }
}

async function deleteFile() {
    const filename = document.getElementById('deleteName')?.value || '';
    
    if (!filename) {
        showStatus('Enter filename to delete', 'error');
        return;
    }
    
    if (!confirm(`Delete ${filename}?`)) return;
    
    showStatus(`Deleting ${filename}...`, 'info');
    
    try {
        const response = await fetch(`${API_BASE}/delete/${filename}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${authToken}`}
        });
        
        const data = await response.json();
        if (data.success || response.ok) {
            showStatus(`✓ Deleted: ${filename}`, 'success');
            document.getElementById('deleteName').value = '';
            refreshFileList();
            refreshAuditLog();
        } else {
            showStatus('Delete failed', 'error');
        }
    } catch (err) {
        showStatus('Delete error: ' + err.message, 'error');
    }
}

// ==================== REFRESH FUNCTIONS ====================
async function refreshStatus() {
    const data = await apiCall('/status');
    if (!data || !data.status) return;
    
    const status = data.status;
    document.getElementById('fileCount').textContent = status.file_count || 0;
    document.getElementById('threatCount').textContent = status.security_events || 0;
    
    // Get lock count from separate endpoint
    const locksData = await apiCall('/locks');
    if (locksData && locksData.locks) {
        document.getElementById('lockCount').textContent = locksData.locks.length || 0;
    }
    
    // Calculate storage usage from file list
    const fileData = await apiCall('/list');
    if (fileData && fileData.files) {
        const totalBytes = fileData.files.reduce((sum, file) => sum + (file.size || 0), 0);
        const totalMB = (totalBytes / (1024 * 1024)).toFixed(2);
        document.getElementById('storageUsed').textContent = totalMB + ' MB';
    }
    
    // Update file list
    refreshFileList();
}

async function clearAuditLog() {
    if (!confirm('⚠️ Are you sure you want to clear all audit history? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/logs/clear`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success || response.ok) {
            showStatus('✓ Audit history cleared', 'success');
            refreshAuditLog();
        } else {
            showStatus(`✗ Failed to clear history: ${result.error || 'Unknown error'}`, 'error');
        }
    } catch (err) {
        console.error('Clear audit log error:', err);
        showStatus('✗ Error clearing audit history', 'error');
    }
}

async function refreshAuditLog() {
    const data = await apiCall('/logs');
    if (!data || !data.logs) return;
    
    const auditTable = document.getElementById('auditTable');
    if (!auditTable) return;
    
    if (data.logs.length === 0) {
        auditTable.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #00aa00;">No audit logs yet</td></tr>';
        return;
    }
    
    auditTable.innerHTML = data.logs.slice(-50).reverse().map(log => {
        const operation = (log.operation || log.op || '').toLowerCase();
        const status = (log.status || 'SUCCESS').toUpperCase();
        
        // Determine row class for color coding
        let rowClass = '';
        if (status.includes('FAIL') || status.includes('ERROR') || status.includes('DENIED')) {
            rowClass = 'audit-failed';
        } else if (operation.includes('lock') || operation.includes('lck')) {
            rowClass = 'audit-lock';
        } else if (status.includes('SUCCESS') || status.includes('OK')) {
            rowClass = 'audit-success';
        }
        
        return `
            <tr class="${rowClass}" data-operation="${operation}" data-status="${status}">
                <td>${log.timestamp || log.time || ''}</td>
                <td>${log.operation || log.op || ''}</td>
                <td>${log.file || ''}</td>
                <td><span class="${log.status?.toLowerCase() || 'success'}">${log.status || 'SUCCESS'}</span></td>
                <td>${log.details || ''}</td>
            </tr>
        `;
    }).join('');
}

// Global filter state
let currentAuditFilter = 'all';

function filterAudit(filterType) {
    currentAuditFilter = filterType;
    
    // Update active button
    document.querySelectorAll('.audit-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Get all rows
    const rows = document.querySelectorAll('#auditTable tr[data-operation]');
    
    rows.forEach(row => {
        const operation = row.getAttribute('data-operation');
        const status = row.getAttribute('data-status');
        let show = false;
        
        switch(filterType) {
            case 'all':
                show = true;
                break;
            case 'upload':
                show = operation.includes('upload') || operation.includes('write');
                break;
            case 'download':
                show = operation.includes('download') || operation.includes('read');
                break;
            case 'delete':
                show = operation.includes('delete') || operation.includes('remove');
                break;
            case 'lock':
                show = operation.includes('lock') || operation.includes('lck');
                break;
            case 'failed':
                show = status.includes('FAIL') || status.includes('ERROR') || status.includes('DENIED');
                break;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

async function clearAuditLog() {
    if (!confirm('Clear all audit logs?')) return;
    // This would need a new endpoint in Flask to clear logs
    showStatus('Audit log clear not yet implemented', 'info');
}

// ==================== FILE LIST REFRESH ====================
async function refreshFileList() {
    console.log('[FileList] Refreshing file list...');
    try {
        const filesData = await apiCall('/list');
        console.log('[FileList] Received data:', filesData);
        
        if (filesData && filesData.files && Array.isArray(filesData.files)) {
            console.log('[FileList] Files count:', filesData.files.length);
            
            if (filesData.files.length === 0) {
                document.getElementById('fileListContainer').innerHTML = '<div style="color: #a0b0c8; text-align: center; padding: 10px;">[No files yet - Upload files to see them listed here]</div>';
                return;
            }
            
            const fileListHTML = filesData.files.map(file => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(74, 144, 226, 0.1);">
                    <div style="flex: 1;">
                        <strong style="color: #fff;">${file.name || file}</strong>
                        ${file.size ? `<span style="color: #6c7a89; font-size: 0.85em; margin-left: 8px;">${formatFileSize(file.size)}</span>` : ''}
                    </div>
                    <div style="display: flex; gap: 5px;">
                        <button onclick="downloadFileByName('${file.name || file}')" style="padding: 4px 8px; font-size: 0.75em; background: rgba(74, 144, 226, 0.3);">📥</button>
                        <button onclick="deleteFileByName('${file.name || file}')" class="danger" style="padding: 4px 8px; font-size: 0.75em;">🗑️</button>
                    </div>
                </div>
            `).join('');
            document.getElementById('fileListContainer').innerHTML = fileListHTML;
            console.log('[FileList] Updated file list display');
        } else {
            console.log('[FileList] No valid files data received');
            document.getElementById('fileListContainer').innerHTML = '<div style="color: #a0b0c8; text-align: center; padding: 10px;">[No files yet]</div>';
        }
    } catch (err) {
        console.error('[FileList] Error:', err);
        document.getElementById('fileListContainer').innerHTML = '<div style="color: #e57373; text-align: center; padding: 10px;">[Unable to fetch file list]</div>';
    }
}

// Helper functions for inline file actions
function downloadFileByName(filename) {
    document.getElementById('downloadName').value = filename;
    downloadFile();
}

function deleteFileByName(filename) {
    document.getElementById('deleteName').value = filename;
    deleteFile();
}

async function refreshSecurityEvents() {
    const data = await apiCall('/security/threats');
    if (!data) return;
    
    const threatTable = document.getElementById('threatTable');
    if (!threatTable) return;
    
    if (!data.threats || data.threats.length === 0) {
        threatTable.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #00aa00;">[No threats - Secure]</td></tr>';
        return;
    }
    
    threatTable.innerHTML = data.threats.slice(-10).reverse().map(threat => `
        <tr>
            <td>${threat.timestamp}</td>
            <td>${threat.event_type || threat.type || 'UNKNOWN'}</td>
            <td><span class="severity-${(threat.severity || 'info').toLowerCase()}">${threat.severity || 'INFO'}</span></td>
            <td>${threat.details || ''}</td>
        </tr>
    `).join('');
}

async function refreshEventFeed() {
    const data = await apiCall('/security/events');
    if (!data) return;
    
    const feed = document.getElementById('eventFeed');
    if (!feed) return;
    
    if (!data.events || data.events.length === 0) {
        feed.innerHTML = '<div class="event-line" style="color: #00aa00;">[Waiting for events...]</div>';
        return;
    }
    
    feed.innerHTML = data.events.slice(-30).reverse().map(event => `
        <div class="event-line">
            <span class="event-time">[${event.timestamp}]</span>
            <span class="event-type">${event.event_type || event.type || 'EVENT'}</span>
            ${event.filename ? event.filename : ''}
        </div>
    `).join('');
}

async function refreshAll() {
    await Promise.all([
        refreshStatus(),
        refreshAuditLog(),
        refreshSecurityEvents(),
        refreshEventFeed()
    ]);
}

// ==================== AUTO POLLING ====================
function startAutoPolling() {
    console.log('[Polling] Starting auto-poll');
    
    // Poll status every 3 seconds
    pollInterval = setInterval(refreshStatus, 3000);
    
    // Poll events every 2 seconds
    eventPollInterval = setInterval(async () => {
        await Promise.all([
            refreshAuditLog(),
            refreshSecurityEvents(),
            refreshEventFeed()
        ]);
    }, 2000);
    
    refreshAll();
}

function stopAutoPolling() {
    console.log('[Polling] Stopping auto-poll');
    if (pollInterval) clearInterval(pollInterval);
    if (eventPollInterval) clearInterval(eventPollInterval);
}

// ==================== UI HELPERS ====================
function showStatus(message, type = 'info') {
    console.log(`[UI] ${type.toUpperCase()}: ${message}`);
    
    // Try to use operationStatus div first
    const statusDiv = document.getElementById('operationStatus');
    const msgSpan = document.getElementById('operationMessage');
    
    if (statusDiv && msgSpan) {
        msgSpan.textContent = message;
        msgSpan.style.color = type === 'success' ? '#00ff00' : (type === 'error' ? '#ff6666' : '#00aa00');
        statusDiv.style.display = 'block';
        
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

// ==================== FILE UPLOAD FROM DEVICE ====================
let selectedFile = null;

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        console.log(`[FileUpload] Selected: ${file.name} (${file.size} bytes)`);
        
        // Show file info
        document.getElementById('selectedFileName').textContent = file.name;
        document.getElementById('selectedFileSize').textContent = formatFileSize(file.size);
        document.getElementById('selectedFileInfo').style.display = 'block';
        document.getElementById('uploadBtn').disabled = false;
        
        showStatus(`Selected: ${file.name} (${formatFileSize(file.size)})`, 'success');
    }
}

async function uploadSelectedFile() {
    if (!selectedFile) {
        showStatus('No file selected', 'error');
        return;
    }
    
    console.log(`[FileUpload] Uploading ${selectedFile.name}...`);
    showStatus(`Uploading ${selectedFile.name}...`, 'info');
    
    try {
        // Create FormData and append the actual file object
        const formData = new FormData();
        formData.append('file', selectedFile);  // Changed: send file object directly
        formData.append('filename', selectedFile.name);
        
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
                // DON'T set Content-Type - browser will set it with boundary for FormData
            },
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`[FileUpload] Success: ${selectedFile.name}`);
            showStatus(`✓ Uploaded ${selectedFile.name} successfully!`, 'success');
                
            // Reset file input
            document.getElementById('fileInput').value = '';
            document.getElementById('selectedFileInfo').style.display = 'none';
            document.getElementById('uploadBtn').disabled = true;
            selectedFile = null;
            
            // Refresh status and logs
            console.log('[FileUpload] About to refresh file list...');
            refreshFileList();
            refreshStatus();
            refreshAuditLog();
        } else {
            showStatus(`Upload failed: ${result.error || 'Unknown error'}`, 'error');
        }
    } catch (err) {
        console.error('[FileUpload] Error:', err);
        showStatus('Upload failed: Network error', 'error');
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// ==================== OS COMMAND EXECUTION ====================
async function runOSCommand(commandType) {
    console.log(`[OSCommand] Executing: ${commandType}`);
    
    const commandDiv = document.getElementById('commandOutput');
    const commandText = document.getElementById('commandText');
    
    // Show terminal
    commandDiv.style.display = 'block';
    commandText.textContent = 'Executing command...';
    
    // Command mappings
    const commands = {
        'files': {
            cmd: 'ls -lah storage/',
            desc: 'List files in storage with details'
        },
        'storage': {
            cmd: 'du -sh storage/',
            desc: 'Calculate total storage usage'
        },
        'locks': {
            cmd: 'fcntl(F_GETLK) system call',
            desc: 'Query active file locks'
        },
        'clients': {
            cmd: 'who | wc -l',
            desc: 'Count active client sessions'
        },
        'audit': {
            cmd: 'wc -l logs/audit.log',
            desc: 'Count total audit log entries'
        },
        'security': {
            cmd: 'grep -c "FAIL" logs/audit.log',
            desc: 'Count failed authentication attempts'
        },
        'threads': {
            cmd: 'ps -o nlwp <pid>',
            desc: 'Show active server threads'
        },
        'uptime': {
            cmd: 'ps -p <pid> -o etime',
            desc: 'Show server uptime'
        },
        'blocked': {
            cmd: 'Deadlock avoidance metrics',
            desc: 'Show blocked operations count'
        },
        'recovered': {
            cmd: 'Timeout recovery metrics',
            desc: 'Show recovered operations count'
        }
    };
    
    const command = commands[commandType];
    
    if (!command) {
        commandText.textContent = 'Unknown command type';
        return;
    }
    
    // Simulate command execution with actual data
    try {
        let output = '';
        
        if (commandType === 'files') {
            const data = await apiCall('/list');
            if (data && data.files) {
                output += `$ ${command.cmd}\n`;
                output += `total ${data.files.length}\n`;
                data.files.forEach(file => {
                    output += `-rw-r--r-- 1 user user ${file.size.toString().padStart(8)} ${file.modified || 'Jan 28'} ${file.name}\n`;
                });
                output += `\nTotal files: ${data.files.length}`;
            }
        } else if (commandType === 'storage') {
            const data = await apiCall('/list');
            if (data && data.files) {
                const totalBytes = data.files.reduce((sum, file) => sum + (file.size || 0), 0);
                const totalMB = (totalBytes / (1024 * 1024)).toFixed(2);
                output += `$ ${command.cmd}\n`;
                output += `${totalMB}M\tstorage/\n`;
                output += `\nTotal storage used: ${totalMB} MB (${totalBytes} bytes)`;
            }
        } else if (commandType === 'locks') {
            const data = await apiCall('/locks');
            if (data && data.locks) {
                output += `$ Checking active locks via fcntl()...\n`;
                if (data.locks.length === 0) {
                    output += 'No active locks\n';
                } else {
                    data.locks.forEach(lock => {
                        output += `File: ${lock.file}, Type: ${lock.type}, Owner: ${lock.owner}, PID: ${lock.pid}\n`;
                    });
                }
                output += `\nActive locks: ${data.locks.length}`;
            }
        } else if (commandType === 'clients') {
            const data = await apiCall('/session-info');
            if (data) {
                output += `$ ${command.cmd}\n`;
                output += `${data.active_sessions || 1}\n`;
                output += `\nActive sessions: ${data.active_sessions || 1}`;
            }
        } else if (commandType === 'audit') {
            const data = await apiCall('/audit');
            if (data && data.logs) {
                output += `$ ${command.cmd}\n`;
                output += `${data.logs.length} logs/audit.log\n`;
                output += `\nTotal audit entries: ${data.logs.length}`;
            } else {
                output += `$ ${command.cmd}\n`;
                output += `0 logs/audit.log\n`;
                output += `\nTotal audit entries: 0`;
            }
        } else if (commandType === 'security') {
            const data = await apiCall('/security/events');
            if (data && data.events) {
                output += `$ ${command.cmd}\n`;
                const failCount = data.events.filter(e => e.severity === 'high' || e.severity === 'critical').length;
                output += `${failCount}\n`;
                output += `\nSecurity alerts: ${failCount}`;
            }
        } else if (commandType === 'threads') {
            const data = await apiCall('/status');
            if (data) {
                const threads = data.threads || '-';
                output += `$ ${command.cmd}\n`;
                output += `Active threads: ${threads}\n`;
                output += `\nServer is running with ${threads} active threads`;
            }
        } else if (commandType === 'uptime') {
            const data = await apiCall('/status');
            if (data) {
                const uptime = data.uptime || '0s';
                output += `$ ${command.cmd}\n`;
                output += `Elapsed: ${uptime}\n`;
                output += `\nServer has been running for ${uptime}`;
            }
        } else if (commandType === 'blocked') {
            const data = await apiCall('/status');
            if (data) {
                const blocked = data.blocked_ops || 0;
                output += `$ Checking deadlock avoidance system...\n`;
                output += `Blocked operations: ${blocked}\n`;
                output += `\nTotal blocked operations (deadlock prevention): ${blocked}`;
            }
        } else if (commandType === 'recovered') {
            const data = await apiCall('/status');
            if (data) {
                const recovered = data.recovered_ops || 0;
                output += `$ Checking timeout recovery metrics...\n`;
                output += `Recovered operations: ${recovered}\n`;
                output += `\nTotal recovered operations (timeout handling): ${recovered}`;
            }
        }
        
        commandText.textContent = output || 'No output';
        
        // Auto-hide after 20 seconds
        setTimeout(() => {
            commandDiv.style.display = 'none';
        }, 20000);
        
    } catch (err) {
        console.error('[OSCommand] Error:', err);
        commandText.textContent = `Error: ${err.message}`;
    }
}

// ==================== MAIN ENTRY POINT ====================
console.log(`
╔════════════════════════════════════════════════════╗
║          PHASE 4b-4c DASHBOARD ACTIVE              ║
║     Real-time Polling & Interactivity Enabled     ║
╠════════════════════════════════════════════════════╣
║ Auto-polling Intervals:                            ║
║   • Status: Every 3 seconds                        ║
║   • Events: Every 2 seconds                        ║
║   • Security: Every 2 seconds                      ║
╠════════════════════════════════════════════════════╣
║ Features:                                          ║
║   ✓ Login/Logout with session persistence         ║
║   ✓ Real-time audit log refresh                   ║
║   ✓ Live security threat detection                ║
║   ✓ Interactive file operations                   ║
║   ✓ Auto-polling toggle checkbox                  ║
║   ✓ Device file upload support                    ║
║   ✓ OS command execution with output              ║
╚════════════════════════════════════════════════════╝
`);
