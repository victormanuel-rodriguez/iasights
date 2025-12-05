import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


_DIAS = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


def _bucket_hora(hora: int, ancho: int = 3) -> str:
    """
    Agrupa la hora en franjas de `ancho` horas.
    Ej: 8 -> "06:00-09:00" si ancho=3.
    """
    if pd.isna(hora):
        return "Sin hora"
    hora = int(hora)
    inicio = (hora // ancho) * ancho
    fin = inicio + ancho
    return f"{inicio:02d}:00-{fin:02d}:00"


def detectar_patrones_horarios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta patrones de demanda por día y franja horaria usando KMeans.

    Devuelve un DataFrame con columnas:
        - Día
        - Franja horaria
        - Ventas totales
        - No. de transacciones
        - Nivel de demanda ("Pico", "Normal", "Bajo")
    """
    if df.empty:
        return pd.DataFrame(
            columns=[
                "Día",
                "Franja horaria",
                "Ventas totales",
                "No. de transacciones",
                "Nivel de demanda",
            ]
        )

    df_work = df.copy()

    # ================================================================
    # Asegurar tipos correctos de FECHA y HORA (evita warnings)
    # ================================================================

    # Fecha: permitir timestamps como "2025-02-27 00:00:00" o "2025-02-27"
    df_work["transaction_date"] = pd.to_datetime(
        df_work["transaction_date"], errors="coerce"
    )

    # Hora: CSV usa "HH:MM:SS", por eso definimos formato explícito
    df_work["transaction_time"] = pd.to_datetime(
        df_work["transaction_time"].astype(str),
        format="%H:%M:%S",
        errors="coerce"
    ).dt.time

    # Extraer hora numérica (0–23)
    df_work["hora"] = df_work["transaction_time"].apply(
        lambda t: t.hour if pd.notnull(t) else None
    )

    # Día de la semana (0=lun, 6=dom)
    df_work["dia_idx"] = df_work["transaction_date"].dt.dayofweek
    df_work["Día"] = df_work["dia_idx"].map(_DIAS)

    # Franja horaria definida por tus buckets
    df_work["Franja horaria"] = df_work["hora"].apply(_bucket_hora)

    # ================================================================
    # Agregación por día y franja
    # ================================================================
    agg = (
        df_work.groupby(["dia_idx", "Día", "Franja horaria"], dropna=False)
        .agg(
            **{
                "Ventas totales": ("product_subtotal", "sum"),
                "No. de transacciones": ("invoice_id", "nunique"),
            }
        )
        .reset_index()
    )

    if agg.empty:
        return pd.DataFrame(
            columns=[
                "Día",
                "Franja horaria",
                "Ventas totales",
                "No. de transacciones",
                "Nivel de demanda",
            ]
        )

    # Asegurar numéricos
    agg["Ventas totales"] = pd.to_numeric(agg["Ventas totales"], errors="coerce").fillna(0)
    agg["No. de transacciones"] = pd.to_numeric(agg["No. de transacciones"], errors="coerce").fillna(0)

    # ================================================================
    # Clustering (KMeans) o fallback por cuantiles
    # ================================================================
    n_grupos = len(agg)
    if n_grupos >= 3:
        features = agg[["Ventas totales", "No. de transacciones"]].values
        scaler = StandardScaler()
        X = scaler.fit_transform(features)

        kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
        agg["cluster"] = kmeans.fit_predict(X)

        orden = (
            agg.groupby("cluster")["Ventas totales"]
            .mean()
            .sort_values()
            .index.tolist()
        )

        mapping = {
            orden[0]: "Bajo",
            orden[1]: "Normal",
            orden[2]: "Pico",
        }
        agg["Nivel de demanda"] = agg["cluster"].map(mapping)
        agg = agg.drop(columns=["cluster"])

    else:
        v = agg["Ventas totales"]
        q1 = v.quantile(1 / 3)
        q2 = v.quantile(2 / 3)

        def _nivel(x):
            if x <= q1:
                return "Bajo"
            elif x <= q2:
                return "Normal"
            else:
                return "Pico"

        agg["Nivel de demanda"] = agg["Ventas totales"].apply(_nivel)

    # ================================================================
    # Orden correcto: lunes → domingo
    # ================================================================
    agg = agg.sort_values(["dia_idx", "Franja horaria"]).reset_index(drop=True)

    # Limpiar columnas auxiliares
    agg = agg.drop(columns=["dia_idx", "hora"], errors="ignore")

    return agg[
        [
            "Día",
            "Franja horaria",
            "Ventas totales",
            "No. de transacciones",
            "Nivel de demanda",
        ]
    ]