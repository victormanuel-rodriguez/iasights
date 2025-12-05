import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import requests

# -------------------------------------------------------------------
# CONFIGURACIÓN INICIAL
# -------------------------------------------------------------------

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ingestion.validator import cargar_csv
from src.analytics.basico import (
    ventas_diarias,
    resumen_general,
    calcular_kpis_generales,
    top_productos,
    top_clientes,
)
from src.analytics.periodos import obtener_meses_disponibles
from src.analytics.filtros import filtrar_por_periodo
from src.utils.etiquetas import (
    aplicar_etiquetas,
    formatear_monedas
)
from src.ml.patrones_horarios import detectar_patrones_horarios

# -------------------------------------------------------------------
# Cargar estilos CSS
# -------------------------------------------------------------------
styles_path = os.path.join(os.path.dirname(__file__), "styles.css")

if os.path.exists(styles_path):
    with open(styles_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="IAsights", layout="wide")

# Encabezado
st.markdown("<h1>IAsights – Inteligencia para tu negocio</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:18px; color:#cccccc'>Análisis de ventas: KPIs esenciales, insights y predicciones</p>",
    unsafe_allow_html=True,
)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

API_URL = "http://iasights-api:8000"


# -------------------------------------------------------------------
# CARGA DE CSV
# -------------------------------------------------------------------
st.header("1. Cargar archivo CSV")
uploaded_file = st.file_uploader("Selecciona tu archivo CSV de ventas", type=["csv"])

if not uploaded_file:
    st.stop()

df = cargar_csv(uploaded_file)

# Muestra vista previa con etiquetas
st.subheader("Vista previa del archivo")
st.dataframe(aplicar_etiquetas(formatear_monedas(df.head())))

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# KPIs GLOBALES
# -------------------------------------------------------------------
st.header("2. KPIs principales del negocio")

resumen = resumen_general(df)
kpis = calcular_kpis_generales(df)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='kpi-box'>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value'>${resumen['total_ventas']:,.2f}</div>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-label'>Ventas totales</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='kpi-box'>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value'>{resumen['num_facturas_unicas']:,}</div>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-label'>Facturas únicas</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='kpi-box'>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value'>{kpis['n_productos']:,}</div>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-label'>Productos distintos</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# TOP PRODUCTOS Y CLIENTES
# -------------------------------------------------------------------
st.subheader("Top productos por ingreso generado")
df_top_prod = top_productos(df, n=5)
st.dataframe(aplicar_etiquetas(formatear_monedas(df_top_prod)))

st.subheader("Top clientes recurrentes")
df_top_cli = top_clientes(df, n=10)

if df_top_cli.empty:
    st.info("No hay clientes registrados en el CSV (customer_id vacío).")
else:
    st.dataframe(aplicar_etiquetas(formatear_monedas(df_top_cli)))

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# VENTAS DIARIAS
# -------------------------------------------------------------------
st.header("3. Comportamiento histórico de ventas")

ventas = ventas_diarias(df)
ventas_form = aplicar_etiquetas(formatear_monedas(ventas))

fig = px.bar(
    ventas_form,
    x="Fecha",
    y="Ventas Totales",
    title="Ventas diarias (todo el período del archivo)",
)
st.plotly_chart(fig, width="stretch")

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


# -------------------------------------------------------------------
# PERÍODO PARA ANÁLISIS AVANZADO
# -------------------------------------------------------------------
st.header("4. Selección de período para análisis avanzado")

meses = obtener_meses_disponibles(df)

# Mapeo: etiqueta amigable → valor real
opciones_periodo = {
    "Último mes": "ultimo_mes",
    "Últimos 90 días": "ultimos_90_dias"
}

# Agregar meses detectados en el CSV
for m in meses:
    opciones_periodo[f"Mes: {m}"] = m

etiquetas = list(opciones_periodo.keys())

seleccion = st.selectbox("Período a analizar", etiquetas)

periodo = opciones_periodo[seleccion]   # ← valor real que se usa en el backend

df_filtrado = filtrar_por_periodo(df, periodo)

ventas_periodo = ventas_diarias(df_filtrado)
ventas_periodo_form = aplicar_etiquetas(formatear_monedas(ventas_periodo))

