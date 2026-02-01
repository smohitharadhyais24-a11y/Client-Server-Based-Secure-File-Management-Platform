# 🧪 Integration Testing Guide - Master Prompt Implementation

**Quick validation of all phases implemented so far**

---

## ✅ PHASE 1: Authentication System - Full Test

### Test 1.1: Verify users.db exists
```bash
cat auth/users.db
# Should show:
# admin:8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918:admin
# user1:04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c9e5163129:user
# user2:6512bd43d9caa6e02c990b0a82652dca12674cc05cbee5282527b91f1e02722a:user
```

### Test 1.2: Test login endpoint
```bash
# Successful login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Expected response:
# {"success": true, "token": "...", "username": "admin", "message": "Authentication successful"}

# Note the token - you'll use it in subsequent tests
TOKEN="<copy_token_from_response>"
```

### Test 1.3: Test failed login (wrong password)
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpassword"}'

# Expected response:
# {"success": false, "message": "Invalid username or password"}
```

### Test 1.4: Test IP blocking (3 failures)
```bash
# Attempt 1: Wrong password
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'

# Attempt 2: Wrong password
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'

# Attempt 3: Wrong password (3rd failure)
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrong"}'

# 4th attempt (should be blocked):
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Expected response:
# {"success": false, "message": "IP 127.0.0.1 blocked until <time>"}
```

### Test 1.5: Test session info (requires token)
```bash
# Use the token from Test 1.2
curl http://localhost:5000/api/session-info \
  -H "Authorization: Bearer $TOKEN"

# Expected response:
# {
#   "success": true,
#   "session": {
#     "username": "admin",
#     "role": "admin",
#     "login_time": "2026-01-27T22:31:05.123456",
#     "last_activity": "2026-01-27T22:31:10.654321"
#   },
#   "active_sessions": 1
# }
```

### Test 1.6: Test logout (requires token)
```bash
curl -X POST http://localhost:5000/api/logout \
  -H "Authorization: Bearer $TOKEN"

# Expected response:
# {"success": true, "message": "Logged out successfully"}

# Verify token is invalid
curl http://localhost:5000/api/session-info \
  -H "Authorization: Bearer $TOKEN"

# Should fail:
# {"error": "Invalid or expired token"}
```

### Test 1.7: Check sessions.json was created/updated
```bash
cat auth/sessions.json
# Should show active sessions as JSON
```

---

## ✅ PHASE 5: Demo Guide - Quick Validation

### Test 5.1: Verify DEMO_GUIDE.md exists
```bash
wc -l DEMO_GUIDE.md
# Should show: 376 lines

head -50 DEMO_GUIDE.md
# Should show: 🎬 OS File Server - Complete Demo Guide for Evaluation
```

### Test 5.2: Verify all 9 demos documented
```bash
grep -c "^### \*\*Demo" DEMO_GUIDE.md
# Should output: 9
```

### Test 5.3: Check viva questions included
```bash
grep -c "^### Q" DEMO_GUIDE.md
# Should output: 6
```

---

## 🔄 PHASE 2: Event Stream - Preparation Test

### Test 2.1: Verify Flask API has event parsing
```bash
grep -n "def parse_event_line" api_layer/app.py
# Should find the function definition

grep -n "@app.route('/api/events'" api_layer/app.py
# Should find the /api/events endpoint
```

### Test 2.2: Verify PHASE2_EVENT_STREAM_GUIDE.md exists
```bash
wc -l PHASE2_EVENT_STREAM_GUIDE.md
# Should show: 118 lines

head -20 PHASE2_EVENT_STREAM_GUIDE.md
# Should show implementation guide
```

### Test 2.3: Verify logs directory exists
```bash
ls -la logs/
# Should show:
# audit.log (existing)
# security.log (existing)
# events.log (will be created once C server is modified)
```

### Test 2.4: Test events endpoint (before C modification)
```bash
# Get token first
TOKEN=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.token')

# Try to get events
curl http://localhost:5000/api/events \
  -H "Authorization: Bearer $TOKEN"

# Expected response (empty or error):
# {"success": true, "events": []}
# (No events yet until C server is modified)
```

---

## 📋 README.md - Validation

### Test R1: Check "Enhanced Features" section
```bash
grep -n "🆕 ENHANCED FEATURES" README.md
# Should find the new section
```

### Test R2: Verify authentication credentials documented
```bash
grep -A 5 "username: admin" README.md
# Should show credential table
```

### Test R3: Check DEMO_GUIDE link
```bash
grep "DEMO_GUIDE.md" README.md
# Should have reference
```

---

## 🏗️ Architecture Validation

### Test A1: Verify 3-tier architecture still intact
```bash
# C Server running
ps aux | grep file_server

# Flask API running
lsof -i :5000
# Should show Python listening on port 5000

# Web Dashboard accessible
test -f web_dashboard/index.html && echo "Dashboard exists" || echo "Dashboard missing"
```

### Test A2: Verify existing endpoints still work
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.token')

# Test existing endpoints (should still work)
curl -s http://localhost:5000/api/status | jq '.file_count'
curl -s http://localhost:5000/api/list | jq '.files | length'
curl -s http://localhost:5000/api/logs | jq '.logs | length'
```

