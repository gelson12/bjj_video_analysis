#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

LOG_FILE="/app/app.log"

if [ -d "$LOG_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - app.log is a directory. Removing it..."
    rm -r "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Creating an empty app.log file..."
    touch "$LOG_FILE"
elif [ ! -f "$LOG_FILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - app.log does not exist. Creating it..."
    touch "$LOG_FILE"
    chmod 664 "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - app.log is already a file."
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Ensuring file has appropriate permissions to be written by any application..."
    chmod 664 "$LOG_FILE"
fi
