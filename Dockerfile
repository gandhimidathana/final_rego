# Use official slim Python base
FROM python:3.10-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and system Chrome & Chromedriver
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates fonts-liberation \
    libglib2.0-0 libnss3 libgconf-2-4 libxi6 libxrender1 \
    libxcomposite1 libxcursor1 libxdamage1 libxtst6 libxrandr2 \
    xdg-utils libappindicator1 libasound2 chromium-driver \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Chrome Stable from Google
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV CHROME_BIN="/usr/bin/google-chrome"
ENV PATH="/usr/bin/chromedriver:${PATH}"

# Set working directory
WORKDIR /app

# Copy all source files
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port (match PORT env var in Railway)
EXPOSE 10000

# Run the Flask app via gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
