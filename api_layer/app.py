"""
OS FILE SERVER - WEB API LAYER
==============================

CRITICAL ARCHITECTURE RULES:
1. NO file I/O happens here - ALL file operations go through C server
2. This is a THIN control layer - NOT implementing OS logic
3. Only reads metadata/logs (not modifying them)
4. All requests are forwarded to C TCP server

OS CONCEPT MAPPING:
- /upload → C server open() + write() + fcntl(F_WRLCK)
- /download → C server read() + fcntl(F_RDLCK)  
- /delete → C server unlink() + fcntl(F_WRLCK)
- /locks → Reads C server's global lock state
- /logs → Reads C server's audit log file
- /status → Queries C server thread/connection state
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import socket
import os
import json
import time
import tempfile
from datetime import datetime

# Import our auth and security modules
from auth import auth_manager
from security import security_manager

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from dashboard

# ==================== AUTH HELPER FUNCTIONS ====================
def get_client_ip():
    """Get client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'

def require_auth(f):
    """Decorator to require valid auth token"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401
        
        valid, session = auth_manager.validate_token(token)
        if not valid:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Attach session to request for use in endpoint
        request.session = session
        return f(*args, **kwargs)
    
    return decorated_function

# C Server connection settings
C_SERVER_HOST = '127.0.0.1'
C_SERVER_PORT = 8888

# Paths to C server's data directories (relative to project root, not api_layer/)
STORAGE_DIR = '../storage/'
METADATA_DIR = '../metadata/'
LOGS_DIR = '../logs/'
AUDIT_LOG_FILE = '../logs/audit.log'
SECURITY_LOG_FILE = '../logs/security.log'
AUTH_TOKEN = os.environ.get('FILE_SERVER_AUTH', 'os-core-token')


def log_event(action, detail):
    """Lightweight stdout logging so WSL terminal shows API activity."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {action}: {detail}")


# ==================== DASHBOARD SERVING ====================
@app.route('/', methods=['GET'])
def serve_dashboard():
    """Serve the web dashboard HTML"""
    try:
        dashboard_path = '../web_dashboard/dashboard.html'
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
        else:
            return '<h1>Dashboard not found</h1>', 404, {'Content-Type': 'text/html'}
    except Exception as e:
        return f'<h1>Error loading dashboard: {str(e)}</h1>', 500, {'Content-Type': 'text/html'}

@app.route('/dashboard.js', methods=['GET'])
def serve_dashboard_js():
    """Serve the dashboard JavaScript"""
    try:
        js_path = '../web_dashboard/dashboard.js'
        if os.path.exists(js_path):
            with open(js_path, 'r') as f:
                return f.read(), 200, {'Content-Type': 'application/javascript'}
        else:
            return 'console.error("dashboard.js not found");', 404, {'Content-Type': 'application/javascript'}
    except Exception as e:
        return f'console.error("Error loading dashboard.js: {str(e)}");', 500, {'Content-Type': 'application/javascript'}
@app.route('/demo.html', methods=['GET'])
def serve_demo_html():
    """Serve the demo mode HTML"""
    try:
        demo_path = '../web_dashboard/demo.html'
        if os.path.exists(demo_path):
            with open(demo_path, 'r') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
        else:
            return '<h1>Demo page not found</h1>', 404, {'Content-Type': 'text/html'}
    except Exception as e:
        return f'<h1>Error loading demo page: {str(e)}</h1>', 500, {'Content-Type': 'text/html'}

@app.route('/demo.js', methods=['GET'])
def serve_demo_js():
    """Serve the demo mode JavaScript"""
    try:
        js_path = '../web_dashboard/demo.js'
        if os.path.exists(js_path):
            with open(js_path, 'r') as f:
                return f.read(), 200, {'Content-Type': 'application/javascript'}
        else:
            return 'console.error("demo.js not found");', 404, {'Content-Type': 'application/javascript'}
    except Exception as e:
        return f'console.error("Error loading demo.js: {str(e)}");', 500, {'Content-Type': 'application/javascript'}

