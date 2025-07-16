# Use official slim Python base
FROM python:3.10-slim

# Avoid interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install Chrome dependencies and Chrome
RUN apt-get update && apt-get install -y \
    curl unzip gnupg wget ca-certificates fonts-liberation \
    libglib2.0-0 libnss3 libgconf-2-4 libxi6 libxrender1 \
    libxcomposite1 libxcursor1 libxdamage1 libxtst6 libxrandr2 \
    xdg-utils libappindicator1 libasound2 chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Google Chrome Stable
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Set environment variables so Selenium knows where Chrome and Chromedriver are
ENV CHROME_BIN="/usr/bin/google-chrome"
ENV PATH="/usr/bin/chromedriver:${PATH}"

# Set working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask app port (Render uses dynamic port via $PORT)
EXPOSE 10000

# Start the app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
