"""
Log Anomaly Detection API
FastAPI backend service
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import LogAnomalyModel

app = FastAPI(
    title="Log Anomaly Detection API",
    description="ML service for detecting anomalies in log files",
    version="1.0.0"
)

# Global model instance
model: Optional[LogAnomalyModel] = None


class LogEntry(BaseModel):
    log: str


class LogBatch(BaseModel):
    logs: List[str]


class PredictionResult(BaseModel):
    log: str
    is_anomaly: bool
    anomaly_score: float


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global model
    model = LogAnomalyModel()
    
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    if os.path.exists(model_path):
        model.load(model_path)
        print("Model loaded successfully")
    else:
        # Train with sample data if no model exists
        print("No model found, training with sample data...")
        from train import generate_sample_logs
        logs = generate_sample_logs()
        model.train(logs)
        model.save(model_path)
        print("Model trained and saved")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None and model.is_trained
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None and model.is_trained,
        "model_path": os.path.join(os.path.dirname(__file__), "model.pkl")
    }


@app.post("/predict", response_model=List[PredictionResult])
async def predict(batch: LogBatch):
    """Predict anomalies for a batch of logs"""
    if model is None or not model.is_trained:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        results = model.predict(batch.logs)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train")
async def train(batch: LogBatch):
    """Retrain the model with new data"""
    global model
    
    try:
        model = LogAnomalyModel()
        model.train(batch.logs)
        
        model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
        model.save(model_path)
        
        return {
            "status": "success",
            "message": f"Model trained with {len(batch.logs)} samples"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)