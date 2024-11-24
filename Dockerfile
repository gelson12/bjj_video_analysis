# Dockerfile

# Use a Python 3.10 slim image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Update sources.list to use an alternative mirror
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

# Continue with other Dockerfile steps...


# Create a temporary directory and set TMPDIR environment variable
RUN mkdir -p /app/tmp
ENV TMPDIR=/app/tmp

# Copy requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run on container start
CMD ["python", "app.py"]
