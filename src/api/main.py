from fastapi import FastAPI

app = FastAPI(title="iasights API")

@app.get("/health")
def health_check():
    return {"status": "ok"}