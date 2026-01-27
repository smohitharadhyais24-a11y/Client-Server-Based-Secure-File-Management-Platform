#!/bin/bash

# Proper test to see if fcntl locks work

cat > /tmp/test_lock.c << 'EOF'
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

int main(int argc, char *argv[]) {
    int fd = open("/tmp/testfile.txt", O_WRONLY | O_CREAT, 0644);
    struct flock lock;
    
    lock.l_type = F_WRLCK;
    lock.l_whence = SEEK_SET;
    lock.l_start = 0;
    lock.l_len = 0;
    lock.l_pid = getpid();
    
    printf("[PID %d] Trying to lock /tmp/testfile.txt\n", getpid());
    
    if (fcntl(fd, F_SETLK, &lock) == -1) {
        if (errno == EACCES || errno == EAGAIN) {
            printf("[PID %d] LOCK REJECTED - File already locked!\n", getpid());
            return 1;
        }
        perror("fcntl error");
        return 1;
    }
    
    printf("[PID %d] LOCK ACQUIRED - File locked successfully\n", getpid());
    printf("[PID %d] Sleeping for 10 seconds... (try running this again in another terminal)\n", getpid());
    sleep(10);
    printf("[PID %d] Releasing lock\n", getpid());
    
    lock.l_type = F_UNLCK;
    fcntl(fd, F_SETLK, &lock);
    close(fd);
    
    return 0;
}
EOF

gcc -o /tmp/test_lock /tmp/test_lock.c
rm -f /tmp/testfile.txt

echo "=== Testing fcntl locks ===" 
echo "Run: /tmp/test_lock"
echo "Then quickly run it again in another terminal to see if lock rejection works"
