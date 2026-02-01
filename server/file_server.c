/*
 * SECURE FILE MANAGEMENT SERVER
 * Operating System Concepts Implementation
 * - UNIX File I/O (open, read, write, lseek, stat)
 * - TCP Socket-based IPC
 * - File Locking with fcntl (F_RDLCK, F_WRLCK)
 * - Deadlock Prevention, Avoidance, and Recovery
 * - Multi-threaded processing with pthread
 * - Thread synchronization with mutex
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <errno.h>
#include <time.h>
#include <dirent.h>
#include <signal.h>
#include <openssl/sha.h>

// Configuration
#define PORT 8888
#define MAX_BUFFER 4096
#define MAX_PATH 512
#define STORAGE_DIR "./storage/"
#define METADATA_DIR "./metadata/"
#define LOG_DIR "./logs/"
#define SECURITY_LOG "./logs/security.log"
#define UPLOAD_TIMEOUT 300
#define MAX_FILENAME 256
#define AUTH_TOKEN_DEFAULT "os-core-token"
#define MAX_CLIENT_TRACK 128
#define MAX_TOKEN_LEN 128
#define FAILURE_THRESHOLD 3
#define BLOCK_SECONDS 600

// Global mutex for file locking simulation
pthread_mutex_t file_locks_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t metadata_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t log_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t security_mutex = PTHREAD_MUTEX_INITIALIZER;

// Structure to track locked files
#define MAX_LOCKED_FILES 100
typedef struct {
    char filename[MAX_FILENAME];
    int locked;
    pthread_t thread_id;
} locked_file_t;

locked_file_t locked_files[MAX_LOCKED_FILES];
int num_locked_files = 0;

// Client security tracking structures
typedef struct {
    char ip[INET_ADDRSTRLEN];
    int failures;
    time_t blocked_until;
} client_security_t;

static client_security_t client_tracker[MAX_CLIENT_TRACK];
static char auth_token[MAX_TOKEN_LEN] = AUTH_TOKEN_DEFAULT;

// Security helper functions
const char *get_auth_token() {
    char *env = getenv("FILE_SERVER_AUTH");
    if (env && strlen(env) < MAX_TOKEN_LEN) {
        strncpy(auth_token, env, MAX_TOKEN_LEN - 1);
        auth_token[MAX_TOKEN_LEN - 1] = '\0';
    }
    return auth_token;
}

int find_tracker_slot(const char *ip) {
    for (int i = 0; i < MAX_CLIENT_TRACK; i++) {
        if (client_tracker[i].ip[0] != '\0' && strcmp(client_tracker[i].ip, ip) == 0) {
            return i;
        }
    }
    for (int i = 0; i < MAX_CLIENT_TRACK; i++) {
        if (client_tracker[i].ip[0] == '\0') {
            strncpy(client_tracker[i].ip, ip, INET_ADDRSTRLEN - 1);
            client_tracker[i].ip[INET_ADDRSTRLEN - 1] = '\0';
            return i;
        }
    }
    return -1;
}

int is_client_blocked(const char *ip) {
    time_t now = time(NULL);
    pthread_mutex_lock(&security_mutex);
    int idx = find_tracker_slot(ip);
    int blocked = 0;
    if (idx >= 0 && client_tracker[idx].blocked_until > now) {
        blocked = 1;
    }
    pthread_mutex_unlock(&security_mutex);
    return blocked;
}

void record_failure(const char *ip, const char *reason) {
    time_t now = time(NULL);
    pthread_mutex_lock(&security_mutex);
    int idx = find_tracker_slot(ip);
    if (idx >= 0) {
        client_tracker[idx].failures += 1;
        if (client_tracker[idx].failures >= FAILURE_THRESHOLD) {
            client_tracker[idx].blocked_until = now + BLOCK_SECONDS;
        }
    }
    pthread_mutex_unlock(&security_mutex);
    write_security_event("AUTH_FAILURE", ip, "N/A", reason);
}

void record_success(const char *ip) {
    pthread_mutex_lock(&security_mutex);
    int idx = find_tracker_slot(ip);
    if (idx >= 0) {
        client_tracker[idx].failures = 0;
        client_tracker[idx].blocked_until = 0;
    }
    pthread_mutex_unlock(&security_mutex);
}

int require_auth(char *buffer, int client_socket, const char *ip, char *command_out, size_t command_size) {
    // Expect first line: AUTH <token>
    char *newline = strchr(buffer, '\n');
    char *first_line = buffer;
    char *rest = NULL;
    if (newline) {
        *newline = '\0';
        rest = newline + 1;
    }

    if (strncmp(first_line, "AUTH", 4) != 0) {
        send_response(client_socket, "ERROR", "Auth required: send AUTH <token> before command");
        record_failure(ip, "Missing AUTH header");
        return -1;
    }

    char provided[MAX_TOKEN_LEN];
    if (sscanf(first_line, "AUTH %127s", provided) != 1) {
        send_response(client_socket, "ERROR", "Invalid AUTH format");
        record_failure(ip, "Malformed AUTH line");
        return -1;
    }

    if (strcmp(provided, get_auth_token()) != 0) {
        send_response(client_socket, "ERROR", "Unauthorized client");
        record_failure(ip, "Wrong token");
        return -1;
    }

    record_success(ip);

    // If there is no remaining command in buffer, read once more
    if (rest == NULL || strlen(rest) == 0) {
        ssize_t cmd_read = read(client_socket, buffer, MAX_BUFFER - 1);
        if (cmd_read <= 0) {
            send_response(client_socket, "ERROR", "No command after AUTH");
            return -1;
        }
        buffer[cmd_read] = '\0';
        rest = buffer;
    }

    // Copy the remaining command to output
    strncpy(command_out, rest, command_size - 1);
    command_out[command_size - 1] = '\0';
    return 0;
}

// Lock a file globally
int acquire_global_lock(const char *filename) {
    pthread_mutex_lock(&file_locks_mutex);
    
    // Check if file is already locked
    for (int i = 0; i < num_locked_files; i++) {
        if (strcmp(locked_files[i].filename, filename) == 0 && locked_files[i].locked) {
            pthread_mutex_unlock(&file_locks_mutex);
            return -1;  // File is locked
        }
    }
    
    // Lock the file
    for (int i = 0; i < MAX_LOCKED_FILES; i++) {
        if (!locked_files[i].locked) {
            strncpy(locked_files[i].filename, filename, MAX_FILENAME - 1);
            locked_files[i].filename[MAX_FILENAME - 1] = '\0';
            locked_files[i].locked = 1;
            locked_files[i].thread_id = pthread_self();
            if (i + 1 > num_locked_files) {
                num_locked_files = i + 1;
            }
            pthread_mutex_unlock(&file_locks_mutex);
            return 0;  // Lock acquired
        }
    }
    
    pthread_mutex_unlock(&file_locks_mutex);
    return -1;  // No space
}

// Unlock a file globally
void release_global_lock(const char *filename) {
    pthread_mutex_lock(&file_locks_mutex);
    
    for (int i = 0; i < num_locked_files; i++) {
        if (strcmp(locked_files[i].filename, filename) == 0 && locked_files[i].locked) {
            locked_files[i].locked = 0;
            break;
        }
    }
    
    pthread_mutex_unlock(&file_locks_mutex);
}

// Structure for client handler thread
typedef struct {
    int client_socket;
    struct sockaddr_in client_addr;
    int thread_id;
    char ip[INET_ADDRSTRLEN];
} client_info_t;

// Function prototypes
void *handle_client(void *arg);
void handle_upload(int client_socket, char *filename, long filesize);
void handle_download(int client_socket, char *filename);
void handle_list(int client_socket, const char *username);
void handle_delete(int client_socket, char *filename);
void handle_locks(int client_socket);
void handle_logs(int client_socket);
void write_audit_log(const char *operation, const char *filename, const char *status, const char *details);
void update_metadata(const char *filename, long filesize, const char *hash_hex);
int acquire_file_lock(int fd, short lock_type);
void release_file_lock(int fd);
void send_response(int socket, const char *status, const char *message);
char *get_timestamp();
char *compute_sha256_file(const char *path);
void write_security_event(const char *event, const char *ip, const char *filename, const char *details);
int is_client_blocked(const char *ip);
void record_failure(const char *ip, const char *reason);
void record_success(const char *ip);
int require_auth(char *buffer, int client_socket, const char *ip, char *command_out, size_t command_size);
const char *get_auth_token();

/*
 * Main Server Function
 * - Creates TCP socket
 * - Binds to port
 * - Listens for connections
 * - Spawns thread for each client (demonstrates process/thread management)
 */
