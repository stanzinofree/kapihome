from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="KapiHome API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "KapiHome API - Zen Capibara Style"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "kapihome-backend"}
    )
