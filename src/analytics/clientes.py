import pandas as pd

def clientes_recurrentes(df: pd.DataFrame, min_visitas: int = 2) -> pd.DataFrame:
    """
    Devuelve clientes conocidos (no null) con al menos min_visitas facturas.
    """
    df_conocidos = df[df["customer_id"].notna()].copy()

    agg = (
        df_conocidos.groupby(["customer_id", "customer_name"], as_index=False)
                    .agg(
                        num_facturas=("invoice_id", "nunique"),
                        total_ventas=("product_subtotal", "sum")
                    )
    )

    recurrentes = agg[agg["num_facturas"] >= min_visitas].sort_values(
        ["num_facturas", "total_ventas"],
        ascending=[False, False]
    )

    return recurrentes


def resumen_clientes(df: pd.DataFrame) -> dict:
    """
    Métricas generales sobre clientes.
    """
    df_conocidos = df[df["customer_id"].notna()].copy()

    num_clientes_unicos = df_conocidos["customer_id"].nunique()
    total_ventas_clientes_conocidos = df_conocidos["product_subtotal"].sum()

    return {
        "num_clientes_unicos": int(num_clientes_unicos),
        "total_ventas_clientes_conocidos": float(total_ventas_clientes_conocidos),
    }