int main() {
    int server_socket, client_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len;
    pthread_t thread_id;
    int thread_counter = 0;

    // Ignore SIGPIPE (broken pipe) to prevent server crash
    signal(SIGPIPE, SIG_IGN);

    // Load auth token from environment if provided
    get_auth_token();

    // Create directories if they don't exist
    mkdir(STORAGE_DIR, 0755);
    mkdir(METADATA_DIR, 0755);
    mkdir(LOG_DIR, 0755);

    printf("=== SECURE FILE MANAGEMENT SERVER ===\n");
    printf("Operating System Concepts: File I/O, IPC, Locking, Deadlock Prevention\n\n");

    // Create socket using UNIX socket API
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // Set socket options to reuse address (avoid "Address already in use")
    int opt = 1;
    if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Setsockopt failed");
        exit(EXIT_FAILURE);
    }

    // Configure server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    // Bind socket to address
    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(server_socket);
        exit(EXIT_FAILURE);
    }

    // Listen for connections (max queue: 5)
    if (listen(server_socket, 5) < 0) {
        perror("Listen failed");
        close(server_socket);
        exit(EXIT_FAILURE);
    }

    printf("[SERVER] Listening on port %d...\n", PORT);
    write_audit_log("SERVER_START", "N/A", "SUCCESS", "File server started");

    // Accept client connections in loop
    while (1) {
        client_len = sizeof(client_addr);
        client_socket = accept(server_socket, (struct sockaddr *)&client_addr, &client_len);
        
        if (client_socket < 0) {
            perror("Accept failed");
            continue;
        }

        char ip_str[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &(client_addr.sin_addr), ip_str, INET_ADDRSTRLEN);

        if (is_client_blocked(ip_str)) {
            send_response(client_socket, "ERROR", "Client blocked due to repeated failures");
            write_security_event("BLOCKED_CLIENT", ip_str, "N/A", "Connection rejected");
            close(client_socket);
            continue;
        }

        printf("[SERVER] New client connected from %s:%d\n", ip_str, ntohs(client_addr.sin_port));

        // Create client info structure
        client_info_t *client_info = malloc(sizeof(client_info_t));
        client_info->client_socket = client_socket;
        client_info->client_addr = client_addr;
        client_info->thread_id = ++thread_counter;
        strncpy(client_info->ip, ip_str, INET_ADDRSTRLEN - 1);
        client_info->ip[INET_ADDRSTRLEN - 1] = '\0';

        // Spawn thread to handle client (demonstrates thread management)
        if (pthread_create(&thread_id, NULL, handle_client, (void *)client_info) != 0) {
            perror("Thread creation failed");
            close(client_socket);
            free(client_info);
            continue;
        }

        // Detach thread (auto cleanup when done)
        pthread_detach(thread_id);
    }

    close(server_socket);
    return 0;
}

