FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip chromium chromium-driver \
    fonts-liberation libnss3 libxss1 libappindicator1 libatk-bridge2.0-0 libgtk-3-0 \
    && apt-get clean

# Set display to fake one (optional for headless)
ENV DISPLAY=:99

# Set working dir and copy project
WORKDIR /app
COPY . /app

# Install Python requirements
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 10000

# Start using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
