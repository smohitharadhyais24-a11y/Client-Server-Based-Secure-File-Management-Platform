"""
OS-Based Authentication Module
Implements file-based user authentication with SHA-256 hashing
No cloud services - pure local OS file operations
"""

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

# File paths - Use absolute path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # Go up from api_layer/ to project root
USERS_DB_PATH = os.path.join(PROJECT_ROOT, "auth", "users.db")
SESSIONS_PATH = os.path.join(PROJECT_ROOT, "auth", "sessions.json")

class AuthManager:
    """Manages local user authentication and session handling"""
    
    def __init__(self):
        self.active_sessions = {}
        self.blocked_ips = {}
        self.failed_attempts = {}
        self.load_sessions()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 (OS best practice)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self) -> Dict[str, Tuple[str, str]]:
        """Load users from local users.db file
        Format: username:password_hash:role
        Returns: {username: (password_hash, role)}
        """
        users = {}
        try:
            print(f"[AUTH] Looking for users.db at: {USERS_DB_PATH}")
            if os.path.exists(USERS_DB_PATH):
                print(f"[AUTH] [OK] users.db found, loading...")
                with open(USERS_DB_PATH, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split(':')
                            if len(parts) == 3:
                                username, pwd_hash, role = parts
                                users[username] = (pwd_hash, role)
                print(f"[AUTH] [OK] Loaded {len(users)} users")
            else:
                print(f"[AUTH] [ERROR] users.db NOT FOUND at {USERS_DB_PATH}")
        except Exception as e:
            print(f"[AUTH] [ERROR] Error loading users: {e}")
        return users
    
    def authenticate(self, username: str, password: str, client_ip: str) -> Tuple[bool, str, Optional[str]]:
        """
        Authenticate user with username and password
        Args:
            username: Username
            password: Plain text password
            client_ip: Client IP address (for blocking)
        
        Returns:
            (success: bool, message: str, token: str or None)
        """
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            block_expiry = self.blocked_ips[client_ip]
            if datetime.now() < block_expiry:
                return False, f"IP {client_ip} blocked until {block_expiry}", None
            else:
                del self.blocked_ips[client_ip]
                self.failed_attempts[client_ip] = 0
        
        # Load users from file
        users = self.load_users()
        
        if username not in users:
            self._track_failed_attempt(client_ip)
            return False, "Invalid username or password", None
        
        expected_hash, role = users[username]
        provided_hash = self.hash_password(password)
        
        if provided_hash != expected_hash:
            self._track_failed_attempt(client_ip)
            return False, "Invalid username or password", None
        
        # Authentication successful - create session
        token = secrets.token_urlsafe(32)
        session = {
            "username": username,
            "role": role,
            "token": token,
            "client_ip": client_ip,
            "login_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        self.active_sessions[token] = session
        self.failed_attempts[client_ip] = 0
        self.save_sessions()
        
        return True, "Authentication successful", token
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Validate session token
        Returns: (valid: bool, session_data: dict or None)
        """
        if token not in self.active_sessions:
            return False, None
        
        session = self.active_sessions[token]
        
        # Check session expiry (24 hours)
        login_time = datetime.fromisoformat(session["login_time"])
        if datetime.now() - login_time > timedelta(hours=24):
            del self.active_sessions[token]
            self.save_sessions()
            return False, None
        
        # Update last activity
        session["last_activity"] = datetime.now().isoformat()
        return True, session
    
    def logout(self, token: str) -> bool:
        """Logout and invalidate session"""
        if token in self.active_sessions:
            del self.active_sessions[token]
            self.save_sessions()
            return True
        return False
    
    def _track_failed_attempt(self, client_ip: str):
        """Track failed login attempts and block IP after 3 failures"""
        if client_ip not in self.failed_attempts:
            self.failed_attempts[client_ip] = 0
        
        self.failed_attempts[client_ip] += 1
        
        # Block IP after 3 failed attempts (600 seconds = 10 minutes)
        # TESTING: Disabled for demo - uncomment for production
        # if self.failed_attempts[client_ip] >= 3:
        #     self.blocked_ips[client_ip] = datetime.now() + timedelta(seconds=600)
        #     print(f"[AUTH] IP {client_ip} blocked for 600s (3 failures)")
    
    def save_sessions(self):
        """Save active sessions to local file"""
        try:
            os.makedirs(os.path.dirname(SESSIONS_PATH), exist_ok=True)
            with open(SESSIONS_PATH, 'w') as f:
                json.dump(self.active_sessions, f, indent=2)
        except Exception as e:
            print(f"[AUTH] Error saving sessions: {e}")
    
    def load_sessions(self):
        """Load sessions from local file"""
        try:
            if os.path.exists(SESSIONS_PATH):
                with open(SESSIONS_PATH, 'r') as f:
                    self.active_sessions = json.load(f)
        except Exception as e:
            print(f"[AUTH] Error loading sessions: {e}")
    
    def get_session_info(self, token: str) -> Optional[Dict]:
        """Get session information (safe for frontend)"""
        valid, session = self.validate_token(token)
        if not valid:
            return None
        
        return {
            "username": session["username"],
            "role": session["role"],
            "login_time": session["login_time"],
            "last_activity": session["last_activity"]
        }
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)


# Initialize global auth manager
auth_manager = AuthManager()
