FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema (MySQL)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Railway expone PORT
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]