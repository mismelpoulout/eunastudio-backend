FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema necesarias para mysql-connector-python
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Puerto fijo (Railway lo redirige)
EXPOSE 8080

# 🚀 USAR WSGI CORRECTAMENTE
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8080"]