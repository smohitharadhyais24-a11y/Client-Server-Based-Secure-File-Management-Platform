# 🪟 WINDOWS SETUP GUIDE (WSL)

## Overview

This project requires a Linux environment. Windows users must use **WSL (Windows Subsystem for Linux)**.

---

## Step 1: Install WSL

### Option A: Quick Install (Windows 11 / Windows 10 version 2004+)

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
```

This installs Ubuntu by default. **Restart your computer** when prompted.

---

### Option B: Manual Install (Older Windows)

1. Enable WSL:
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   ```

2. Enable Virtual Machine Platform:
   ```powershell
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

3. Restart computer

4. Install Ubuntu from Microsoft Store:
   - Open Microsoft Store
   - Search "Ubuntu"
   - Click "Get" → Install

---

## Step 2: First-Time Setup

1. Launch **Ubuntu** from Start Menu

2. Create username and password when prompted:
   ```
   Enter new UNIX username: yourusername
   Enter new UNIX password: ********
   ```

3. Update packages:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

---

## Step 3: Install Required Tools

```bash
# Install GCC compiler
sudo apt install gcc -y

# Install make
sudo apt install make -y

# Install Python3 (usually pre-installed)
sudo apt install python3 -y

# Verify installations
gcc --version
make --version
python3 --version
```

---

## Step 4: Navigate to Project Folder

Your Windows drives are mounted at `/mnt/`:

```bash
# Navigate to project folder
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"

# Verify you're in the right place
ls -la
```

**Expected output:**
```
server/
client/
storage/
metadata/
logs/
test_files/
Makefile
README.md
```

---

## Step 5: Make Scripts Executable

```bash
# Make all shell scripts executable
chmod +x *.sh

# Verify
ls -la *.sh
```

---

## Step 6: Build and Run

```bash
# Build the server
make

# Start server
make run
```

**Expected output:**
```
=== SECURE FILE MANAGEMENT SERVER ===
[SERVER] Listening on port 8888...
```

---

## Step 7: Run Client (New Terminal)

Open a **new WSL terminal** (don't close server):

```bash
# Navigate to project
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"

# Run client
python3 client/client.py
```

---

## Common WSL Issues

### Issue 1: "Permission denied" when running scripts

**Solution:**
```bash
chmod +x *.sh
chmod +x client/client.py
```

---

### Issue 2: Line ending errors (^M characters)

**Cause:** Windows uses CRLF, Linux uses LF

**Solution:**
```bash
# Install dos2unix
sudo apt install dos2unix -y

# Convert all files
find . -type f -name "*.sh" -exec dos2unix {} \;
find . -type f -name "*.py" -exec dos2unix {} \;
```

---

### Issue 3: Cannot find project folder

**Remember:**
- Windows `C:\` → WSL `/mnt/c/`
- Windows `D:\` → WSL `/mnt/d/`

**Example:**
```bash
# Windows path:
C:\Users\S Mohith\Desktop\PROJECTS\3RD SEM\NEW OS

# WSL path:
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
```

---

### Issue 4: "Address already in use"

**Solution:**
```bash
# Find and kill process
lsof -ti:8888 | xargs kill -9

# Or
killall file_server

# Then restart
make run
```

---

## Opening Multiple WSL Terminals

### Method 1: Windows Terminal (Recommended)

1. Install **Windows Terminal** from Microsoft Store
2. Click **`+`** button (new tab)
3. Select **Ubuntu**

---

### Method 2: Start Menu

1. Open **Ubuntu** from Start Menu (Terminal 1)
2. Open **Ubuntu** again from Start Menu (Terminal 2)

---

### Method 3: WSL Command

In PowerShell or CMD:
```powershell
wsl
```

---

## Quick Reference

### Navigate to project:
```bash
cd "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS"
```

### Terminal 1 (Server):
```bash
make run
```

### Terminal 2 (Client):
```bash
python3 client/client.py
```

### Terminal 3 (For concurrent demo):
```bash
python3 client/client.py UPLOAD test_files/test3.txt
```

---

## File Editing in Windows

You can edit files using **Windows editors** (VS Code, Notepad++):

1. Navigate to project in Windows Explorer:
   ```
   C:\Users\S Mohith\Desktop\PROJECTS\3RD SEM\NEW OS
   ```

2. Edit files normally

3. Save

4. WSL will see changes immediately

**VS Code WSL Extension (Recommended):**
- Install "Remote - WSL" extension
- Click green button (bottom-left)
- Select "New WSL Window"
- Open project folder

---

## Verification

Run verification script:

```bash
bash verify_setup.sh
```

**Expected output:**
```
✓ GCC found
✓ Python3 found
✓ pthread support available
✓ All directories exist
✓ All files found
✓ All checks passed!
```

---

## Demo Day Checklist for Windows Users

Before evaluation:

1. ✅ WSL installed and working
2. ✅ Can open multiple WSL terminals
3. ✅ Project compiles: `make build`
4. ✅ Server starts: `make run`
5. ✅ Client connects: `python3 client/client.py LIST`
6. ✅ Have VS Code open with code (for walkthrough)
7. ✅ Practiced demo at least once

---

## Performance Tips

WSL performance is best when:
- ✅ Files are in WSL filesystem (`~/projects/`)
- ⚠️ Slower when files are in Windows (`/mnt/c/...`)

**For best performance (optional):**
```bash
# Copy project to WSL home
cp -r "/mnt/c/Users/S Mohith/Desktop/PROJECTS/3RD SEM/NEW OS" ~/os-project
cd ~/os-project
make run
```

---

## Troubleshooting WSL

### WSL won't start

**Solution:**
```powershell
# In PowerShell (Admin)
wsl --shutdown
wsl
```

---

### Reset WSL (emergency)

**Warning:** This deletes all WSL data!

```powershell
# In PowerShell (Admin)
wsl --unregister Ubuntu
wsl --install
```

---

## Alternative: Use Git Bash (Not Recommended)

Git Bash has limited UNIX support. **WSL is strongly recommended**.

If you must use Git Bash:
1. Install Git for Windows (includes Git Bash)
2. Navigate to project
3. Run: `bash demo_full.sh`

**Note:** Compilation might fail. Use WSL instead.

---

## Summary

1. **Install WSL** → `wsl --install`
2. **Install tools** → `sudo apt install gcc make python3`
3. **Navigate** → `cd "/mnt/c/Users/S Mohith/..."`
4. **Build** → `make`
5. **Run** → `make run` (Terminal 1) + `python3 client/client.py` (Terminal 2)

**You're ready for demo! 🚀**
