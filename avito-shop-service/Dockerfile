FROM python:3.10

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

COPY ./avito-shop-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY avito-shop-service/ .

RUN dos2unix start.sh && chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]