fig2 = px.line(
    ventas_periodo_form,
    x="Fecha",
    y="Ventas Totales",
    title=f"Gráfico de ventas para el período seleccionado:",
)
st.plotly_chart(fig2, width="stretch")

# -------------------------------------------------------------------
# HEATMAP DE DEMANDA POR DIA DE LA SEMANA Y HORA
# -------------------------------------------------------------------

st.header("5. Patrones de demanda por día y horario")

patrones_df = detectar_patrones_horarios(df_filtrado)

if patrones_df.empty:
    st.info(
        "No hay suficientes datos en el período seleccionado para analizar "
        "patrones horarios de demanda."
    )
else:
    # Copias para visualización/tablas y para heatmap
    patrones_vis = patrones_df.copy()
    patrones_vis["Ventas totales"] = patrones_vis["Ventas totales"].apply(
        lambda x: f"${x:,.2f}"
    )

    st.subheader("Mapa de calor de demanda por día y franja horaria")

    # Heatmap usando ventas totales numéricas
    heat_df = (
        patrones_df.pivot_table(
            index="Día",
            columns="Franja horaria",
            values="Ventas totales",
            aggfunc="sum",
        )
        .fillna(0)
    )

    # ORDENAR LOS DÍAS DE LUNES A DOMINGO
    orden_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Reindexar filas usando el orden correcto
    heat_df = heat_df.reindex(orden_dias)

    # Crear heatmap
    fig_hm = px.imshow(
        heat_df,
        color_continuous_scale="Turbo",
        labels={
            "x": "Franja horaria",
            "y": "Día",
            "color": "Ventas totales",
        },
        aspect="auto",
    )
    st.plotly_chart(fig_hm, width="stretch")

    # Top franjas de mayor demanda
    st.subheader("Franjas con mayor demanda (Pico)")
    top_pico = (
        patrones_df[patrones_df["Nivel de demanda"] == "Pico"]
        .sort_values("Ventas totales", ascending=False)
        .head(5)
        .copy()
    )
    top_pico["Ventas totales"] = top_pico["Ventas totales"].apply(
        lambda x: f"${x:,.2f}"
    )
    st.dataframe(top_pico)

    # Franjas con menor demanda
    st.subheader("Franjas con menor demanda (Bajo)")
    top_bajo = (
        patrones_df[patrones_df["Nivel de demanda"] == "Bajo"]
        .sort_values("Ventas totales", ascending=True)
        .head(5)
        .copy()
    )
    top_bajo["Ventas totales"] = top_bajo["Ventas totales"].apply(
        lambda x: f"${x:,.2f}"
    )
    st.dataframe(top_bajo)

# -------------------------------------------------------------------
# ML – PREDICCIÓN DE VENTAS
# -------------------------------------------------------------------
st.header("6. Predicción de ventas")

if st.button("Generar predicción para los próximos 7 días"):
    with st.spinner("Entrenando modelo y generando predicciones..."):

        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
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

        # --------------------
        # MÉTRICAS  DEL MODELO
        # --------------------
        st.subheader("Desempeño del modelo")

        r2 = metricas.get("r2_test", None)
        dias = metricas.get("n_dias_hist", None)

        st.success(
            f"""
            **Resultados del modelo:**

            • **Calidad del modelo:** {r2 * 100:.1f}%  
            • **Días analizados:** {dias}  
            • **Estado:** Modelo entrenado correctamente.
            """
        )

        # ---------------------------
        # GRÁFICA DE PREDICCIÓN
        # ---------------------------
        if not pred_futuro.empty:
            historico["tipo"] = "Histórico"
            pred_futuro["tipo"] = "Predicción"

            comb = pd.concat([historico, pred_futuro], ignore_index=True)
            comb = aplicar_etiquetas(formatear_monedas(comb))

            fig3 = px.line(
                comb,
                x="Fecha",
                y="Predicción",
                color="tipo",
                title="Predicción de ventas para próximos 7 días"
            )
            st.plotly_chart(fig3, width="stretch")

        else:
            st.warning("No fue posible generar predicciones (datos insuficientes).")
