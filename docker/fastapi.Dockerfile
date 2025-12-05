# Imagen base ligera y estable
FROM python:3.10-slim

# Evitar buffering y permitir logs en tiempo real
ENV PYTHONUNBUFFERED=1

# Crear directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements primero para aprovechar layer caching
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente del backend
COPY src ./src

# (Opcional) Exponer puerto usado internamente por FastAPI
EXPOSE 8000

# Comando para iniciar el servidor FastAPI
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]