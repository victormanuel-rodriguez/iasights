import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px

# Ruta absoluta a la carpeta raíz del proyecto (la que contiene src/)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ingestion.validator import cargar_csv
from src.analytics.basico import ventas_diarias, resumen_general
from src.analytics.patrones import ventas_por_categoria, top_productos_por_ventas
from src.analytics.clientes import clientes_recurrentes

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
st.set_page_config(page_title="iasights MVP", layout="wide")

st.title("iasights – MVP Inicial")

uploaded_file = st.file_uploader("Sube tu archivo CSV de ventas", type=["csv"])

if uploaded_file:
    df = cargar_csv(uploaded_file)

    st.subheader("Resumen general")
    resumen = resumen_general(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas totales", f"${resumen['total_ventas']:.2f}")
    col2.metric("Facturas únicas", resumen["num_facturas_unicas"])
    col3.metric("Productos distintos", resumen["num_productos"])

    st.subheader("Ventas diarias")
    ventas = ventas_diarias(df)
    fig = px.bar(ventas, x="transaction_date", y="total_ventas", title="Ventas por día")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 5 productos por ventas")
    top_prod = top_productos_por_ventas(df, top_n=5)
    st.dataframe(top_prod)

    st.subheader("Clientes recurrentes (≥ 2 facturas)")
    clientes_rec = clientes_recurrentes(df, min_visitas=2)
    st.dataframe(clientes_rec.head(10))