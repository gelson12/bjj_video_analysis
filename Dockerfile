# Dockerfile

# Use a Python 3.10 slim image to reduce size and stay updated
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Update sources.list to use a reliable Debian mirror
RUN echo "deb http://ftp.us.debian.org/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb http://ftp.us.debian.org/debian/ bookworm-updates main" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list

# Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a temporary directory and set TMPDIR environment variable
RUN mkdir -p /app/tmp
ENV TMPDIR=/app/tmp

# Copy requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the shell scripts into the container
COPY checkif_applog_exists.sh /app/checkif_applog_exists.sh
COPY entrypoint.sh /app/entrypoint.sh

# Make the scripts executable
RUN chmod +x /app/checkif_applog_exists.sh /app/entrypoint.sh

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Set the entrypoint to the entrypoint.sh script
ENTRYPOINT ["/app/entrypoint.sh"]

# Define the default command to run the Flask app
CMD ["python", "app.py"]