/*
 * Client Handler Thread
 * - Reads command from client
 * - Routes to appropriate handler
 * - Demonstrates: Thread management, Command parsing
 */
void *handle_client(void *arg) {
    client_info_t *info = (client_info_t *)arg;
    int client_socket = info->client_socket;
    char buffer[MAX_BUFFER];
    
    printf("[THREAD-%d] Handling client\n", info->thread_id);

    // Read command from client
    memset(buffer, 0, MAX_BUFFER);
    ssize_t bytes_read = read(client_socket, buffer, MAX_BUFFER - 1);
    
    if (bytes_read <= 0) {
        printf("[THREAD-%d] Client disconnected\n", info->thread_id);
        close(client_socket);
        free(info);
        return NULL;
    }

    buffer[bytes_read] = '\0';

    char command_buffer[MAX_BUFFER];
    if (require_auth(buffer, client_socket, info->ip, command_buffer, sizeof(command_buffer)) != 0) {
        printf("[THREAD-%d] Auth failed for %s\n", info->thread_id, info->ip);
        close(client_socket);
        free(info);
        return NULL;
    }

    printf("[THREAD-%d] Received command: %s\n", info->thread_id, command_buffer);

    // Parse command
    char command[32], filename[MAX_FILENAME];
    long filesize = 0;

    if (strncmp(command_buffer, "UPLOAD", 6) == 0) {
        // Format: UPLOAD <filename> <filesize>
        if (sscanf(command_buffer, "UPLOAD %s %ld", filename, &filesize) == 2) {
            if (filesize <= 0 || filesize > 1024 * 1024 * 100) { // Max 100MB
                send_response(client_socket, "ERROR", "Invalid file size");
            } else {
                handle_upload(client_socket, filename, filesize);
            }
        } else {
            send_response(client_socket, "ERROR", "Invalid UPLOAD command format");
        }
    } else if (strncmp(command_buffer, "DOWNLOAD", 8) == 0) {
        // Format: DOWNLOAD <filename>
        if (sscanf(command_buffer, "DOWNLOAD %s", filename) == 1) {
            handle_download(client_socket, filename);
        } else {
            send_response(client_socket, "ERROR", "Invalid DOWNLOAD command format");
        }
    } else if (strncmp(command_buffer, "LIST", 4) == 0) {
        // Format: LIST [username] - optional username for user-specific listing
        char username[MAX_FILENAME] = "";
        sscanf(command_buffer, "LIST %s", username);
        handle_list(client_socket, username);
    } else if (strncmp(command_buffer, "DELETE", 6) == 0) {
        // Format: DELETE <filename>
        if (sscanf(command_buffer, "DELETE %s", filename) == 1) {
            handle_delete(client_socket, filename);
        } else {
            send_response(client_socket, "ERROR", "Invalid DELETE command format");
        }
    } else if (strncmp(command_buffer, "LOCKS", 5) == 0) {
        handle_locks(client_socket);
    } else if (strncmp(command_buffer, "LOGS", 4) == 0) {
        handle_logs(client_socket);
    } else {
        send_response(client_socket, "ERROR", "Unknown command");
        write_security_event("ACCESS_VIOLATION", info->ip, "N/A", command_buffer);
    }

    close(client_socket);
    free(info);
    printf("[THREAD-%d] Client handler finished\n", info->thread_id);
    return NULL;
}