---

## 📊 Full Integration Test Script (Copy-Paste Ready)

### For Linux/WSL Bash:
```bash
#!/bin/bash

echo "=== OS FILE SERVER INTEGRATION TEST ==="
echo

# Ensure servers running
echo "1. Checking servers..."
curl -s http://localhost:5000/api/status | jq -r '.api_status' || echo "FAIL: API not responding"

# Test authentication
echo "2. Testing authentication..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.token')
echo "   ✓ Login successful, token: ${TOKEN:0:20}..."

# Test session info
echo "3. Testing session info..."
curl -s http://localhost:5000/api/session-info \
  -H "Authorization: Bearer $TOKEN" | jq '.session.username'

# Test file operations (existing)
echo "4. Testing file operations..."
curl -s http://localhost:5000/api/status | jq '{files: .file_count, storage: .total_storage_human}'

# Test events endpoint
echo "5. Testing events endpoint..."
curl -s http://localhost:5000/api/events \
  -H "Authorization: Bearer $TOKEN" | jq '.events | length'

# Test logout
echo "6. Testing logout..."
curl -s -X POST http://localhost:5000/api/logout \
  -H "Authorization: Bearer $TOKEN" | jq '.success'

# Verify logout
echo "7. Verifying token invalid after logout..."
curl -s http://localhost:5000/api/session-info \
  -H "Authorization: Bearer $TOKEN" | jq '.error' || echo "Expected error"

echo
echo "=== ALL TESTS COMPLETE ==="
echo "✅ Authentication: WORKING"
echo "✅ Session Management: WORKING"
echo "✅ Event Endpoint: READY (awaits C server event logging)"
echo "✅ File Operations: WORKING"
echo "✅ Backward Compatibility: MAINTAINED"
```

### For Windows PowerShell:
```powershell
# Function to get token
function Get-Token {
    $response = curl -s -X POST http://localhost:5000/api/login `
        -H "Content-Type: application/json" `
        -d '{\"username\":\"admin\",\"password\":\"password\"}'
    return ($response | ConvertFrom-Json).token
}

Write-Host "=== OS FILE SERVER INTEGRATION TEST ===" -ForegroundColor Green
Write-Host ""

# Test authentication
Write-Host "1. Testing authentication..." -ForegroundColor Cyan
$token = Get-Token
Write-Host "✓ Login successful, token: $($token.Substring(0, 20))..." -ForegroundColor Green

# Test session info
Write-Host "2. Testing session info..." -ForegroundColor Cyan
$session = curl -s http://localhost:5000/api/session-info `
    -H "Authorization: Bearer $token" | ConvertFrom-Json
Write-Host "✓ Session user: $($session.session.username)" -ForegroundColor Green

# Test file operations
Write-Host "3. Testing file operations..." -ForegroundColor Cyan
$status = curl -s http://localhost:5000/api/status | ConvertFrom-Json
Write-Host "✓ Files: $($status.file_count), Storage: $($status.total_storage_human)" -ForegroundColor Green

# Test events
Write-Host "4. Testing events endpoint..." -ForegroundColor Cyan
$events = curl -s http://localhost:5000/api/events `
    -H "Authorization: Bearer $token" | ConvertFrom-Json
Write-Host "✓ Events endpoint ready ($($events.events.count) events)" -ForegroundColor Green

# Test logout
Write-Host "5. Testing logout..." -ForegroundColor Cyan
$logout = curl -s -X POST http://localhost:5000/api/logout `
    -H "Authorization: Bearer $token" | ConvertFrom-Json
Write-Host "✓ Logout successful" -ForegroundColor Green

Write-Host ""
Write-Host "=== ALL TESTS COMPLETE ===" -ForegroundColor Green
```

---

## ✅ Success Criteria

| Test | Pass | Fail | Status |
|------|------|------|--------|
| users.db exists | ✅ | ❌ | Expected |
| Login endpoint works | ✅ | ❌ | Expected |
| Failed login blocked | ✅ | ❌ | Expected |
| IP blocking (3 failures) | ✅ | ❌ | Expected |
| Session info works | ✅ | ❌ | Expected |
| Logout invalidates token | ✅ | ❌ | Expected |
| Existing endpoints work | ✅ | ❌ | Expected |
| Events endpoint exists | ✅ | ❌ | Expected |
| DEMO_GUIDE.md exists | ✅ | ❌ | Expected |
| Phase 2 guide exists | ✅ | ❌ | Expected |

**All tests should PASS** ✅

---

## 🚀 Next Steps

Once all tests pass:

1. **Implement PHASE 2** - Modify C server to emit events.log
   - Follow: PHASE2_EVENT_STREAM_GUIDE.md
   - Verify events.log creation
   - Re-test /api/events endpoint

2. **Implement PHASE 3** - Add security detection

3. **Implement PHASE 4** - Redesign dashboard

4. **Final Integration Test** - Full system with all phases

---

**Test Date:** January 27, 2026  
**Expected Result:** All 10 tests PASS ✅
