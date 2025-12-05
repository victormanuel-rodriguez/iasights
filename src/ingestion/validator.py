import pandas as pd

REQUIRED_COLUMNS = [
    "invoice_id",
    "transaction_date",
    "transaction_time",
    "customer_id",
    "customer_name",
    "product_id",
    "product_name",
    "product_category",
    "product_quantity",
    "product_unit_price",
    "product_subtotal"
]

def cargar_csv(data) -> pd.DataFrame:
    """
    Acepta: ruta a archivo (str) o DataFrame cargado en memoria.
    """
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.read_csv(data)

    # Validación de columnas
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Columnas faltantes: {missing}")

    # Casting
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d")
    df["product_quantity"] = pd.to_numeric(df["product_quantity"], errors="coerce")
    df["product_unit_price"] = pd.to_numeric(df["product_unit_price"], errors="coerce")
    df["product_subtotal"] = pd.to_numeric(df["product_subtotal"], errors="coerce")

    return df