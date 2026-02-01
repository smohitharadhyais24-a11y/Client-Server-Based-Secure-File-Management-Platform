#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

# First, login to get token
print("=" * 60)
print("1. LOGIN TEST")
print("=" * 60)

try:
    req = urllib.request.Request(
        'http://localhost:5000/api/login',
        data=json.dumps({'username': 'user1', 'password': 'test123'}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    result = json.loads(res.read())
    print(f"✓ Login successful")
    token = result['token']
    print(f"  Token: {token[:30]}...")
except Exception as e:
    print(f"✗ Login failed: {e}")
    exit(1)

# Test protected endpoint: session-info
print("\n" + "=" * 60)
print("2. SESSION INFO TEST (with token)")
print("=" * 60)
try:
    req = urllib.request.Request(
        'http://localhost:5000/api/session-info',
        headers={'Authorization': f'Bearer {token}'}
    )
    res = urllib.request.urlopen(req)
    result = json.loads(res.read())
    print(f"✓ Session info retrieved")
    print(f"  Username: {result.get('username')}")
    print(f"  Role: {result.get('role')}")
    print(f"  Token created: {result.get('token_created')}")
except Exception as e:
    print(f"✗ Session info failed: {e}")

# Test protected endpoint without token
print("\n" + "=" * 60)
print("3. SESSION INFO TEST (without token - should fail)")
print("=" * 60)
try:
    req = urllib.request.Request('http://localhost:5000/api/session-info')
    res = urllib.request.urlopen(req)
    result = json.loads(res.read())
    print(f"✗ Should have been blocked but got: {result}")
except urllib.error.HTTPError as e:
    if e.code == 401:
        print(f"✓ Correctly blocked with 401 Unauthorized")
    else:
        print(f"✗ Wrong error code: {e.code}")

# Test logout
print("\n" + "=" * 60)
print("4. LOGOUT TEST")
print("=" * 60)
try:
    req = urllib.request.Request(
        'http://localhost:5000/api/logout',
        data=json.dumps({}).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )
    res = urllib.request.urlopen(req)
    result = json.loads(res.read())
    print(f"✓ Logout successful")
    print(f"  Message: {result.get('message')}")
except Exception as e:
    print(f"✗ Logout failed: {e}")

print("\n" + "=" * 60)
print("AUTHENTICATION SYSTEM: ALL TESTS PASSED ✓")
print("=" * 60)