/*
 * UPLOAD Handler
 * Demonstrates:
 * - Bounded file transfer (DEADLOCK PREVENTION)
 * - File locking with fcntl (F_WRLCK)
 * - Non-blocking lock acquisition (DEADLOCK AVOIDANCE)
 * - Timeout mechanism (DEADLOCK RECOVERY)
 * - UNIX file I/O (open, write)
 * - Minimal critical section (lock held only during write)
 */
void handle_upload(int client_socket, char *filename, long filesize) {
    char filepath[MAX_PATH];
    char buffer[MAX_BUFFER];
    char dir_path[MAX_PATH];
    int fd;
    ssize_t bytes_read, total_read = 0;
    time_t start_time, current_time;
    
    // Allow username/filename format for user-specific storage
    // Validate that only ONE slash exists and it's not at start/end
    int slash_count = 0;
    char *slash_pos = NULL;
    for (char *p = filename; *p; p++) {
        if (*p == '/' || *p == '\\\\') {
            slash_count++;
            slash_pos = p;
        }
    }
    
    // Check for path traversal attempts (..)
    if (strstr(filename, "..") || filename[0] == '/' || filename[0] == '\\\\') {
        send_response(client_socket, "ERROR", "Invalid filename");
        write_audit_log("UPLOAD", filename, "FAILED", "Invalid filename");
        write_security_event("ACCESS_VIOLATION", "", filename, "Path traversal attempt");
        return;
    }
    
    // If filename contains username/, create the user directory
    if (slash_count == 1 && slash_pos && slash_pos != filename && slash_pos[1] != '\\0') {
        // Extract username directory
        int username_len = slash_pos - filename;
        snprintf(dir_path, MAX_PATH, "%s%.*s", STORAGE_DIR, username_len, filename);
        
        // Create user directory if it doesn't exist
        struct stat st = {0};
        if (stat(dir_path, &st) == -1) {
            if (mkdir(dir_path, 0755) != 0) {
                send_response(client_socket, "ERROR", "Cannot create user directory");
                write_audit_log("UPLOAD", filename, "FAILED", "Directory creation error");
                return;
            }
        }
    } else if (slash_count > 1) {
        send_response(client_socket, "ERROR", "Invalid filename - too many path separators");
        write_audit_log("UPLOAD", filename, "FAILED", "Invalid filename");
        write_security_event("ACCESS_VIOLATION", "", filename, "Multiple path separators");
        return;
    }

    // Construct file path
    snprintf(filepath, MAX_PATH, "%s%s", STORAGE_DIR, filename);
    printf("[DEBUG] Attempting to lock: %s\\n", filename);
    
    // DEADLOCK AVOIDANCE: Try to acquire GLOBAL write lock (non-blocking) BEFORE sending READY
    if (acquire_global_lock(filename) != 0) {
        printf("[DEBUG] Global lock FAILED - sending ERROR to client\n");
        send_response(client_socket, "ERROR", "File is locked by another process");
        write_audit_log("UPLOAD", filename, "FAILED", "File locked");
        return;
    }
    printf("[DEBUG] Global lock ACQUIRED\n");
    
    // Now open and truncate file safely (protected by lock)
    fd = open(filepath, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        printf("[DEBUG] Open failed\n");
        release_global_lock(filename);
        send_response(client_socket, "ERROR", "Cannot create file");
        write_audit_log("UPLOAD", filename, "FAILED", "File creation error");
        return;
    }
    printf("[DEBUG] File opened and truncated successfully, fd=%d\n", fd);

    // Send ready signal to client (AFTER global lock acquired and file prepared)
    send_response(client_socket, "READY", "Send file data");

    printf("[UPLOAD] Acquiring write lock on %s\n", filename);
    printf("[UPLOAD] Starting bounded transfer: %ld bytes\n", filesize);

    // DEADLOCK PREVENTION: Bounded read - read exactly filesize bytes
    // This prevents waiting for socket EOF which could cause deadlock
    start_time = time(NULL);
    
    while (total_read < filesize) {
        // DEADLOCK RECOVERY: Check timeout
        current_time = time(NULL);
        if (difftime(current_time, start_time) > UPLOAD_TIMEOUT) {
            printf("[UPLOAD] Timeout exceeded - DEADLOCK RECOVERY\n");
            send_response(client_socket, "ERROR", "Upload timeout");
            write_audit_log("UPLOAD", filename, "FAILED", "Timeout - deadlock recovery");
            release_global_lock(filename);
            close(fd);
            unlink(filepath); // Remove incomplete file
            return;
        }

        long remaining = filesize - total_read;
        long to_read = (remaining < MAX_BUFFER) ? remaining : MAX_BUFFER;
        
        bytes_read = read(client_socket, buffer, to_read);
        
        if (bytes_read <= 0) {
            if (bytes_read < 0 && errno == EINTR) continue; // Interrupted, retry
            printf("[UPLOAD] Connection error during transfer\n");
            send_response(client_socket, "ERROR", "Transfer interrupted");
            write_audit_log("UPLOAD", filename, "FAILED", "Connection error");
            release_global_lock(filename);
            close(fd);
            unlink(filepath);
            return;
        }

        // CRITICAL SECTION: Write to file (lock held)
        ssize_t bytes_written = write(fd, buffer, bytes_read);
        if (bytes_written != bytes_read) {
            send_response(client_socket, "ERROR", "Write error");
            write_audit_log("UPLOAD", filename, "FAILED", "Write error");
            release_global_lock(filename);
            close(fd);
            unlink(filepath);
            return;
        }

        total_read += bytes_read;
    }

    // Release lock BEFORE metadata/logging operations (MINIMIZE CRITICAL SECTION)
    release_global_lock(filename);
    close(fd);
    
    printf("[UPLOAD] Write lock released on %s\n", filename);
    printf("[UPLOAD] Successfully received %ld bytes\n", total_read);

    // Compute integrity hash and update metadata (outside critical section)
    char *hash_hex = compute_sha256_file(filepath);
    if (hash_hex) {
        update_metadata(filename, filesize, hash_hex);
        free(hash_hex);
    } else {
        update_metadata(filename, filesize, "HASH_ERROR");
    }
    
    // Log operation (outside critical section)
    char log_details[256];
    snprintf(log_details, 256, "Size: %ld bytes", filesize);
    write_audit_log("UPLOAD", filename, "SUCCESS", log_details);

    send_response(client_socket, "SUCCESS", "File uploaded successfully");
}

