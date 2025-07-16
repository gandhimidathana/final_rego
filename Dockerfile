# Dockerfile for Flask + Selenium (no Python code changes)

FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates fonts-liberation \
    libglib2.0-0 libnss3 libgconf-2-4 libxi6 libxrender1 \
    libxcomposite1 libxcursor1 libxdamage1 libxtst6 libxrandr2 \
    xdg-utils libappindicator1 libasound2 chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Set Chrome path (so your existing Python code works without changes)
ENV PATH="/usr/bin/chromedriver:${PATH}"
ENV CHROME_BIN="/usr/bin/google-chrome"

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 10000

# Start your app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
