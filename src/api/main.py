from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io

from src.ingestion.validator import cargar_csv
from src.analytics.basico import resumen_general, ventas_diarias

app = FastAPI(
    title="iasights API",
    description="Backend para análisis de datos de ventas con IA",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/summary")
async def summary_endpoint(file: UploadFile = File(...)):
    """
    Recibe un archivo CSV y devuelve un resumen general del dataset.
    """
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    df = cargar_csv(df) if isinstance(df, pd.DataFrame) else cargar_csv(file)

    resumen = resumen_general(df)
    return resumen


@app.post("/ventas-diarias")
async def ventas_diarias_endpoint(file: UploadFile = File(...)):
    """
    Recibe un archivo CSV y devuelve ventas agregadas por día.
    """
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    df = df.dropna(subset=["transaction_date"])
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    ventas = ventas_diarias(df)

    return ventas.to_dict(orient="records")