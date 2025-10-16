# Usar Python 3.12 (evita el error de audioop en Python 3.13)
FROM python:3.12-slim

# Información del mantenedor
LABEL maintainer="tu-email@ejemplo.com"
LABEL description="Elite Verify - Sistema de Verificación para Discord"

# Variables de entorno de Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo requirements.txt primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos del proyecto
COPY . .

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Cambiar al usuario no-root
USER botuser

# Exponer el puerto (Railway usa la variable PORT)
EXPOSE 5000

# Comando de inicio
CMD ["python", "bot.py"]
