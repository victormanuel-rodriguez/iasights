import pandas as pd

def ventas_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ventas totales por categoría de producto.
    """
    agg = (
        df.groupby("product_category", as_index=False)
          .agg(total_ventas=("product_subtotal", "sum"))
          .sort_values("total_ventas", ascending=False)
    )
    return agg


def top_productos_por_ventas(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Top N productos por ventas totales.
    """
    agg = (
        df.groupby(["product_id", "product_name"], as_index=False)
          .agg(total_ventas=("product_subtotal", "sum"))
          .sort_values("total_ventas", ascending=False)
          .head(top_n)
    )
    return agg


def ventas_por_hora(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ventas agregadas por hora del día (0–23).
    """
    # Extraemos la hora a partir de transaction_time
    horas = pd.to_datetime(df["transaction_time"], format="%H:%M:%S").dt.hour
    df_tmp = df.copy()
    df_tmp["hora"] = horas

    agg = (
        df_tmp.groupby("hora", as_index=False)
              .agg(total_ventas=("product_subtotal", "sum"))
              .sort_values("hora")
    )
    return agg


def ventas_por_dia_semana(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ventas agregadas por día de la semana (0=Lunes, 6=Domingo).
    """
    df_tmp = df.copy()
    df_tmp["dia_semana"] = df_tmp["transaction_date"].dt.dayofweek

    agg = (
        df_tmp.groupby("dia_semana", as_index=False)
              .agg(total_ventas=("product_subtotal", "sum"))
              .sort_values("dia_semana")
    )
    return agg