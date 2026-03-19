# ──────────────────────────────────────────────
# Dockerfile — Receta para construir el contenedor de Django
# ──────────────────────────────────────────────
# 📚 Un Dockerfile tiene "instrucciones" que se ejecutan en orden.
# Cada instrucción crea una "capa" que Docker cachea. Si no cambias
# una capa, Docker la reutiliza → builds más rápidos.

# ── Imagen base ──
# Usamos Python 3.12 en su variante "slim" (más liviana, sin extras innecesarios)
FROM python:3.12-slim

# ── Variables de entorno ──
# PYTHONDONTWRITEBYTECODE=1: no genera archivos .pyc (bytecode compilado)
# PYTHONUNBUFFERED=1: imprime los logs inmediatamente (no los guarda en buffer)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── Directorio de trabajo ──
# Todo lo que hagamos a partir de aquí será dentro de /app en el contenedor
WORKDIR /app

# ── Dependencias del sistema ──
# Algunas librerías Python necesitan compiladores de C para instalarse
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ── Instalar dependencias Python ──
# 📚 TRUCO: copiamos SOLO requirements/ primero, antes del código.
# ¿Por qué? Porque Docker cachea capas. Si no cambias las dependencias,
# Docker reutiliza esta capa y no reinstala todo cada vez que cambias código.
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

# ── Copiar el código de la aplicación ──
COPY . .

# ── Puerto ──
# Exponemos el puerto 8000 (informativo, el binding real se hace en docker-compose)
EXPOSE 8000

# ── Comando por defecto ──
# Gunicorn es el servidor WSGI de producción (más robusto que el servidor de Django)
# --bind 0.0.0.0:8000 = escucha en todas las interfaces, puerto 8000
# --workers 2 = 2 procesos para manejar requests en paralelo
# config.wsgi:application = punto de entrada de la app Django
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