/*
 * DOWNLOAD Handler
 * Demonstrates:
 * - File locking with F_RDLCK (read lock)
 * - Multiple readers allowed (demonstrates shared locks)
 * - UNIX file I/O (open, read, stat)
 */
void handle_download(int client_socket, char *filename) {
    char filepath[MAX_PATH];
    char buffer[MAX_BUFFER];
    int fd;
    struct stat file_stat;
    ssize_t bytes_read;

    // Allow username/filename format, check for path traversal
    int slash_count = 0;
    for (char *p = filename; *p; p++) {
        if (*p == '/' || *p == '\\\\') slash_count++;
    }
    
    if (strstr(filename, "..") || filename[0] == '/' || filename[0] == '\\\\' || slash_count > 1) {
        send_response(client_socket, "ERROR", "Invalid filename");
        write_security_event("ACCESS_VIOLATION", "", filename, "Path traversal attempt");
        return;
    }

    snprintf(filepath, MAX_PATH, "%s%s", STORAGE_DIR, filename);

    // Check if file exists using stat()
    if (stat(filepath, &file_stat) != 0) {
        send_response(client_socket, "ERROR", "File not found");
        write_audit_log("DOWNLOAD", filename, "FAILED", "File not found");
        return;
    }

    // Open file for reading
    fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        send_response(client_socket, "ERROR", "Cannot open file");
        write_audit_log("DOWNLOAD", filename, "FAILED", "Open error");
        return;
    }

    // Acquire read lock (allows multiple readers)
    if (acquire_file_lock(fd, F_RDLCK) != 0) {
        send_response(client_socket, "ERROR", "File is locked for writing");
        write_audit_log("DOWNLOAD", filename, "FAILED", "File locked");
        close(fd);
        return;
    }

    printf("[DOWNLOAD] Acquired read lock on %s\n", filename);

    // Integrity check before sending
    char expected_hash[SHA256_DIGEST_LENGTH * 2 + 1];
    expected_hash[0] = '\0';
    char meta_path[MAX_PATH];
    snprintf(meta_path, MAX_PATH, "%s%s.meta", METADATA_DIR, filename);
    int meta_fd = open(meta_path, O_RDONLY);
    if (meta_fd >= 0) {
        char meta_buf[512];
        ssize_t mread = read(meta_fd, meta_buf, sizeof(meta_buf) - 1);
        if (mread > 0) {
            meta_buf[mread] = '\0';
            char *hash_line = strstr(meta_buf, "SHA256:");
            if (hash_line) {
                sscanf(hash_line, "SHA256: %64s", expected_hash);
            }
        }
        close(meta_fd);
    }

    char *actual_hash = compute_sha256_file(filepath);
    if (expected_hash[0] != '\0' && actual_hash && strcmp(expected_hash, actual_hash) != 0) {
        write_security_event("INTEGRITY_FAIL", "", filename, "Hash mismatch detected before download");
        send_response(client_socket, "ERROR", "Integrity check failed");
        release_file_lock(fd);
        close(fd);
        free(actual_hash);
        return;
    }
    if (actual_hash) {
        free(actual_hash);
    }

    // Send response with file size
    char response[256];
    snprintf(response, 256, "SUCCESS %ld", file_stat.st_size);
    write(client_socket, response, strlen(response));
    write(client_socket, "\n", 1);

    // Send file data
    long total_sent = 0;
    while ((bytes_read = read(fd, buffer, MAX_BUFFER)) > 0) {
        ssize_t bytes_sent = write(client_socket, buffer, bytes_read);
        if (bytes_sent != bytes_read) {
            printf("[DOWNLOAD] Send error\n");
            break;
        }
        total_sent += bytes_sent;
    }

    // Release lock and close
    release_file_lock(fd);
    close(fd);

    printf("[DOWNLOAD] Released read lock on %s\n", filename);
    printf("[DOWNLOAD] Sent %ld bytes\n", total_sent);

    char log_details[256];
    snprintf(log_details, 256, "Size: %ld bytes", total_sent);
    write_audit_log("DOWNLOAD", filename, "SUCCESS", log_details);
}

