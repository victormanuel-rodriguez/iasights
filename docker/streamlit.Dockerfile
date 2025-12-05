# Imagen base ligera
FROM python:3.10-slim

# Evitar buffering en logs
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente (backend analytics + frontend)
COPY src ./src
COPY frontend ./frontend

# Exponer el puerto interno de Streamlit
EXPOSE 8501

# Comando para lanzar Streamlit
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--browser.gatherUsageStats=false"]