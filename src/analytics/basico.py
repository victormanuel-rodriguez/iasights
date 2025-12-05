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