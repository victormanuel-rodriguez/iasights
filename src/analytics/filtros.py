import pandas as pd
from datetime import timedelta
from .periodos import obtener_mes_por_defecto

def filtrar_por_periodo(df: pd.DataFrame, periodo: str):
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    # Caso 1: último mes completo
    if periodo == "ultimo_mes":
        mes = obtener_mes_por_defecto(df)
        if mes is None:
            raise ValueError("No hay meses con suficientes datos para análisis.")
        return df[df["transaction_date"].dt.to_period("M") == mes]

    # Caso 2: últimos 90 días
    if periodo == "ultimos_90_dias":
        max_fecha = df["transaction_date"].max()
        min_permitida = max_fecha - timedelta(days=90)
        return df[df["transaction_date"] >= min_permitida]

    # Caso 3: mes explícito (ej: "2025-11")
    return df[df["transaction_date"].dt.to_period("M") == periodo]