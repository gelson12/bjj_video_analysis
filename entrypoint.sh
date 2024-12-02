# entrypoint.sh

#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Step 1: Extract cookies using Selenium
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting cookie extraction..."
python extract_cookies.py

# Step 2: Convert to cookies.txt
echo "$(date '+%Y-%m-%d %H:%M:%S') - Converting cookies to Netscape format..."
python convert_cookies.py

# Step 3: Secure cookies.txt
chmod 600 cookies.txt
echo "$(date '+%Y-%m-%d %H:%M:%S') - Secured cookies.txt permissions."

# Optional: Remove cookies.json if no longer needed
rm -f cookies.json

echo "$(date '+%Y-%m-%d %H:%M:%S') - Automated cookie extraction and conversion complete."

# Run the log initialization script
echo "$(date '+%Y-%m-%d %H:%M:%S') - Initializing application logs..."
./checkif_applog_exists.sh

# Check if the previous command was successful
if [ $? -ne 0 ]; then
    echo "Failed to initialize app.log. Exiting."
    exit 1
fi

# Start the main application
echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting Flask application..."
exec "$@"