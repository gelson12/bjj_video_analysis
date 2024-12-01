#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Run the log initialization script
./checkif_applog_exists.sh

# Check if the previous command was successful
if [ $? -ne 0 ]; then
    echo "Failed to initialize app.log. Exiting."
    exit 1
fi

# Start the main application
exec "$@"
