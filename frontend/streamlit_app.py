import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import requests

# -------------------------------------------------------------------
# CONFIGURACIÓN INICIAL
# -------------------------------------------------------------------

# Ruta absoluta a la carpeta raíz del proyecto (la que contiene src/)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ingestion.validator import cargar_csv
from src.analytics.basico import ventas_diarias, resumen_general
from src.analytics.patrones import ventas_por_categoria, top_productos_por_ventas
from src.analytics.clientes import clientes_recurrentes
from src.analytics.periodos import obtener_meses_disponibles
from src.analytics.filtros import filtrar_por_periodo

st.set_page_config(page_title="IAsights MVP", layout="wide")
st.title("IAsights MVP")

API_URL = "http://iasights-api:8000"  # backend dentro de Docker Compose

# -------------------------------------------------------------------
# CARGA DE CSV
# -------------------------------------------------------------------

uploaded_file = st.file_uploader("Sube tu archivo CSV de ventas", type=["csv"])

if uploaded_file:
    df = cargar_csv(uploaded_file)

    # ---------------------------------------------------------------
    # RESUMEN GENERAL
    # ---------------------------------------------------------------
    st.subheader("Resumen general")
    resumen = resumen_general(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas totales", f"${resumen['total_ventas']:.2f}")
    col2.metric("Facturas únicas", resumen["num_facturas_unicas"])
    col3.metric("Productos distintos", resumen["num_productos"])

    # ---------------------------------------------------------------
    # VENTAS DIARIAS
    # ---------------------------------------------------------------
    st.subheader("Ventas diarias (todas las fechas del CSV)")
    ventas = ventas_diarias(df)
    fig = px.bar(ventas, x="transaction_date", y="total_ventas", title="Ventas por día")
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------------
    # TOP PRODUCTOS
    # ---------------------------------------------------------------
    st.subheader("Top 5 productos por ventas")
    top_prod = top_productos_por_ventas(df, top_n=5)
    st.dataframe(top_prod)

    # ---------------------------------------------------------------
    # CLIENTES RECURRENTES
    # ---------------------------------------------------------------
    st.subheader("Clientes recurrentes (≥ 2 facturas)")
    clientes_rec = clientes_recurrentes(df, min_visitas=2)
    st.dataframe(clientes_rec.head(10))

    # ---------------------------------------------------------------
    # SELECCIÓN DE PERIODO
    # ---------------------------------------------------------------
    meses = obtener_meses_disponibles(df)

    st.subheader("Seleccione período para análisis avanzado (ML)")
    periodo = st.selectbox(
        "Período",
        ["ultimo_mes", "ultimos_90_dias"] + meses
    )

    df_filtrado = filtrar_por_periodo(df, periodo)

    st.info(f"Filtrando datos para el período seleccionado: {periodo}")

    # Mostrar ventas del período filtrado
    ventas_periodo = ventas_diarias(df_filtrado)
    fig2 = px.line(
        ventas_periodo,
        x="transaction_date",
        y="total_ventas",
        title=f"Ventas diarias – período: {periodo}"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------------------------------------------
    # PREDICCIÓN DE VENTAS (IA – MODELO 1)
    # -------------------------------------------------------------------
    st.subheader("Predicción de ventas (IA tradicional)")

    if st.button("Generar predicción para los próximos 7 días"):
        with st.spinner("Entrenando modelo y generando predicciones..."):

            # Enviar archivo y parámetros al backend
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
                }
            params = {"periodo": periodo, "dias_futuro": 7}

            try:
                response = requests.post(
                    f"{API_URL}/forecast-sales",
                    files=files,
                    params=params,
                    timeout=60
                )
            except Exception as e:
                st.error(f"Error al conectar con backend FastAPI: {e}")
                st.stop()

            if response.status_code != 200:
                st.error(f"Error del backend ({response.status_code}): {response.text}")
                st.stop()

            data = response.json()

            historico = pd.DataFrame(data["historico"])
            pred_futuro = pd.DataFrame(data["predicciones_futuras"])
            metricas = data["metricas_modelo"]

            # Mostrar métricas
            st.write("### Métricas del modelo")
            st.write(metricas)

            # Gráfico combinado (histórico + predicciones)
            if not pred_futuro.empty:
                historico["tipo"] = "Histórico"
                pred_futuro["tipo"] = "Predicción"

                comb = pd.concat([historico, pred_futuro], ignore_index=True)
                fig3 = px.line(
                    comb,
                    x="transaction_date",
                    y="prediccion",
                    color="tipo",
                    title="Predicción de ventas para próximos 7 días",
                )
                st.plotly_chart(fig3, use_container_width=True)

            else:
                st.warning("No fue posible generar predicciones (datos insuficientes).")