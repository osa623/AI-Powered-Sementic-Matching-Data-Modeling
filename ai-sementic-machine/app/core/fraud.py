from sklearn.ensemble import IsolationForest
import numpy as np
import pickle
import os
from app.config import settings

class FraudDetectionEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FraudDetectionEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("Loading Fraud Detection Model...")
        model_path = os.path.join(settings.BASE_DIR, "data/models/fraud_model.pkl")
        
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print("✅ Fraud Model Loaded.")
        else:
            print("⚠️ Training new Isolation Forest model...")
            self.model = IsolationForest(contamination=0.1, random_state=42)
            print("✅ New model initialized.")

    def extract_features(self, user_metadata: dict):
        """
        Extract behavioral features from user metadata
        Features: claim_frequency, time_variance, location_consistency, etc.
        """
        features = [
            user_metadata.get('claim_count', 0),
            user_metadata.get('claim_frequency_per_day', 0.0),
            user_metadata.get('avg_time_between_claims', 24.0),
            user_metadata.get('location_variance', 0.0),
            user_metadata.get('account_age_days', 1)
        ]
        return np.array(features).reshape(1, -1)

    def predict_fraud(self, user_metadata: dict):
        """
        Returns: fraud_score (0-100), is_suspicious (bool)
        """
        features = self.extract_features(user_metadata)
        
        # Predict: -1 = anomaly (fraud), 1 = normal
        prediction = self.model.predict(features)[0]
        anomaly_score = self.model.score_samples(features)[0]
        
        # Convert to 0-100 scale (lower = more suspicious)
        fraud_score = max(0, min(100, (1 - abs(anomaly_score)) * 100))
        
        return {
            "fraud_score": round(fraud_score, 2),
            "is_suspicious": prediction == -1,
            "reason": "Anomalous behavior pattern detected" if prediction == -1 else "Normal behavior"
        }
