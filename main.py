from fastapi import FastAPI

app = FastAPI(title="ETL Document Service")

@app.get("/health")
def health():
    return {"status": "ok"}