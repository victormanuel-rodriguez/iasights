def agregar_features_temporales(df):
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    df["dia_semana"] = df["transaction_date"].dt.dayofweek  # 0=Lunes
    df["es_fin_semana"] = df["dia_semana"].isin([5, 6]).astype(int)
    df["semana_mes"] = df["transaction_date"].dt.day // 7 + 1
    df["dia_mes"] = df["transaction_date"].dt.day

    return df

def agregar_ventas_diarias(df):
    df["subtotal"] = df["cantidad"] * df["product_unit_price"]

    diario = df.groupby("transaction_date").agg(
        ventas_totales=("subtotal", "sum"),
        num_transacciones=("invoice_id", "nunique"),
        num_items=("cantidad", "sum"),
        porc_combos=(lambda x: (df[df["product_category"].str.contains("combo", case=False)].shape[0]) / df.shape[0])
    )

    diario = diario.reset_index()
    diario = agregar_features_temporales(diario)
    return diario