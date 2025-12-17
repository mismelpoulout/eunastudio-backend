FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema (necesarias para MySQL)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Railway usa la variable PORT
CMD gunicorn app:app --bind 0.0.0.0:$PORT