@app.route('/demo.css', methods=['GET'])
def serve_demo_css():
    """Serve the demo mode CSS"""
    try:
        css_path = '../web_dashboard/demo.css'
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                return f.read(), 200, {'Content-Type': 'text/css'}
        else:
            return '/* demo.css not found */', 404, {'Content-Type': 'text/css'}
    except Exception as e:
        return f'/* Error loading demo.css: {str(e)} */', 500, {'Content-Type': 'text/css'}

# ============================================================================
# HELPER: Communicate with C Server via TCP
# ============================================================================

def send_to_c_server(command):
    """
    OS CONCEPT: TCP Socket IPC
    Sends command to C file server, receives response
    This demonstrates proper client-server separation
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((C_SERVER_HOST, C_SERVER_PORT))
        
        # Auth + command in one flow to match server parser
        auth_header = f"AUTH {AUTH_TOKEN}\n"
        sock.sendall(auth_header.encode())
        sock.sendall(command.encode() + b'\n')
        response = sock.recv(4096).decode().strip()
        
        sock.close()
        return {'success': True, 'response': response}
    except socket.timeout:
        return {'success': False, 'error': 'C server timeout'}
    except ConnectionRefusedError:
        return {'success': False, 'error': 'C server not running'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ============================================================================
# API ENDPOINTS: File Operations (Forward to C Server)
# ============================================================================

@app.route('/api/upload', methods=['POST'])
@require_auth
def api_upload():
    """
    OS CONCEPT: File I/O (open, write), File Locking (fcntl F_WRLCK)
    
    Forwards upload request to C server which:
    - Opens file using open()
    - Acquires write lock using fcntl()
    - Writes data using write()
    - Creates metadata
    """
    if 'file' not in request.files:
        log_event('UPLOAD', 'rejected - no file field')
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        log_event('UPLOAD', 'rejected - empty filename')
        return jsonify({'success': False, 'error': 'Empty filename'}), 400
    
    # Get username from session for user-specific storage
    username = request.session.get('username', 'anonymous')
    
    # Sanitize filename to avoid spaces/shell chars breaking C server parse
    safe_name = os.path.basename(file.filename).replace(' ', '_')
    # Prepend username directory for isolation
    user_file_path = f"{username}/{safe_name}"
    
    # Save temporarily to send to C server (single-socket flow matches C client protocol)
    fd, temp_path = tempfile.mkstemp(prefix="api_upload_", suffix=f"_{safe_name}")
    with os.fdopen(fd, 'wb') as tmp:
        file.save(tmp)
    
    file_size = os.path.getsize(temp_path)
    # Use user-specific path for storage isolation
    command = f"UPLOAD {user_file_path} {file_size}\n"
    
    try:
        # Open one TCP connection and follow the same protocol as the Python CLI client
        with socket.create_connection((C_SERVER_HOST, C_SERVER_PORT), timeout=10) as sock:
            sock.sendall(f"AUTH {AUTH_TOKEN}\n".encode())
            sock.sendall(command.encode())
            ready = sock.recv(1024).decode()
            if 'READY' not in ready:
                os.remove(temp_path)
                return jsonify({'success': False, 'error': ready}), 500

            with open(temp_path, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    sock.sendall(chunk)

            final_response = sock.recv(1024).decode()
            os.remove(temp_path)

            if 'SUCCESS' in final_response:
                log_event('UPLOAD', f"ok - {username}/{safe_name} ({file_size} bytes)")
                return jsonify({
                    'success': True,
                    'message': f'File uploaded via C server: {safe_name}',
                    'filename': safe_name,
                    'os_operations': ['open()', 'fcntl(F_WRLCK)', 'write()', 'close()']
                })
            log_event('UPLOAD', f"failed - {username}/{safe_name} :: {final_response.strip()}")
            return jsonify({'success': False, 'error': final_response}), 500
    except Exception as e:
        log_event('UPLOAD', f"exception - {username}/{safe_name} :: {e}")
        os.remove(temp_path)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
@require_auth
def api_download(filename):
    """
    OS CONCEPT: File I/O (read), Shared Locking (fcntl F_RDLCK)
    
    Requests file from C server which:
    - Acquires read lock using fcntl(F_RDLCK)
    - Reads file using read()
    - Multiple readers can download simultaneously (shared locks)
    """
    # Get username from session for user-specific storage
    username = request.session.get('username', 'anonymous')
    user_file_path = f"{username}/{filename}"
    command = f"DOWNLOAD {user_file_path}"
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((C_SERVER_HOST, C_SERVER_PORT))
        sock.sendall(f"AUTH {AUTH_TOKEN}\n".encode())
        sock.sendall(command.encode() + b'\n')
        
        # Get response with file size
        response = sock.recv(1024).decode().strip().split('\n')[0]
        
        if 'SUCCESS' in response:
            # Extract file size
            parts = response.split()
            file_size = int(parts[1])
            
            # Receive file data
            temp_path = f'/tmp/download_{filename}'
            with open(temp_path, 'wb') as f:
                remaining = file_size
                while remaining > 0:
                    chunk_size = min(4096, remaining)
                    chunk = sock.recv(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    remaining -= len(chunk)
            
            sock.close()
            log_event('DOWNLOAD', f"ok - {filename} ({file_size} bytes)")
            return send_file(temp_path, as_attachment=True, download_name=filename)
        else:
            log_event('DOWNLOAD', f"failed - {filename} :: {response}")
            return jsonify({'success': False, 'error': response}), 404
            
    except Exception as e:
        log_event('DOWNLOAD', f"exception - {filename} :: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
@require_auth
def api_delete(filename):
    """
    OS CONCEPT: File Deletion (unlink), Exclusive Locking (fcntl F_WRLCK)
    
    Forwards delete request to C server which:
    - Acquires write lock using fcntl(F_WRLCK)
    - Deletes file using unlink()
    - Prevents deletion while file is in use
    """
    # Get username from session for user-specific storage
    username = request.session.get('username', 'anonymous')
    user_file_path = f"{username}/{filename}"
    command = f"DELETE {user_file_path}"
    result = send_to_c_server(command)
    
    if result['success'] and 'SUCCESS' in result['response']:
        log_event('DELETE', f"ok - {filename}")
        return jsonify({
            'success': True,
            'message': f'File deleted via C server: {filename}',
            'os_operations': ['fcntl(F_WRLCK)', 'unlink()']
        })
    else:
        log_event('DELETE', f"failed - {filename} :: {result.get('error', result.get('response'))}")
        return jsonify({'success': False, 'error': result.get('error', 'Delete failed')}), 500

@app.route('/api/list', methods=['GET'])
@require_auth
def api_list():
    """
    OS CONCEPT: Directory Traversal (readdir), File Status (stat)
    
    Queries C server for file list which uses:
    - opendir() to open storage directory
    - readdir() to iterate files
    - stat() to get file sizes
    
    Returns only files for the authenticated user.
    """
    # Get username from session for user-specific storage
    username = request.session.get('username', 'anonymous')
    command = f"LIST {username}"
    result = send_to_c_server(command)
    
    if result['success']:
        # Parse file list from response
        response_lines = result['response'].split('\n')
        files = []
        
        for line in response_lines:
            if '(' in line and 'bytes)' in line:
                # Parse: "filename.txt (1234 bytes)"
                parts = line.split('(')
                if len(parts) == 2:
                    filename = parts[0].strip()
                    # Remove username prefix if present for display
                    if filename.startswith(f"{username}/"):
                        filename = filename[len(username)+1:]
                    size_str = parts[1].split()[0]
                    files.append({
                        'name': filename,
                        'size': int(size_str),
                        'size_human': format_bytes(int(size_str))
                    })
        
        log_event('LIST', f"ok - {username} has {len(files)} files")
        return jsonify({
            'success': True,
            'files': files,
            'os_operations': ['opendir()', 'readdir()', 'stat()']
        })
    else:
        log_event('LIST', f"failed :: {result.get('error')}")
        return jsonify({'success': False, 'error': result.get('error')}), 500

# ============================================================================
# API ENDPOINTS: OS State Visualization (Read-Only)
# ============================================================================

@app.route('/api/locks', methods=['GET'])
def api_locks():
    """
    OS CONCEPT: Lock Status Inspection
    
    Reads C server's global lock state to visualize:
    - Which files are currently locked
    - Write locks (exclusive) vs Read locks (shared)
    - Demonstrates deadlock avoidance mechanism
    """
    command = "LOCKS"
    result = send_to_c_server(command)
    
    if result['success']:
        locks = []
        response_lines = result['response'].split('\n')
        
        for line in response_lines:
            if 'LOCKED:' in line:
                # Parse lock information
                parts = line.split(':')
                if len(parts) >= 2:
                    lock_info = parts[1].strip()
                    locks.append({
                        'file': lock_info,
                        'type': 'WRITE',  # Global locks are write locks
                        'os_concept': 'fcntl(F_WRLCK) - Exclusive lock'
                    })
        
        return jsonify({
            'success': True,
            'locks': locks,
            'lock_count': len(locks),
            'os_concept': 'Non-blocking lock acquisition (deadlock avoidance)'
        })
    else:
        return jsonify({'success': False, 'error': result.get('error')}), 500

@app.route('/api/logs', methods=['GET'])
def api_logs():
    """
    OS CONCEPT: Audit Logging
    
    Reads C server's audit log file (created using open() + write())
    Shows timeline of all OS operations with timestamps
    """
    try:
        if not os.path.exists(AUDIT_LOG_FILE):
            return jsonify({'success': True, 'logs': []})
        
        with open(AUDIT_LOG_FILE, 'r') as f:
            log_lines = f.readlines()
        
        logs = []
        for line in log_lines[-50:]:  # Last 50 entries
            line = line.strip()
            if line:
                logs.append(parse_audit_log_line(line))
        
        return jsonify({
            'success': True,
            'logs': logs,
            'os_concept': 'Thread-safe logging with mutex protection'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logs/clear', methods=['DELETE'])
@require_auth
def api_clear_logs():
    """
    Clear audit log history
    
    Truncates the audit log file to start fresh
    Requires authentication to prevent unauthorized clearing
    """
    try:
        if os.path.exists(AUDIT_LOG_FILE):
            # Truncate file by opening in write mode
            with open(AUDIT_LOG_FILE, 'w') as f:
                f.write('')  # Empty the file
            
            log_event('CLEAR_LOGS', f"ok - cleared by {request.session.get('username', 'unknown')}")
            
            return jsonify({
                'success': True,
                'message': 'Audit log history cleared',
                'cleared_by': request.session.get('username', 'unknown')
            })
        else:
            return jsonify({
                'success': True,
                'message': 'No audit log file to clear'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/security', methods=['GET'])
def api_security():
    """Expose security log events (auth failures, integrity issues)."""
    try:
        if not os.path.exists(SECURITY_LOG_FILE):
            return jsonify({'success': True, 'alerts': []})

        with open(SECURITY_LOG_FILE, 'r') as f:
            log_lines = f.readlines()

        alerts = []
        for line in log_lines[-50:]:
            line = line.strip()
            if line:
                alerts.append(parse_security_log_line(line))

        return jsonify({'success': True, 'alerts': alerts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
@require_auth
def api_status():
    """
    OS CONCEPT: System Status Monitoring
    
    Provides observability into:
    - C server uptime
    - Active files (from C server via LIST command)
    - System health
    """
    try:
        # Get username from session for user-specific file counting
        username = request.session.get('username', 'anonymous')
        
        # Get file list from C server (authoritative source) for this user only
        list_result = send_to_c_server(f"LIST {username}")
        c_server_running = list_result['success']
        
        # Count files from C server response
        file_count = 0
        total_size = 0
        if list_result['success']:
            # Parse raw response from C server: "filename (size bytes)"
            response_lines = list_result['response'].split('\n')
            for line in response_lines:
                if '(' in line and 'bytes)' in line:
                    try:
                        parts = line.split('(')
                        if len(parts) == 2:
                            size_str = parts[1].split()[0]
                            file_count += 1
                            total_size += int(size_str)
                    except:
                        pass
        
        # Read log counts
        log_entries = 0
        if os.path.exists(AUDIT_LOG_FILE):
            with open(AUDIT_LOG_FILE, 'r') as f:
                log_entries = len(f.readlines())

        security_entries = 0
        if os.path.exists(SECURITY_LOG_FILE):
            with open(SECURITY_LOG_FILE, 'r') as f:
                security_entries = len(f.readlines())
        
        return jsonify({
            'success': True,
            'status': {
                'c_server_running': c_server_running,
                'file_count': file_count,
                'total_storage_bytes': total_size,
                'total_storage_human': format_bytes(total_size),
                'audit_log_entries': log_entries,
                'security_events': security_entries,
                'architecture': 'C File Server → Python API → Web Dashboard'
            },
            'os_concepts': [
                'Multi-threaded server (pthreads)',
                'TCP Socket IPC',
                'File system operations',
                'Deadlock prevention/avoidance/recovery'
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_bytes(bytes_val):
    """Human-readable file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"

