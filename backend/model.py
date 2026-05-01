"""
Log Anomaly Detection Model
Hybrid ML + Rule-based anomaly detection
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from typing import List, Dict, Any


class LogAnomalyModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )

        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )

        self.is_trained = False

    # ----------------------------
    # TRAIN MODEL
    # ----------------------------
    def train(self, logs: List[str], labels: List[int] = None):
        """Train anomaly detection model"""

        # Convert logs → TF-IDF features
        self.vectorizer.fit(logs)
        X = self.vectorizer.transform(logs).toarray()

        # Train Isolation Forest
        if labels is not None:
            self.model.fit(X, y=labels)
        else:
            self.model.fit(X)

        self.is_trained = True
        return self

    # ----------------------------
    # PREDICT
    # ----------------------------
    def predict(self, logs: List[str]) -> List[Dict[str, Any]]:
        """Predict anomalies using hybrid logic"""

        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")

        X = self.vectorizer.transform(logs).toarray()

        # ML predictions
        predictions = self.model.predict(X)  # -1 = anomaly
        scores = self.model.decision_function(X)

        results = []

        for i, (pred, score) in enumerate(zip(predictions, scores)):
            log = str(logs[i]).strip()

            if not log:
                continue

            # ----------------------------
            # RULE-BASED LAYER (IMPORTANT)
            # ----------------------------
            if "CRITICAL" in log.upper():
                is_anomaly = True
                final_score = 0.95

            elif "ERROR" in log.upper():
                is_anomaly = True
                final_score = 0.85

            elif "WARNING" in log.upper():
                is_anomaly = True
                final_score = 0.6

            else:
                # fallback to ML model
                is_anomaly = bool(pred == -1)
                final_score = float(score)

            results.append({
                "log": log,
                "is_anomaly": is_anomaly,
                "anomaly_score": float(final_score),
                "status": "Anomaly 🚨" if is_anomaly else "Normal ✅"
            })

        return results

    # ----------------------------
    # SAVE MODEL
    # ----------------------------
    def save(self, path: str):
        """Save model to disk"""
        joblib.dump({
            'vectorizer': self.vectorizer,
            'model': self.model,
            'is_trained': self.is_trained
        }, path)

    # ----------------------------
    # LOAD MODEL
    # ----------------------------
    def load(self, path: str):
        """Load model from disk"""
        data = joblib.load(path)

        self.vectorizer = data['vectorizer']
        self.model = data['model']
        self.is_trained = data['is_trained']