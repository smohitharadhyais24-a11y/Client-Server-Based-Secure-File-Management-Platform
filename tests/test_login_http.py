#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

test_cases = [
    ('admin', 'password'),
    ('user1', 'test123'),
    ('user2', 'secret'),
]

for username, password in test_cases:
    try:
        req = urllib.request.Request(
            'http://localhost:5000/api/login',
            data=json.dumps({'username': username, 'password': password}).encode(),
            headers={'Content-Type': 'application/json'}
        )
        res = urllib.request.urlopen(req)
        result = json.loads(res.read())
        status = "✓" if result.get('success') else "✗"
        print(f"{status} {username}:{password} -> {result.get('message')}")
        if result.get('success'):
            print(f"  Token: {result.get('token', 'N/A')[:30]}...")
    except urllib.error.HTTPError as e:
        print(f"✗ {username}:{password} -> HTTP {e.code}: {e.reason}")