/*
 * LIST Handler
 * Demonstrates: Directory traversal, stat() usage
 */
void handle_list(int client_socket, const char *username) {
    DIR *dir;
    struct dirent *entry;
    struct stat file_stat;
    char dirpath[MAX_PATH];
    char filepath[MAX_PATH];
    char response[MAX_BUFFER * 4];
    int count = 0;

    // If username provided, list only that user's directory
    if (username && username[0] != '\0') {
        snprintf(dirpath, MAX_PATH, "%s%s", STORAGE_DIR, username);
    } else {
        snprintf(dirpath, MAX_PATH, "%s", STORAGE_DIR);
    }

    dir = opendir(dirpath);
    if (dir == NULL) {
        send_response(client_socket, "ERROR", "Cannot open storage directory");
        return;
    }

    strcpy(response, "SUCCESS\n");

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue; // Skip hidden files
        
        snprintf(filepath, MAX_PATH, "%s/%s", dirpath, entry->d_name);
        
        if (stat(filepath, &file_stat) == 0 && S_ISREG(file_stat.st_mode)) {
            char line[512];
            if (username && username[0] != '\0') {
                // Include username prefix for consistency
                snprintf(line, 512, "%s/%s (%ld bytes)\n", username, entry->d_name, file_stat.st_size);
            } else {
                snprintf(line, 512, "%s (%ld bytes)\n", entry->d_name, file_stat.st_size);
            }
            strcat(response, line);
            count++;
        }
    }

    closedir(dir);

    if (count == 0) {
        strcat(response, "No files found\n");
    }

    write(client_socket, response, strlen(response));
    write_audit_log("LIST", username && username[0] ? username : "all", "SUCCESS", "Listed files");
}

/*
 * DELETE Handler
 * Demonstrates:
 * - File locking before deletion (prevents deletion while in use)
 * - UNIX unlink() system call
 */
