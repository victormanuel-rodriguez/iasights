# IAsights – Plataforma de análisis y predicción de ventas

IAsights es un MVP orientado a pequeños y medianos comercios que desean obtener,
a partir de su propio historial de ventas, un análisis claro del comportamiento
de su negocio y una predicción automática de la demanda en los próximos días.

El proyecto ofrece:
- Visualizaciones limpias del comportamiento histórico.
- KPIs esenciales para el control operativo.
- Identificación de patrones de demanda por día y franja horaria.
- Un modelo predictivo entrenado en caliente con cada archivo cargado.
- Una interfaz simple en Streamlit y un backend independiente en FastAPI.

## 1. Objetivo del proyecto
El propósito del MVP es demostrar cómo un negocio puede obtener valor inmediato
a partir de sus datos sin requerir infraestructura compleja:
- Cargar un archivo CSV con su historial de ventas.
- Recibir indicadores clave y visualizaciones claras.
- Entrenar un modelo de predicción sobre sus propios datos.
- Detectar horas pico y momentos de baja demanda.
- Consultar resultados desde una interfaz fácil de usar.

## 2. Arquitectura general
La solución se compone de dos servicios:
**1. Backend (FastAPI)**  
Procesa datos, entrena el modelo de predicción y expone los endpoints para el frontend.

**2. Frontend (Streamlit)**  
Permite cargar el archivo CSV, visualizar resultados y consumir los servicios del backend.

Ambos contenedores se comunican a través de una red Docker interna.

## 3. Flujo de uso
1. El usuario abre la aplicación Streamlit.  
2. Carga un archivo CSV con su historial de ventas.  
3. El sistema calcula KPIs, tablas y visualizaciones.  
4. Si el usuario lo solicita, se envía la data al backend para entrenar un modelo.  
5. El backend devuelve la predicción para los próximos 7 días y las métricas del modelo.  
6. También se genera un mapa de calor con patrones horarios y se identifican franjas de alta demanda.

## 4. Funcionalidades principales del MVP
### KPIs operativos
- Ventas totales.
- Número de facturas.
- Ticket promedio.
- Cantidad de productos únicos.
- Clientes recurrentes.

### Análisis temporal
- Ventas diarias (gráfico por fecha).
- Filtros por último mes, últimos 90 días o por mes específico del CSV.

### Predicción de ventas
- Modelo Lineal entrenado en caliente.
- Devuelve predicción de 7 días.
- Incluye R² y número de observaciones usadas.

### Patrones de demanda por día y hora
- Agrupación por día de la semana y franja horaria.
- KMeans para clasificar demanda en Bajo, Normal y Pico.
- Mapa de calor con escala ajustada.
- Tablas con las mejores y peores franjas.

## 5. Estructura del repositorio
```
iasights/
├── docker/
│   ├── FastAPI.Dockerfile
│   └── streamlit.Dockerfile
├── frontend/
│   ├── streamlit_app.py
│   └── styles.css
├── src/
│   ├── api/
│   │   └── main.py
│   ├── analytics/
│   │   ├── basico.py
│   │   ├── clientes.py
│   │   ├── filtros.py
│   │   ├── patrones.py
│   │   └── periodos.py
│   ├── ingestion/
│   │   └── validator.py
│   ├── ml/
│   │   ├── modelo_ventas.py
│   │   └── patrones_horarios.py
│   └── utils/
│       └── etiquetas.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 6. Instalación y ejecución con Docker
### Paso 1 — Construir las imágenes
```bash
docker-compose build
```

### Paso 2 — Levantar los servicios
```bash
docker-compose up
```

### Paso 3 — Acceder a la aplicación
- Streamlit: http://localhost:8501  
- FastAPI Docs: http://localhost:8000/docs  

## 7. Requisitos del CSV
El archivo debe contener:
- invoice_id
- transaction_date
- transaction_time
- customer_id
- customer_name
- product_id
- product_name
- product_category
- product_quantity
- product_unit_price
- product_subtotal

## 8. Modelo de predicción
Entrena en caliente, basado en regresión lineal agregada por día.

## 9. Patrones horarios
Incluye:
- Agrupación por día.
- Buckets horarios de 3 horas.
- KMeans para clasificar niveles de demanda.
- Heatmap y tablas explicativas.

## 10. Limitaciones actuales
- No persiste modelos.
- No incluye autenticación.
- Modelo predictivo simple.

## 11. Próximos pasos sugeridos
- Integración con Ollama para análisis explicativos.
- Conectores a sistemas externos.
- Dashboard estilo BI.

## 12. Licencia
Proyecto desarrollado como MVP académico en el marco del curso Product Development,
Postgrado en Análisis y Predicción de Datos de la Universidad Galileo, Guatemala,
Diciembre de 2025