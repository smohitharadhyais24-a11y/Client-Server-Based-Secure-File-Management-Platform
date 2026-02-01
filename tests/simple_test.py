#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

try:
    req = urllib.request.Request(
        'http://localhost:5000/api/login',
        data=json.dumps({'username': 'user1', 'password': 'test123'}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    print(f"Request: POST /api/login")
    print(f"Body: {json.dumps({'username': 'user1', 'password': 'test123'})}")
    
    res = urllib.request.urlopen(req)
    result = json.loads(res.read())
    print(f"Status: {res.status}")
    print(f"Response: {json.dumps(result, indent=2)}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}")
    try:
        body = json.loads(e.read())
        print(f"Response: {json.dumps(body, indent=2)}")
    except:
        print(f"Body: {e.read().decode()}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
