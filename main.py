from contextlib import asynccontextmanager
from pathlib import Path
import json
import time
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "model" / "modelo_cancer.joblib"
META_PATH = BASE_DIR / "model" / "metadata.json"

model = None
metadata = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, metadata
    if not MODEL_PATH.exists() or not META_PATH.exists():
        raise RuntimeError("No se encontraron el modelo o sus metadatos.")
    model = joblib.load(MODEL_PATH)
    metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
    yield

app = FastAPI(
    title="API de clasificación de tumores",
    version="1.0.0",
    description="API académica para inferencia con Breast Cancer Wisconsin.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    features: list[float] = Field(
        ...,
        description="Lista ordenada de 30 características numéricas."
    )

    @field_validator("features")
    @classmethod
    def validate_features(cls, values: list[float]) -> list[float]:
        if len(values) != 30:
            raise ValueError("Se requieren exactamente 30 características.")
        if any(v != v or abs(v) == float("inf") for v in values):
            raise ValueError("No se permiten valores NaN o infinitos.")
        return values

@app.get("/")
def root():
    return {
        "service": "clasificador-cancer-api",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "version": metadata["version"] if metadata else None
    }

@app.get("/model-info")
def model_info():
    if metadata is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible.")
    return metadata

@app.post("/predict")
def predict(payload: PredictionRequest):
    if model is None or metadata is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible.")
    started = time.perf_counter()
    frame = pd.DataFrame([payload.features], columns=metadata["feature_names"])
    prediction = int(model.predict(frame)[0])
    probabilities = model.predict_proba(frame)[0]
    latency_ms = (time.perf_counter() - started) * 1000
    return {
        "prediction": prediction,
        "diagnosis": metadata["target_mapping"][str(prediction)],
        "probability_malignant": round(float(probabilities[0]), 6),
        "probability_benign": round(float(probabilities[1]), 6),
        "latency_ms": round(latency_ms, 3),
        "model_version": metadata["version"]
    }