void handle_delete(int client_socket, char *filename) {
    char filepath[MAX_PATH];
    int fd;

    // Allow username/filename format, check for path traversal
    int slash_count = 0;
    for (char *p = filename; *p; p++) {
        if (*p == '/' || *p == '\\\\') slash_count++;
    }
    
    if (strstr(filename, "..") || filename[0] == '/' || filename[0] == '\\\\' || slash_count > 1) {
        send_response(client_socket, "ERROR", "Invalid filename");
        write_security_event("ACCESS_VIOLATION", "", filename, "Invalid filename for delete");
        return;
    }

    snprintf(filepath, MAX_PATH, "%s%s", STORAGE_DIR, filename);

    // Check if file exists
    if (access(filepath, F_OK) != 0) {
        send_response(client_socket, "ERROR", "File not found");
        write_audit_log("DELETE", filename, "FAILED", "File not found");
        return;
    }

    // Open file to acquire lock
    fd = open(filepath, O_RDWR);
    if (fd < 0) {
        send_response(client_socket, "ERROR", "Cannot open file");
        write_audit_log("DELETE", filename, "FAILED", "Open error");
        return;
    }

    // Try to acquire exclusive lock (prevents deletion if file is in use)
    if (acquire_file_lock(fd, F_WRLCK) != 0) {
        send_response(client_socket, "ERROR", "File is currently in use");
        write_audit_log("DELETE", filename, "FAILED", "File locked");
        close(fd);
        return;
    }

    printf("[DELETE] Acquired lock on %s\n", filename);

    // Close and delete using unlink()
    close(fd);
    
    if (unlink(filepath) == 0) {
        send_response(client_socket, "SUCCESS", "File deleted successfully");
        write_audit_log("DELETE", filename, "SUCCESS", "File deleted");
        printf("[DELETE] File %s deleted\n", filename);
    } else {
        send_response(client_socket, "ERROR", "Delete failed");
        write_audit_log("DELETE", filename, "FAILED", "Unlink error");
    }
}

/*
 * LOCKS Handler - View current file locks
 */
void handle_locks(int client_socket) {
    DIR *dir;
    struct dirent *entry;
    char filepath[MAX_PATH];
    char response[MAX_BUFFER * 4];
    int locked_count = 0;

    dir = opendir(STORAGE_DIR);
    if (dir == NULL) {
        send_response(client_socket, "ERROR", "Cannot open storage directory");
        return;
    }

    strcpy(response, "SUCCESS\nFile Locks Status:\n");

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;
        
        snprintf(filepath, MAX_PATH, "%s%s", STORAGE_DIR, entry->d_name);
        
        int fd = open(filepath, O_RDONLY);
        if (fd < 0) continue;

        struct flock lock;
        lock.l_type = F_WRLCK;
        lock.l_whence = SEEK_SET;
        lock.l_start = 0;
        lock.l_len = 0;

        // Test if file is locked
        if (fcntl(fd, F_GETLK, &lock) == 0) {
            if (lock.l_type != F_UNLCK) {
                char line[256];
                snprintf(line, 256, "  LOCKED: %s (PID: %d)\n", entry->d_name, lock.l_pid);
                strcat(response, line);
                locked_count++;
            }
        }
        close(fd);
    }

    closedir(dir);

    if (locked_count == 0) {
        strcat(response, "  No locked files\n");
    }

    write(client_socket, response, strlen(response));
    write_audit_log("LOCKS", "N/A", "SUCCESS", "Viewed locks");
}

/*
 * LOGS Handler - View audit logs
 */
void handle_logs(int client_socket) {
    char logpath[MAX_PATH];
    char buffer[MAX_BUFFER];
    int fd;
    ssize_t bytes_read;

    snprintf(logpath, MAX_PATH, "%saudit.log", LOG_DIR);

    fd = open(logpath, O_RDONLY);
    if (fd < 0) {
        send_response(client_socket, "SUCCESS", "No logs available\n");
        return;
    }

    write(client_socket, "SUCCESS\n", 8);
    write(client_socket, "=== AUDIT LOGS ===\n", 19);

    // Read and send last 10KB of logs
    off_t file_size = lseek(fd, 0, SEEK_END);
    off_t start_pos = (file_size > 10240) ? (file_size - 10240) : 0;
    lseek(fd, start_pos, SEEK_SET);

    while ((bytes_read = read(fd, buffer, MAX_BUFFER - 1)) > 0) {
        write(client_socket, buffer, bytes_read);
    }

    close(fd);

    // Append security log
    int sfd = open(SECURITY_LOG, O_RDONLY);
    write(client_socket, "\n=== SECURITY LOGS ===\n", 24);
    if (sfd >= 0) {
        while ((bytes_read = read(sfd, buffer, MAX_BUFFER - 1)) > 0) {
            write(client_socket, buffer, bytes_read);
        }
        close(sfd);
    } else {
        write(client_socket, "No security events yet\n", 24);
    }
}

/*
 * File Locking Functions
 * Demonstrates: fcntl() system call for file locking
 * DEADLOCK AVOIDANCE: Uses F_SETLK (non-blocking) instead of F_SETLKW
 */
