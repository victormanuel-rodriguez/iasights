# ==========================================================
# Utilidades de etiquetas y formatos para la UI
# ==========================================================

ETIQUETAS = {
    "transaction_date": "Fecha",
    "transaction_time": "Hora",
    "invoice_id": "Factura",
    "customer_id": "ID Cliente",
    "customer_name": "Cliente",
    "product_id": "ID Producto",
    "product_name": "Producto",
    "product_category": "Categoría",
    "product_quantity": "Cantidad",
    "product_unit_price": "Precio unitario",
    "product_subtotal": "Subtotal",
    "total_ventas": "Ventas Totales",
    "prediccion": "Predicción",
    "r2_test": "Coeficiente R²",
    "n_dias_hist": "Días usados en entrenamiento",
    "cantidad_total": "Cantidad total",
    "ingreso_total": "Ingreso total",
    "n_transacciones": "No. de  transacciones",
    "n_facturas": "No. de facturas",
    "monto_total": "Monto total"
}

# Columnas monetarias que deben mostrarse con dos decimales y comas
MONEY_COLUMNS = [
    "product_unit_price",
    "product_subtotal",
    "total_ventas",
    "ingreso_total",
    "monto_total"
]

# ==========================================================
# Funciones utilitarias
# ==========================================================

def aplicar_etiquetas(df):
    """Renombra columnas según ETIQUETAS (sin modificar df original)."""
    df = df.copy()
    df.rename(columns=ETIQUETAS, inplace=True)
    return df


def formatear_monedas(df):
    """Aplica formato monetario $#,###.## a columnas definidas."""
    df = df.copy()
    for col in MONEY_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"${x:,.2f}")
    return df