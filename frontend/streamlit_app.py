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
from src.analytics.basico import ventas_diarias

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
st.set_page_config(page_title="iasights MVP", layout="wide")

st.title("iasights – MVP Inicial")

uploaded_file = st.file_uploader("Sube tu archivo CSV de ventas", type=["csv"])

if uploaded_file:
    df = cargar_csv(uploaded_file)
    
    st.subheader("Vista previa")
    st.dataframe(df.head())

    st.subheader("Ventas diarias")
    ventas = ventas_diarias(df)

    fig = px.bar(ventas, x="transaction_date", y="total_ventas", title="Ventas por día")
    st.plotly_chart(fig, use_container_width=True)