#!/usr/bin/env python3
"""
Integration Test Script - PHASES 3-4c
Tests all dashboard features end-to-end
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("OS FILE SERVER - INTEGRATION TEST")
print("=" * 70)

# Test 1: Dashboard HTML loads
print("\n[TEST 1] Dashboard HTML Load")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/")
    if r.status_code == 200:
        print("✓ Dashboard HTML loaded successfully (200 OK)")
        print(f"  Response size: {len(r.text)} bytes")
        if "dashboard" in r.text.lower() and "PHASE 4" in r.text:
            print("✓ Dashboard content verified")
        else:
            print("✗ Dashboard content missing")
    else:
        print(f"✗ Dashboard load failed: {r.status_code}")
except Exception as e:
    print(f"✗ Dashboard test error: {e}")

# Test 2: Dashboard JS loads
print("\n[TEST 2] Dashboard JavaScript Load")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/dashboard.js")
    if r.status_code == 200:
        print("✓ Dashboard JS loaded successfully (200 OK)")
        print(f"  Response size: {len(r.text)} bytes")
        if "PHASE 4b-4c" in r.text or "apiCall" in r.text:
            print("✓ JavaScript content verified")
        else:
            print("✗ JavaScript content missing")
    else:
        print(f"✗ Dashboard JS load failed: {r.status_code}")
except Exception as e:
    print(f"✗ Dashboard JS test error: {e}")

# Test 3: Login endpoint
print("\n[TEST 3] Authentication - Login")
print("-" * 70)
auth_token = None
try:
    login_data = {
        "username": "user1",
        "password": "test123"
    }
    r = requests.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            auth_token = data.get('token')
            print(f"✓ Login successful")
            print(f"  Token: {auth_token[:20]}...")
        else:
            print(f"✗ Login failed: {data.get('error')}")
    else:
        print(f"✗ Login endpoint error: {r.status_code}")
        print(f"Response: {r.text[:200]}")
except Exception as e:
    print(f"✗ Login test error: {e}")

if not auth_token:
    print("\n⚠ Cannot continue without auth token")
    exit(1)

headers = {"Authorization": f"Bearer {auth_token}"}

# Test 4: Status endpoint
print("\n[TEST 4] API - System Status")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/api/status", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            status = data.get('status', {})
            print("✓ Status endpoint working")
            print(f"  Files: {status.get('file_count', 'N/A')}")
            print(f"  C Server: {'Running' if status.get('c_server_running') else 'Offline'}")
            print(f"  Audit logs: {status.get('audit_log_entries', 'N/A')}")
        else:
            print(f"✗ Status error: {data.get('error')}")
    else:
        print(f"✗ Status endpoint failed: {r.status_code}")
except Exception as e:
    print(f"✗ Status test error: {e}")

# Test 5: Logs endpoint
print("\n[TEST 5] API - Audit Logs")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/api/logs", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            logs = data.get('logs', [])
            print(f"✓ Logs endpoint working")
            print(f"  Total logs: {len(logs)}")
            if logs:
                print(f"  Latest: {logs[-1]}")
        else:
            print(f"✗ Logs error: {data.get('error')}")
    else:
        print(f"✗ Logs endpoint failed: {r.status_code}")
except Exception as e:
    print(f"✗ Logs test error: {e}")

# Test 6: Locks endpoint
print("\n[TEST 6] API - File Locks")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/api/locks", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            locks = data.get('locks', [])
            print(f"✓ Locks endpoint working")
            print(f"  Active locks: {len(locks)}")
            if locks:
                print(f"  First lock: {locks[0]}")
        else:
            print(f"✗ Locks error: {data.get('error')}")
    else:
        print(f"✗ Locks endpoint failed: {r.status_code}")
except Exception as e:
    print(f"✗ Locks test error: {e}")

# Test 7: Security events endpoint
print("\n[TEST 7] API - Security Events (PHASE 3)")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/api/security/events", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            events = data.get('events', [])
            print(f"✓ Security events endpoint working")
            print(f"  Total events: {len(events)}")
            if events:
                print(f"  Sample: {events[0]}")
        else:
            print(f"✗ Events error: {data.get('error')}")
    else:
        print(f"✗ Security events endpoint failed: {r.status_code}")
except Exception as e:
    print(f"✗ Security events test error: {e}")

# Test 8: Security summary endpoint
print("\n[TEST 8] API - Security Summary")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/api/security/summary", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            summary = data.get('summary', {})
            print(f"✓ Security summary endpoint working")
            print(f"  Total events: {summary.get('total_events', 0)}")
            print(f"  High severity: {summary.get('high_severity_count', 0)}")
            print(f"  Blocked IPs: {summary.get('blocked_ips', 0)}")
        else:
            print(f"✗ Summary error: {data.get('error')}")
    else:
        print(f"✗ Security summary endpoint failed: {r.status_code}")
except Exception as e:
    print(f"✗ Security summary test error: {e}")

# Test 9: Security threats endpoint
print("\n[TEST 9] API - Security Threats")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/api/security/threats", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            threats = data.get('threats', [])
            threat_level = data.get('threat_level', 'NORMAL')
            print(f"✓ Security threats endpoint working")
            print(f"  Threat level: {threat_level}")
            print(f"  Critical/High threats: {len(threats)}")
            if threats:
                print(f"  Sample threat: {threats[0]}")
        else:
            print(f"✗ Threats error: {data.get('error')}")
    else:
        print(f"✗ Security threats endpoint failed: {r.status_code}")
except Exception as e:
    print(f"✗ Security threats test error: {e}")

# Test 10: List files endpoint
print("\n[TEST 10] API - File List")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/api/list", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            files = data.get('files', [])
            print(f"✓ File list endpoint working")
            print(f"  Total files: {len(files)}")
            if files:
                print(f"  Sample: {files[0]}")
        else:
            print(f"✗ List error: {data.get('error')}")
    else:
        print(f"✗ File list endpoint failed: {r.status_code}")
except Exception as e:
    print(f"✗ File list test error: {e}")

# Test 11: Logout endpoint
print("\n[TEST 11] Authentication - Logout")
print("-" * 70)
try:
    r = requests.post(f"{BASE_URL}/api/logout", headers=headers)
    if r.status_code == 200:
        data = r.json()
        if data.get('success'):
            print(f"✓ Logout successful")
        else:
            print(f"✗ Logout error: {data.get('error')}")
    else:
        print(f"✗ Logout endpoint failed: {r.status_code}")
except Exception as e:
    print(f"✗ Logout test error: {e}")

# Test 12: Verify logout - unauthorized request
print("\n[TEST 12] Authorization Check - Post-Logout")
print("-" * 70)
try:
    r = requests.get(f"{BASE_URL}/api/status", headers=headers)
    if r.status_code == 401:
        print(f"✓ Properly blocked unauthorized request (401)")
    else:
        print(f"⚠ Unexpected status: {r.status_code} (should be 401)")
except Exception as e:
    print(f"✗ Authorization check error: {e}")

print("\n" + "=" * 70)
print("INTEGRATION TEST COMPLETE")
print("=" * 70)
print("\nNext Steps:")
print("1. Open browser to http://localhost:5000")
print("2. Login with user1/test123")
print("3. Test file operations (upload/download/delete)")
print("4. Verify auto-polling updates stats")
print("5. Check security alerts")
print("6. Monitor console for any errors")
print("=" * 70)
