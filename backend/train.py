"""
Training script for Log Anomaly Detection Model
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import LogAnomalyModel
import numpy as np


def generate_sample_logs():
    """Generate sample log data for training"""
    normal_logs = [
        "INFO: Application started successfully",
        "INFO: User logged in successfully",
        "INFO: Database connection established",
        "INFO: Request processed in 45ms",
        "INFO: Cache hit for user session",
        "INFO: API response returned successfully",
        "INFO: Background job completed",
        "INFO: Health check passed",
        "INFO: File uploaded successfully",
        "INFO: Email sent successfully",
    ]
    
    anomaly_logs = [
        "ERROR: Database connection timeout after 30s",
        "ERROR: Out of memory exception occurred",
        "ERROR: Invalid authentication token",
        "ERROR: Disk space critical - less than 1% remaining",
        "ERROR: Service unavailable - upstream timeout",
        "ERROR: Null pointer exception in handler",
        "ERROR: SSL certificate expired",
        "ERROR: Rate limit exceeded for API",
    ]
    
    return normal_logs + anomaly_logs


def main():
    print("Training Log Anomaly Detection Model...")
    
    # Generate sample data
    logs = generate_sample_logs()
    print(f"Training with {len(logs)} log samples")
    
    # Create and train model
    model = LogAnomalyModel()
    model.train(logs)
    
    # Save model
    model.save("model.pkl")
    print("Model trained and saved to model.pkl")
    
    # Test predictions
    test_logs = [
        "INFO: User request processed successfully",
        "ERROR: Database connection timeout",
        "INFO: Cache updated",
    ]
    
    print("\nTesting predictions:")
    results = model.predict(test_logs)
    for result in results:
        status = "ANOMALY" if result['is_anomaly'] else "Normal"
        print(f"  [{status}] {result['log'][:50]}...")


if __name__ == "__main__":
    main()