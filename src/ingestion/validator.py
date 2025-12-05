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

def cargar_csv(ruta: str) -> pd.DataFrame:
    """
    Carga el CSV, valida columnas y hace casting básico.
    """
    df = pd.read_csv(ruta)

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