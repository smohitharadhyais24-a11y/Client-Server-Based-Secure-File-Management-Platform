"""
PHASE 3: Security & Intrusion Detection Module
===============================================
Implements rule-based security logic for OS events

Features:
- AUTH_FAIL tracking (3 failures = 600s IP block)
- PATH_TRAVERSAL detection (../ patterns)
- ACCESS_VIOLATION detection (concurrent write access)
- FILE_INTEGRITY_ALERT (hash mismatches)
- Automatic security event generation
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class SecurityManager:
    """
    OS Security Monitoring
    Detects and tracks security violations
    """
    
    def __init__(self):
        self.auth_failures = {}           # IP -> list of (timestamp, user)
        self.blocked_ips = {}             # IP -> block_expiry
        self.file_hashes = {}             # filename -> hash
        self.concurrent_writers = {}      # filename -> set of users
        self.security_events = []         # List of security events
        self.MAX_AUTH_FAILURES = 3
        self.BLOCK_DURATION = 600         # 600 seconds = 10 minutes
        self.load_security_state()
    
    def load_security_state(self):
        """Load existing security state from file"""
        try:
            state_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'auth', 'security_state.json'
            )
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.file_hashes = data.get('file_hashes', {})
        except Exception as e:
            print(f"[SECURITY] Warning loading state: {e}")
    
    def save_security_state(self):
        """Persist security state"""
        try:
            state_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'auth'
            )
            os.makedirs(state_dir, exist_ok=True)
            state_file = os.path.join(state_dir, 'security_state.json')
            with open(state_file, 'w') as f:
                json.dump({'file_hashes': self.file_hashes}, f)
        except Exception as e:
            print(f"[SECURITY] Warning saving state: {e}")
    
    def check_path_traversal(self, filename: str) -> Tuple[bool, str]:
        """
        Detect path traversal attempts (../ patterns)
        Returns: (is_safe, reason)
        """
        dangerous_patterns = ['../', '..\\', '~/', './..']
        filename_lower = filename.lower()
        
        for pattern in dangerous_patterns:
            if pattern in filename_lower:
                return False, f"PATH_TRAVERSAL detected: {pattern} in {filename}"
        
        # Check for absolute paths
        if filename.startswith('/') or (len(filename) > 1 and filename[1] == ':'):
            return False, f"ABSOLUTE_PATH detected: {filename}"
        
        return True, "Safe"
    
    def track_auth_failure(self, ip: str, username: str) -> Tuple[bool, str]:
        """
        Track failed authentication attempts
        Returns: (should_block, reason)
        """
        # Clean expired blocks
        self._clean_expired_blocks()
        
        # Check if already blocked
        if ip in self.blocked_ips:
            expiry = self.blocked_ips[ip]
            if datetime.now() < expiry:
                return False, f"IP {ip} blocked until {expiry.isoformat()}"
            else:
                del self.blocked_ips[ip]
                self.auth_failures[ip] = []
        
        # Track this failure
        if ip not in self.auth_failures:
            self.auth_failures[ip] = []
        
        self.auth_failures[ip].append({
            'timestamp': datetime.now().isoformat(),
            'username': username
        })
        
        failures = len(self.auth_failures[ip])
        
        # Generate security event
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'AUTH_FAIL',
            'ip': ip,
            'username': username,
            'failure_count': failures,
            'severity': 'HIGH' if failures >= 2 else 'MEDIUM'
        }
        self.security_events.append(event)
        
        # Block if threshold exceeded
        if failures >= self.MAX_AUTH_FAILURES:
            self.blocked_ips[ip] = datetime.now() + timedelta(seconds=self.BLOCK_DURATION)
            
            # Generate blocking event
            block_event = {
                'timestamp': datetime.now().isoformat(),
                'type': 'CLIENT_BLOCKED',
                'ip': ip,
                'reason': f'{failures} failed auth attempts',
                'severity': 'CRITICAL'
            }
            self.security_events.append(block_event)
            
            return False, f"IP blocked after {failures} failures"
        
        return True, f"Auth failure {failures}/3"
    
    def check_concurrent_access(self, filename: str, user: str, 
                               operation: str) -> Tuple[bool, str]:
        """
        Detect concurrent write access violations
        Returns: (is_safe, reason)
        """
        if operation.upper() != 'WRITE':
            return True, "Safe (read operation)"
        
        # Check if file is being written by another user
        if filename in self.concurrent_writers:
            writers = self.concurrent_writers[filename]
            if len(writers) > 0 and user not in writers:
                reason = f"CONCURRENT_WRITE: {filename} already being written by {writers}"
                
                # Generate security event
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'ACCESS_VIOLATION',
                    'file': filename,
                    'user': user,
                    'current_writers': list(writers),
                    'severity': 'HIGH'
                }
                self.security_events.append(event)
                
                return False, reason
        
        return True, "Safe (no concurrent access)"
    
    def check_file_integrity(self, filename: str, content: bytes) -> Tuple[bool, str]:
        """
        Check file integrity via hash verification
        Returns: (integrity_ok, reason)
        """
        try:
            current_hash = hashlib.sha256(content).hexdigest()
            
            if filename in self.file_hashes:
                expected_hash = self.file_hashes[filename]
                if current_hash != expected_hash:
                    reason = f"FILE_INTEGRITY_ALERT: {filename} hash mismatch"
                    
                    # Generate security event
                    event = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'FILE_INTEGRITY_ALERT',
                        'file': filename,
                        'expected_hash': expected_hash,
                        'actual_hash': current_hash,
                        'severity': 'CRITICAL'
                    }
                    self.security_events.append(event)
                    
                    # Update hash for future comparisons
                    self.file_hashes[filename] = current_hash
                    self.save_security_state()
                    
                    return False, reason
            else:
                # First time seeing this file, store hash
                self.file_hashes[filename] = current_hash
                self.save_security_state()
            
            return True, "Integrity verified"
        except Exception as e:
            return True, f"Could not check integrity: {e}"
    
    def track_file_operation(self, filename: str, user: str, operation: str):
        """Track file operation for concurrent access detection"""
        if operation.upper() == 'WRITE':
            if filename not in self.concurrent_writers:
                self.concurrent_writers[filename] = set()
            self.concurrent_writers[filename].add(user)
        
        # Generate operation event (non-security)
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': f'FILE_{operation.upper()}',
            'file': filename,
            'user': user,
            'severity': 'INFO'
        }
        self.security_events.append(event)
    
    def release_file_operation(self, filename: str, user: str, operation: str):
        """Release file operation tracking"""
        if operation.upper() == 'WRITE' and filename in self.concurrent_writers:
            self.concurrent_writers[filename].discard(user)
            if not self.concurrent_writers[filename]:
                del self.concurrent_writers[filename]
    
    def _clean_expired_blocks(self):
        """Remove expired IP blocks"""
        expired = [ip for ip, expiry in self.blocked_ips.items() 
                  if datetime.now() >= expiry]
        for ip in expired:
            del self.blocked_ips[ip]
            if ip in self.auth_failures:
                self.auth_failures[ip] = []
    
    def get_security_events(self, limit: int = 50) -> List[Dict]:
        """Get recent security events (last 'limit' events)"""
        return self.security_events[-limit:]
    
    def get_high_severity_events(self, limit: int = 20) -> List[Dict]:
        """Get high/critical severity events only"""
        high_events = [e for e in self.security_events 
                      if e.get('severity') in ['HIGH', 'CRITICAL']]
        return high_events[-limit:]
    
    def is_ip_blocked(self, ip: str) -> Tuple[bool, Optional[str]]:
        """Check if IP is currently blocked"""
        self._clean_expired_blocks()
        if ip in self.blocked_ips:
            expiry = self.blocked_ips[ip]
            if datetime.now() < expiry:
                return True, expiry.isoformat()
        return False, None
    
    def get_summary(self) -> Dict:
        """Get security summary"""
        high_sev = len([e for e in self.security_events 
                       if e.get('severity') in ['HIGH', 'CRITICAL']])
        
        return {
            'total_events': len(self.security_events),
            'high_severity': high_sev,
            'blocked_ips': len(self.blocked_ips),
            'tracked_files': len(self.file_hashes),
            'recent_events': self.security_events[-10:] if self.security_events else []
        }


# Global security manager instance
security_manager = SecurityManager()