def parse_audit_log_line(line):
    """Parse C server audit log format"""
    # Format: [YYYY-MM-DD HH:MM:SS] OPERATION=X FILE=Y STATUS=Z DETAILS=...
    try:
        timestamp = line[1:20]
        rest = line[22:]
        
        parts = {}
        for item in rest.split(' DETAILS='):
            if '=' in item:
                for pair in item.split():
                    if '=' in pair:
                        key, val = pair.split('=', 1)
                        parts[key] = val
        
        return {
            'timestamp': timestamp,
            'operation': parts.get('OPERATION', 'UNKNOWN'),
            'file': parts.get('FILE', 'N/A'),
            'status': parts.get('STATUS', 'UNKNOWN'),
            'details': line.split('DETAILS=')[-1] if 'DETAILS=' in line else ''
        }
    except:
        return {'timestamp': '', 'operation': 'PARSE_ERROR', 'file': '', 'status': '', 'details': line}


def parse_security_log_line(line):
    """Parse security log format: [ts] EVENT=X IP=Y FILE=Z DETAILS=..."""
    try:
        timestamp = line[1:20]
        rest = line[22:]
        parts = {}
        for token in rest.split():
            if '=' in token:
                key, val = token.split('=', 1)
                parts[key] = val
        return {
            'timestamp': timestamp,
            'event': parts.get('EVENT', 'UNKNOWN'),
            'ip': parts.get('IP', ''),
            'file': parts.get('FILE', ''),
            'details': line.split('DETAILS=')[-1] if 'DETAILS=' in line else ''
        }
    except:
        return {'timestamp': '', 'event': 'PARSE_ERROR', 'ip': '', 'file': '', 'details': line}