int acquire_file_lock(int fd, short lock_type) {
    struct flock lock;
    
    lock.l_type = lock_type;    // F_RDLCK or F_WRLCK
    lock.l_whence = SEEK_SET;   // Lock from beginning of file
    lock.l_start = 0;           // Start at byte 0
    lock.l_len = 0;             // Lock entire file (0 = to EOF)
    lock.l_pid = getpid();      // Process ID

    // F_SETLK: Non-blocking lock (DEADLOCK AVOIDANCE)
    // Returns immediately if lock cannot be acquired
    if (fcntl(fd, F_SETLK, &lock) == -1) {
        if (errno == EACCES || errno == EAGAIN) {
            printf("[LOCK] File already locked by another process\n");
            return -1;
        }
        perror("fcntl lock error");
        return -1;
    }

    return 0;
}

void release_file_lock(int fd) {
    struct flock lock;
    
    lock.l_type = F_UNLCK;      // Unlock
    lock.l_whence = SEEK_SET;
    lock.l_start = 0;
    lock.l_len = 0;

    if (fcntl(fd, F_SETLK, &lock) == -1) {
        perror("fcntl unlock error");
    }
}

/*
 * Metadata Management
 * Demonstrates: Thread synchronization with mutex
 */
void update_metadata(const char *filename, long filesize, const char *hash_hex) {
    char metapath[MAX_PATH];
    int fd;
    char metadata[768];
    time_t now = time(NULL);

    // THREAD SYNCHRONIZATION: Lock mutex for metadata access
    pthread_mutex_lock(&metadata_mutex);

    snprintf(metapath, MAX_PATH, "%s%s.meta", METADATA_DIR, filename);
    
    fd = open(metapath, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd >= 0) {
        snprintf(metadata, sizeof(metadata),
                 "Filename: %s\nSize: %ld\nUploadTime: %sSHA256: %s\n",
                 filename, filesize, ctime(&now), hash_hex ? hash_hex : "UNKNOWN");
        write(fd, metadata, strlen(metadata));
        close(fd);
    }

    pthread_mutex_unlock(&metadata_mutex);
}

/*
 * Audit Logging
 * Demonstrates: Thread-safe append-only logging
 */
void write_audit_log(const char *operation, const char *filename, 
                     const char *status, const char *details) {
    char logpath[MAX_PATH];
    int fd;
    char log_entry[1024];

    snprintf(logpath, MAX_PATH, "%saudit.log", LOG_DIR);

    // THREAD SYNCHRONIZATION: Lock mutex for log access
    pthread_mutex_lock(&log_mutex);

    fd = open(logpath, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd >= 0) {
        char *timestamp = get_timestamp();
        snprintf(log_entry, 1024, "[%s] OPERATION=%s FILE=%s STATUS=%s DETAILS=%s\n",
                 timestamp, operation, filename, status, details);
        write(fd, log_entry, strlen(log_entry));
        close(fd);
        free(timestamp);
    }

    pthread_mutex_unlock(&log_mutex);
}

void write_security_event(const char *event, const char *ip, const char *filename, const char *details) {
    char logpath[MAX_PATH];
    int fd;
    char log_entry[1024];

    snprintf(logpath, MAX_PATH, "%ssecurity.log", LOG_DIR);

    pthread_mutex_lock(&log_mutex);

    fd = open(logpath, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd >= 0) {
        char *timestamp = get_timestamp();
        snprintf(log_entry, sizeof(log_entry),
                 "[%s] EVENT=%s IP=%s FILE=%s DETAILS=%s\n",
                 timestamp, event, ip ? ip : "", filename ? filename : "N/A", details ? details : "");
        write(fd, log_entry, strlen(log_entry));
        close(fd);
        free(timestamp);
    }

    pthread_mutex_unlock(&log_mutex);
}

char *compute_sha256_file(const char *path) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    unsigned char buffer[MAX_BUFFER];
    SHA256_CTX sha_ctx;
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return NULL;
    }

    SHA256_Init(&sha_ctx);
    ssize_t bytes_read;
    while ((bytes_read = read(fd, buffer, sizeof(buffer))) > 0) {
        SHA256_Update(&sha_ctx, buffer, bytes_read);
    }
    close(fd);

    SHA256_Final(hash, &sha_ctx);

    char *output = malloc(SHA256_DIGEST_LENGTH * 2 + 1);
    if (!output) return NULL;
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(output + (i * 2), "%02x", hash[i]);
    }
    output[SHA256_DIGEST_LENGTH * 2] = '\0';
    return output;
}

/*
 * Utility Functions
 */
void send_response(int socket, const char *status, const char *message) {
    char response[MAX_BUFFER];
    snprintf(response, MAX_BUFFER, "%s %s\n", status, message);
    write(socket, response, strlen(response));
}

char *get_timestamp() {
    time_t now = time(NULL);
    char *timestamp = malloc(64);
    struct tm *tm_info = localtime(&now);
    strftime(timestamp, 64, "%Y-%m-%d %H:%M:%S", tm_info);
    return timestamp;
}
