#!/usr/bin/env python3
"""
SECURE FILE MANAGEMENT CLIENT
Terminal-based client for OS Lab demonstration
Connects to C-based file server via TCP sockets
"""

import socket
import os
import sys
import time

# Configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8888
BUFFER_SIZE = 4096

class FileClient:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
    
    def connect(self):
        """Create TCP socket connection to server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            return sock
        except ConnectionRefusedError:
            print(f"[ERROR] Cannot connect to server at {self.host}:{self.port}")
            print("[ERROR] Make sure the server is running")
            return None
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return None
    
    def upload_file(self, filepath, slow_ms=0):
        """
        Upload file to server
        Demonstrates: Bounded file transfer (deadlock prevention)
        Protocol: UPLOAD <filename> <filesize>\\n<filedata>
        """
        if not os.path.exists(filepath):
            print(f"[ERROR] File not found: {filepath}")
            return False
        
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        print(f"[UPLOAD] Connecting to server...")
        sock = self.connect()
        if not sock:
            return False
        
        try:
            if slow_ms > 0:
                print(f"[UPLOAD] Throttling enabled: {slow_ms} ms per chunk")
            # Send UPLOAD command with filename and filesize
            command = f"UPLOAD {filename} {filesize}\n"
            sock.sendall(command.encode())
            print(f"[UPLOAD] Sent command: UPLOAD {filename} {filesize}")
            
            # Wait for READY response
            response = sock.recv(BUFFER_SIZE).decode().strip()
            print(f"[UPLOAD] Server response: {response}")
            
            if not response.startswith("READY"):
                print(f"[ERROR] Server not ready: {response}")
                return False
            
            # Send file data (bounded transfer)
            print(f"[UPLOAD] Sending {filesize} bytes...")
            with open(filepath, 'rb') as f:
                total_sent = 0
                while total_sent < filesize:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    sock.sendall(chunk)
                    total_sent += len(chunk)

                    if slow_ms > 0:
                        time.sleep(slow_ms / 1000.0)
                    
                    # Progress indicator
                    progress = (total_sent / filesize) * 100
                    print(f"\r[UPLOAD] Progress: {progress:.1f}% ({total_sent}/{filesize} bytes)", end='')
            
            print()  # New line after progress
            
            # Wait for final response
            time.sleep(0.1)  # Give server time to process
            final_response = sock.recv(BUFFER_SIZE).decode().strip()
            print(f"[UPLOAD] Server response: {final_response}")
            
            if "SUCCESS" in final_response:
                print(f"[SUCCESS] File uploaded successfully!")
                return True
            else:
                print(f"[ERROR] Upload failed")
                return False
                
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
            return False
        finally:
            sock.close()
    
    def download_file(self, filename, save_path=None):
        """
        Download file from server
        Demonstrates: Bounded file transfer
        """
        if save_path is None:
            save_path = filename
        
        print(f"[DOWNLOAD] Connecting to server...")
        sock = self.connect()
        if not sock:
            return False
        
        try:
            # Send DOWNLOAD command
            command = f"DOWNLOAD {filename}\n"
            sock.sendall(command.encode())
            print(f"[DOWNLOAD] Sent command: DOWNLOAD {filename}")
            
            # Receive response with filesize
            response = sock.recv(BUFFER_SIZE).decode().strip()
            print(f"[DOWNLOAD] Server response: {response}")
            
            if not response.startswith("SUCCESS"):
                print(f"[ERROR] Download failed: {response}")
                return False
            
            # Parse filesize
            parts = response.split()
            if len(parts) < 2:
                print("[ERROR] Invalid response format")
                return False
            
            filesize = int(parts[1])
            print(f"[DOWNLOAD] Receiving {filesize} bytes...")
            
            # Receive file data (bounded transfer)
            with open(save_path, 'wb') as f:
                total_received = 0
                while total_received < filesize:
                    remaining = filesize - total_received
                    chunk_size = min(BUFFER_SIZE, remaining)
                    chunk = sock.recv(chunk_size)
                    
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    total_received += len(chunk)
                    
                    # Progress indicator
                    progress = (total_received / filesize) * 100
                    print(f"\r[DOWNLOAD] Progress: {progress:.1f}% ({total_received}/{filesize} bytes)", end='')
            
            print()  # New line after progress
            
            if total_received == filesize:
                print(f"[SUCCESS] File downloaded successfully to {save_path}")
                return True
            else:
                print(f"[ERROR] Incomplete download: received {total_received}/{filesize} bytes")
                return False
                
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            return False
        finally:
            sock.close()
    
    def list_files(self):
        """List all files on server"""
        print(f"[LIST] Connecting to server...")
        sock = self.connect()
        if not sock:
            return False
        
        try:
            # Send LIST command
            command = "LIST\n"
            sock.sendall(command.encode())
            print(f"[LIST] Sent command: LIST")
            
            # Receive response
            response = sock.recv(BUFFER_SIZE * 4).decode()
            print("\n" + "="*50)
            print(response)
            print("="*50)
            return True
            
        except Exception as e:
            print(f"[ERROR] List failed: {e}")
            return False
        finally:
            sock.close()
    
    def delete_file(self, filename):
        """Delete file from server"""
        print(f"[DELETE] Connecting to server...")
        sock = self.connect()
        if not sock:
            return False
        
        try:
            # Send DELETE command
            command = f"DELETE {filename}\n"
            sock.sendall(command.encode())
            print(f"[DELETE] Sent command: DELETE {filename}")
            
            # Receive response
            response = sock.recv(BUFFER_SIZE).decode().strip()
            print(f"[DELETE] Server response: {response}")
            
            if "SUCCESS" in response:
                print(f"[SUCCESS] File deleted successfully!")
                return True
            else:
                print(f"[ERROR] Delete failed")
                return False
                
        except Exception as e:
            print(f"[ERROR] Delete failed: {e}")
            return False
        finally:
            sock.close()
    
    def view_locks(self):
        """View current file locks"""
        print(f"[LOCKS] Connecting to server...")
        sock = self.connect()
        if not sock:
            return False
        
        try:
            # Send LOCKS command
            command = "LOCKS\n"
            sock.sendall(command.encode())
            print(f"[LOCKS] Sent command: LOCKS")
            
            # Receive response
            response = sock.recv(BUFFER_SIZE * 4).decode()
            print("\n" + "="*50)
            print(response)
            print("="*50)
            return True
            
        except Exception as e:
            print(f"[ERROR] View locks failed: {e}")
            return False
        finally:
            sock.close()
    
    def view_logs(self):
        """View audit logs"""
        print(f"[LOGS] Connecting to server...")
        sock = self.connect()
        if not sock:
            return False
        
        try:
            # Send LOGS command
            command = "LOGS\n"
            sock.sendall(command.encode())
            print(f"[LOGS] Sent command: LOGS")
            
            # Receive response
            response = sock.recv(BUFFER_SIZE * 4).decode()
            print("\n" + "="*50)
            print(response)
            print("="*50)
            return True
            
        except Exception as e:
            print(f"[ERROR] View logs failed: {e}")
            return False
        finally:
            sock.close()


def print_menu():
    """Display interactive menu"""
    print("\n" + "="*60)
    print(" SECURE FILE MANAGEMENT CLIENT - OS Lab Project")
    print("="*60)
    print(" 1. Upload File")
    print(" 2. Download File")
    print(" 3. List Files")
    print(" 4. Delete File")
    print(" 5. View File Locks")
    print(" 6. View Audit Logs")
    print(" 7. Exit")
    print("="*60)


def main():
    """Main interactive client loop"""
    client = FileClient()
    
    print("\n🔥 SECURE FILE MANAGEMENT CLIENT")
    print("Demonstrates: TCP Sockets, File I/O, Deadlock Prevention\n")
    
    if len(sys.argv) > 1:
        # Command-line mode
        command = sys.argv[1].upper()
        
        if command == "UPLOAD" and len(sys.argv) > 2:
            # Optional flag: --slow <ms> to throttle upload for demo concurrency
            args = sys.argv[2:]
            slow_ms = 0

            if "--slow" in args:
                idx = args.index("--slow")
                # Default to 50ms per chunk if no value provided
                if idx + 1 < len(args):
                    try:
                        slow_ms = int(args[idx + 1])
                        del args[idx:idx + 2]
                    except ValueError:
                        print("[ERROR] --slow expects an integer number of milliseconds")
                        return
                else:
                    slow_ms = 50
                    del args[idx]

            if not args:
                print("[ERROR] Please provide a file to upload")
                return

            filepath = args[0]
            client.upload_file(filepath, slow_ms=slow_ms)
        elif command == "DOWNLOAD" and len(sys.argv) > 2:
            save_path = sys.argv[3] if len(sys.argv) > 3 else sys.argv[2]
            client.download_file(sys.argv[2], save_path)
        elif command == "LIST":
            client.list_files()
        elif command == "DELETE" and len(sys.argv) > 2:
            client.delete_file(sys.argv[2])
        elif command == "LOCKS":
            client.view_locks()
        elif command == "LOGS":
            client.view_logs()
        else:
            print("Usage:")
            print("  python client.py UPLOAD <filepath> [--slow <ms>]")
            print("  python client.py DOWNLOAD <filename> [save_path]")
            print("  python client.py LIST")
            print("  python client.py DELETE <filename>")
            print("  python client.py LOCKS")
            print("  python client.py LOGS")
    else:
        # Interactive mode
        while True:
            print_menu()
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == '1':
                filepath = input("Enter file path to upload: ").strip()
                client.upload_file(filepath)
            elif choice == '2':
                filename = input("Enter filename to download: ").strip()
                save_path = input("Enter save path (press Enter for default): ").strip()
                save_path = save_path if save_path else filename
                client.download_file(filename, save_path)
            elif choice == '3':
                client.list_files()
            elif choice == '4':
                filename = input("Enter filename to delete: ").strip()
                confirm = input(f"Are you sure you want to delete '{filename}'? (yes/no): ").strip()
                if confirm.lower() == 'yes':
                    client.delete_file(filename)
            elif choice == '5':
                client.view_locks()
            elif choice == '6':
                client.view_logs()
            elif choice == '7':
                print("\n[EXIT] Goodbye!")
                break
            else:
                print("\n[ERROR] Invalid choice. Please enter 1-7.")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