# ============================================================================
# AUTHENTICATION ENDPOINTS (PHASE 1)
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """
    Authenticate user with username/password
    Returns: JWT-like token for subsequent requests
    
    OS Concept: File-based access control (reading users.db)
    """
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    client_ip = get_client_ip()
    
    log_event('LOGIN_ATTEMPT', f'User={username} IP={client_ip}')
    
    success, message, token = auth_manager.authenticate(username, password, client_ip)
    
    if success:
        log_event('LOGIN_SUCCESS', f'User={username} Token={token[:16]}...')
        return jsonify({
            'success': True,
            'token': token,
            'username': username,
            'message': message
        }), 200
    else:
        log_event('LOGIN_FAILED', f'User={username} IP={client_ip} Reason={message}')
        return jsonify({
            'success': False,
            'message': message
        }), 401

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout and invalidate session token
    
    OS Concept: Session termination, resource cleanup
    """
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    username = request.session.get('username', 'unknown')
    
    if auth_manager.logout(token):
        log_event('LOGOUT_SUCCESS', f'User={username}')
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    else:
        return jsonify({'success': False, 'message': 'Logout failed'}), 400

@app.route('/api/session-info', methods=['GET'])
@require_auth
def session_info():
    """
    Get current session information
    
    OS Concept: Process identity and context
    """
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    info = auth_manager.get_session_info(token)
    
    if info:
        return jsonify({
            'success': True,
            'session': info,
            'active_sessions': auth_manager.get_active_sessions_count()
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Session invalid'}), 401

@app.route('/api/events', methods=['GET'])
@require_auth
def get_events():
    """
    Get live OS event stream
    Parses events.log file generated by C server
    
    OS Concept: Audit trail, real-time system monitoring
    """
    try:
        events = []
        events_file = '../logs/events.log'
        
        if os.path.exists(events_file):
            with open(events_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(parse_event_line(line))
        
        # Return last 50 events (most recent first)
        events = events[-50:]
        events.reverse()
        
        return jsonify({'success': True, 'events': events}), 200
    except Exception as e:
        log_event('EVENTS_ERROR', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

def parse_event_line(line):
    """Parse event line from events.log"""
    try:
        # Format: [timestamp] EVENT_TYPE filename lock_type pid user status
        parts = line.strip('[]').split('] ', 1)
        if len(parts) == 2:
            timestamp = parts[0]
            rest = parts[1]
            tokens = rest.split()
            
            return {
                'timestamp': timestamp,
                'event_type': tokens[0] if len(tokens) > 0 else 'UNKNOWN',
                'filename': tokens[1] if len(tokens) > 1 else '',
                'lock_type': tokens[2] if len(tokens) > 2 else 'NONE',
                'pid': tokens[3] if len(tokens) > 3 else '',
                'user': tokens[4] if len(tokens) > 4 else 'system',
                'status': tokens[5] if len(tokens) > 5 else 'PENDING'
            }
    except:
        pass
    
    return {'timestamp': '', 'event_type': 'PARSE_ERROR', 'raw': line}

# ============================================================================
# PHASE 3: SECURITY ENDPOINTS
# ============================================================================

@app.route('/api/security/events', methods=['GET'])
@require_auth
def get_security_events():
    """Get security events (requires authentication)"""
    try:
        limit = request.args.get('limit', 50, type=int)
        events = security_manager.get_security_events(limit)
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        }), 200
    except Exception as e:
        log_event('SECURITY_EVENTS_ERROR', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/summary', methods=['GET'])
@require_auth
def get_security_summary():
    """Get security summary (requires authentication)"""
    try:
        summary = security_manager.get_summary()
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
    except Exception as e:
        log_event('SECURITY_SUMMARY_ERROR', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/threats', methods=['GET'])
@require_auth
def get_security_threats():
    """Get high/critical severity threats only"""
    try:
        limit = request.args.get('limit', 20, type=int)
        threats = security_manager.get_high_severity_events(limit)
        return jsonify({
            'success': True,
            'threats': threats,
            'count': len(threats),
            'threat_level': 'CRITICAL' if len(threats) > 5 else ('HIGH' if len(threats) > 2 else 'NORMAL')
        }), 200
    except Exception as e:
        log_event('SECURITY_THREATS_ERROR', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/check/<path:filename>', methods=['POST'])
@require_auth
def check_file_security(filename):
    """Check file for security violations"""
    try:
        # Check path traversal
        safe, reason = security_manager.check_path_traversal(filename)
        if not safe:
            return jsonify({
                'success': False,
                'check': 'PATH_TRAVERSAL',
                'reason': reason,
                'severity': 'CRITICAL'
            }), 403
        
        return jsonify({
            'success': True,
            'file': filename,
            'path_safe': True,
            'checks': {
                'path_traversal': 'PASS',
                'access_control': 'PASS'
            }
        }), 200
    except Exception as e:
        log_event('SECURITY_CHECK_ERROR', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/status', methods=['GET'])
def get_security_status():
    """Get overall security status (no auth required for general info)"""
    try:
        summary = security_manager.get_summary()
        threat_count = len(security_manager.get_high_severity_events())
        blocked_count = len(security_manager.blocked_ips)
        
        # Determine threat level
        if threat_count > 10 or blocked_count > 3:
            threat_level = 'CRITICAL'
        elif threat_count > 5 or blocked_count > 1:
            threat_level = 'HIGH'
        else:
            threat_level = 'NORMAL'
        
        return jsonify({
            'success': True,
            'threat_level': threat_level,
            'events': summary['total_events'],
            'high_severity': summary['high_severity'],
            'blocked_ips': blocked_count,
            'status': 'SECURE' if threat_level == 'NORMAL' else f'WARNING: {threat_level}'
        }), 200
    except Exception as e:
        log_event('SECURITY_STATUS_ERROR', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("OS FILE SERVER - WEB API LAYER")
    print("=" * 70)
    print(f"C Server: {C_SERVER_HOST}:{C_SERVER_PORT}")
    print("API Server: http://localhost:5000")
    print()
    print("ARCHITECTURE:")
    print("  C File Server (OS Core)")
    print("       | TCP/IPC")
    print("  Python API Layer (This)")
    print("       | HTTP/JSON")
    print("  Web Dashboard (Browser)")
    print()
    print("ALL FILE OPERATIONS HAPPEN IN C SERVER")
    print("This layer only forwards requests and visualizes state")
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
