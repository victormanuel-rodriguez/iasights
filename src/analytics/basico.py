import pandas as pd

def resumen_general(df: pd.DataFrame) -> dict:
    """
    Calcula métricas globales del dataset de ventas.

    Returns:
        dict con:
            total_ventas: float
            num_transacciones: int
            num_facturas_unicas: int
            num_clientes_conocidos: int
            num_productos: int
            fecha_min: str (YYYY-MM-DD)
            fecha_max: str (YYYY-MM-DD)
    """
    total_ventas = df["product_subtotal"].sum()
    num_transacciones = len(df)
    num_facturas_unicas = df["invoice_id"].nunique()
    num_clientes_conocidos = df["customer_id"].notna().sum()
    num_productos = df["product_id"].nunique()
    fecha_min = df["transaction_date"].min().date().isoformat()
    fecha_max = df["transaction_date"].max().date().isoformat()

    return {
        "total_ventas": float(total_ventas),
        "num_transacciones": int(num_transacciones),
        "num_facturas_unicas": int(num_facturas_unicas),
        "num_clientes_conocidos": int(num_clientes_conocidos),
        "num_productos": int(num_productos),
        "fecha_min": fecha_min,
        "fecha_max": fecha_max,
    }


def ventas_diarias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve un DataFrame con ventas totales por día.

    Columns:
        transaction_date (datetime64[ns])
        total_ventas (float)
    """
    df_grouped = (
        df.groupby("transaction_date", as_index=False)
          .agg(total_ventas=("product_subtotal", "sum"))
          .sort_values("transaction_date")
    )
    return df_grouped

def calcular_kpis_generales(df: pd.DataFrame) -> dict:
    """
    Calcula KPIs globales a partir del detalle de ventas.
    Asume columnas:
    - invoice_id
    - customer_id
    - product_id
    - product_subtotal
    """
    df_limpio = df.copy()

    # Asegurar tipo numérico
    df_limpio["product_subtotal"] = pd.to_numeric(
        df_limpio["product_subtotal"], errors="coerce"
    ).fillna(0)

    monto_total = df_limpio["product_subtotal"].sum()

    n_facturas = df_limpio["invoice_id"].nunique()

    n_clientes_registrados = df_limpio["customer_id"].notna().sum()
    n_clientes_unicos = df_limpio["customer_id"].nunique() - (
        1 if df_limpio["customer_id"].isna().any() else 0
    )

    n_productos = df_limpio["product_id"].nunique()

    ticket_promedio = monto_total / n_facturas if n_facturas > 0 else 0.0

    return {
        "monto_total": float(monto_total),
        "n_facturas": int(n_facturas),
        "n_clientes_registrados": int(n_clientes_registrados),
        "n_clientes_unicos": int(n_clientes_unicos),
        "n_productos": int(n_productos),
        "ticket_promedio": float(ticket_promedio),
    }


def top_productos(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Top N productos por ingreso generado.
    Asume columnas:
    - product_id
    - product_name
    - product_category
    - product_quantity
    - product_subtotal
    """
    df_limpio = df.copy()
    df_limpio["product_subtotal"] = pd.to_numeric(
        df_limpio["product_subtotal"], errors="coerce"
    ).fillna(0)
    df_limpio["product_quantity"] = pd.to_numeric(
        df_limpio["product_quantity"], errors="coerce"
    ).fillna(0)

    agrupado = (
        df_limpio.groupby(
            ["product_id", "product_name", "product_category"], dropna=False
        )
        .agg(
            cantidad_total=("product_quantity", "sum"),
            ingreso_total=("product_subtotal", "sum"),
            n_transacciones=("invoice_id", "nunique"),
        )
        .reset_index()
    )

    return (
        agrupado.sort_values("ingreso_total", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def top_clientes(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Top N clientes por recurrencia y monto.
    Asume columnas:
    - customer_id
    - customer_name
    - invoice_id
    - product_subtotal
    """
    df_limpio = df.copy()
    df_limpio["product_subtotal"] = pd.to_numeric(
        df_limpio["product_subtotal"], errors="coerce"
    ).fillna(0)

    # Filtramos solo clientes con algún identificador
    df_limpio = df_limpio[df_limpio["customer_id"].notna()]

    if df_limpio.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "customer_name",
                "n_facturas",
                "monto_total",
            ]
        )

    agrupado = (
        df_limpio.groupby(["customer_id", "customer_name"], dropna=False)
        .agg(
            n_facturas=("invoice_id", "nunique"),
            monto_total=("product_subtotal", "sum"),
        )
        .reset_index()
    )

    return (
        agrupado.sort_values(
            ["n_facturas", "monto_total"], ascending=[False, False]
        )
        .head(n)
        .reset_index(drop=True)
    )