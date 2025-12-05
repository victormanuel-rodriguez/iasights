import pandas as pd

def obtener_meses_disponibles(df: pd.DataFrame):
    # Asegurarse de que transaction_date es datetime
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    meses = (
        df["transaction_date"]
        .dt.to_period("M")
        .astype(str)
        .unique()
    )
    meses_ordenados = sorted(meses)
    return meses_ordenados

def mes_tiene_suficientes_datos(df: pd.DataFrame, mes: str, minimo_dias=15):
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    periodo = df[df["transaction_date"].dt.to_period("M") == mes]
    dias = periodo["transaction_date"].dt.date.nunique()
    return dias >= minimo_dias

def obtener_mes_por_defecto(df: pd.DataFrame, minimo_dias=15):
    meses = obtener_meses_disponibles(df)
    # Revisar desde el más reciente
    for mes in reversed(meses):
        if mes_tiene_suficientes_datos(df, mes, minimo_dias):
            return mes
    return None