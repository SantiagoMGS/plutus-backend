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

# ── Hacer ejecutable el entrypoint ──
RUN chmod +x entrypoint.sh

# ── Puerto ──
# Exponemos el puerto 8000 (informativo, el binding real se hace en docker-compose)
EXPOSE 8000

# ── Comando por defecto ──
# El entrypoint ejecuta migraciones y luego arranca gunicorn
CMD ["./entrypoint.sh"]
