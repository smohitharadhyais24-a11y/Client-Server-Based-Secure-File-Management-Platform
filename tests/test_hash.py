import hashlib

# Check what password corresponds to the hash in users.db
target_hash = "04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c9e5163129"

test_passwords = ['test123', 'password123', 'secret', 'test', 'password', 'user123']
for pwd in test_passwords:
    h = hashlib.sha256(pwd.encode()).hexdigest()
    match = " <-- MATCH!" if h == target_hash else ""
    print(f"{pwd:20} {h}{match}")

print("\nFor reference:")
print(f"test123 hashes to: {hashlib.sha256('test123'.encode()).hexdigest()}")
