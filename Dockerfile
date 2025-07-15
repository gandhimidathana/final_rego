FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget curl unzip chromium chromium-driver \
    fonts-liberation libnss3 libxss1 libappindicator1 libatk-bridge2.0-0 libgtk-3-0 \
    && apt-get clean

ENV DISPLAY=:99


WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 10000

CMD ["python", "app.py"]
