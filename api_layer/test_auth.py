#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from auth import auth_manager

# Test all three users
test_cases = [
    ('admin', 'password'),
    ('user1', 'test123'),
    ('user2', 'secret'),
]

for username, password in test_cases:
    success, msg, token = auth_manager.authenticate(username, password, '127.0.0.1')
    status = "✓ SUCCESS" if success else "✗ FAILED"
    print(f"{status} - {username}:{password} -> {msg}")
    if success:
        print(f"  Token: {token[:30]}...")
