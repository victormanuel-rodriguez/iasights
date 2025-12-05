import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


def _construir_dataset_diario(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye un dataset diario agregando ventas y añadiendo features temporales.
    Espera columnas:
        - transaction_date
        - product_subtotal
    """
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    # Agregación a nivel de día
    diario = (
        df.groupby("transaction_date", as_index=False)
          .agg(ventas_totales=("product_subtotal", "sum"))
          .sort_values("transaction_date")
    )

    # Features temporales
    fecha_min = diario["transaction_date"].min()
    diario["dia_semana"] = diario["transaction_date"].dt.dayofweek        # 0=Lunes
    diario["es_fin_semana"] = diario["dia_semana"].isin([5, 6]).astype(int)
    diario["semana_mes"] = (diario["transaction_date"].dt.day - 1) // 7 + 1
    diario["dia_mes"] = diario["transaction_date"].dt.day
    diario["dia_ordinal"] = (diario["transaction_date"] - fecha_min).dt.days

    return diario


def entrenar_y_predecir_ventas_diarias(
    df_filtrado: pd.DataFrame,
    dias_futuro: int = 7,
    test_size: float = 0.2,
    random_state: int = 42
) -> dict:
    """
    Entrena un modelo de regresión para ventas diarias sobre el periodo filtrado
    y genera predicciones para los próximos `dias_futuro` días.

    Params:
        df_filtrado: DataFrame con transacciones ya filtradas por periodo.
        dias_futuro: número de días futuros a predecir.
        test_size: proporción de datos para evaluación interna.
        random_state: semilla para reproducibilidad.

    Returns:
        dict con:
            - historico: DataFrame con columnas
                [transaction_date, ventas_totales, prediccion (opcional)]
            - predicciones_futuras: DataFrame con columnas
                [transaction_date, prediccion]
            - metricas_modelo: dict con r2_test, n_dias_hist
    """
    diario = _construir_dataset_diario(df_filtrado)

    n_dias = len(diario)
    if n_dias < 21:
        # Demasiado pocos datos para un modelo razonable
        return {
            "historico": diario,
            "predicciones_futuras": pd.DataFrame(),
            "metricas_modelo": {
                "r2_test": None,
                "n_dias_hist": int(n_dias),
                "mensaje": "Datos insuficientes para entrenamiento (se requieren ≥ 21 días)."
            }
        }

    # Features y target
    features = ["dia_semana", "es_fin_semana", "semana_mes", "dia_mes", "dia_ordinal"]
    target = "ventas_totales"

    X = diario[features]
    y = diario[target]

    # Split para evaluación interna
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False
    )

    modelo = RandomForestRegressor(
        n_estimators=200,
        random_state=random_state,
        n_jobs=-1
    )
    modelo.fit(X_train, y_train)

    r2_test = modelo.score(X_test, y_test)

    # Reentrenar en todo el histórico para predicción final
    modelo.fit(X, y)

    # Predicción en histórico (opcional, útil para gráficos comparativos)
    diario["prediccion"] = modelo.predict(X)

    # Predicciones futuras
    ultima_fecha = diario["transaction_date"].max()
    fecha_min = diario["transaction_date"].min()

    fechas_futuras = pd.date_range(
        start=ultima_fecha + pd.Timedelta(days=1),
        periods=dias_futuro,
        freq="D"
    )

    df_futuro = pd.DataFrame({"transaction_date": fechas_futuras})
    df_futuro["dia_semana"] = df_futuro["transaction_date"].dt.dayofweek
    df_futuro["es_fin_semana"] = df_futuro["dia_semana"].isin([5, 6]).astype(int)
    df_futuro["semana_mes"] = (df_futuro["transaction_date"].dt.day - 1) // 7 + 1
    df_futuro["dia_mes"] = df_futuro["transaction_date"].dt.day
    df_futuro["dia_ordinal"] = (df_futuro["transaction_date"] - fecha_min).dt.days

    X_future = df_futuro[features]
    df_futuro["prediccion"] = modelo.predict(X_future)

    # Ordenar columnas para claridad
    historico = diario[["transaction_date", "ventas_totales", "prediccion"]]
    predicciones_futuras = df_futuro[["transaction_date", "prediccion"]]

    metricas = {
        "r2_test": float(r2_test),
        "n_dias_hist": int(n_dias),
        "mensaje": "Modelo entrenado correctamente."
    }

    return {
        "historico": historico,
        "predicciones_futuras": predicciones_futuras,
        "metricas_modelo": metricas
    }