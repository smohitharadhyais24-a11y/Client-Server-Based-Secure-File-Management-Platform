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

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from dashboard

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
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] [API] {action} :: {detail}")

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
    # Sanitize filename to avoid spaces/shell chars breaking C server parse
    safe_name = os.path.basename(file.filename).replace(' ', '_')
    
    # Save temporarily to send to C server (single-socket flow matches C client protocol)
    fd, temp_path = tempfile.mkstemp(prefix="api_upload_", suffix=f"_{safe_name}")
    with os.fdopen(fd, 'wb') as tmp:
        file.save(tmp)
    
    file_size = os.path.getsize(temp_path)
    command = f"UPLOAD {safe_name} {file_size}\n"
    
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
                log_event('UPLOAD', f"ok - {safe_name} ({file_size} bytes)")
                return jsonify({
                    'success': True,
                    'message': f'File uploaded via C server: {safe_name}',
                    'os_operations': ['open()', 'fcntl(F_WRLCK)', 'write()', 'close()']
                })
            log_event('UPLOAD', f"failed - {safe_name} :: {final_response.strip()}")
            return jsonify({'success': False, 'error': final_response}), 500
    except Exception as e:
        log_event('UPLOAD', f"exception - {safe_name} :: {e}")
        os.remove(temp_path)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def api_download(filename):
    """
    OS CONCEPT: File I/O (read), Shared Locking (fcntl F_RDLCK)
    
    Requests file from C server which:
    - Acquires read lock using fcntl(F_RDLCK)
    - Reads file using read()
    - Multiple readers can download simultaneously (shared locks)
    """
    command = f"DOWNLOAD {filename}"
    
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
def api_delete(filename):
    """
    OS CONCEPT: File Deletion (unlink), Exclusive Locking (fcntl F_WRLCK)
    
    Forwards delete request to C server which:
    - Acquires write lock using fcntl(F_WRLCK)
    - Deletes file using unlink()
    - Prevents deletion while file is in use
    """
    command = f"DELETE {filename}"
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
def api_list():
    """
    OS CONCEPT: Directory Traversal (readdir), File Status (stat)
    
    Queries C server for file list which uses:
    - opendir() to open storage directory
    - readdir() to iterate files
    - stat() to get file sizes
    """
    command = "LIST"
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
                    size_str = parts[1].split()[0]
                    files.append({
                        'name': filename,
                        'size': int(size_str),
                        'size_human': format_bytes(int(size_str))
                    })
        
        log_event('LIST', f"ok - {len(files)} files")
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
def api_status():
    """
    OS CONCEPT: System Status Monitoring
    
    Provides observability into:
    - C server uptime
    - Active files (from C server via LIST command)
    - System health
    """
    try:
        # Get file list from C server (authoritative source)
        list_result = send_to_c_server("LIST")
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
    print("       ↓ TCP/IPC")
    print("  Python API Layer (This)")
    print("       ↓ HTTP/JSON")
    print("  Web Dashboard (Browser)")
    print()
    print("ALL FILE OPERATIONS HAPPEN IN C SERVER")
    print("This layer only forwards requests and visualizes state")
    print("=" * 70)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
