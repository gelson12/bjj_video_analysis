# Dockerfile

# Use a Python 3.10 slim image to reduce size and stay updated
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Update sources.list to use a reliable Debian mirror
RUN echo "deb http://ftp.us.debian.org/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb http://ftp.us.debian.org/debian/ bookworm-updates main" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list

# Install required system packages and dependencies for Selenium and Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

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
