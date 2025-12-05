import pandas as pd

def ventas_diarias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve un DataFrame con ventas totales por día.
    """
    df_grouped = (
        df.groupby(df["transaction_date"])
          .agg(total_ventas=("product_subtotal", "sum"))
          .reset_index()
          .sort_values("transaction_date")
    )
    return df_grouped