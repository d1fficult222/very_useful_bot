FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei

RUN apt-get update && apt-get install -y curl fonts-noto-cjk fonts-dejavu-core

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
