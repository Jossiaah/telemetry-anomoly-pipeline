import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from src.generator.simulator import TelemetryPayload

class TelemetryAnomalyDetector:
    def __init__(self, contamination: float = 0.02, random_state: int = 42):
        """
        Initializes the unsupervised Isolation Forest model.
        Contamination represents the expected percentage of outliers in the data.
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1 # Utilize all available CPU cores for execution speed
        )
        self.is_trained = False

    def _extract_features(self, payload: TelemetryPayload) -> np.ndarray:
        """Helper method to convert standard Pydantic models into a model-friendly numerical array."""
        return np.array([[
            payload.velocity,
            payload.battery_temp,
            payload.brake_pressure
        ]])

    def fit_baseline(self, historical_payloads: list[TelemetryPayload]) -> None:
        """
        Trains the initial baseline model using a batch of historical telemetry.
        Demonstrates production MLOps cold-start data handling.
        """
        if not historical_payloads:
            raise ValueError("Cannot train baseline with empty data.")
            
        # Convert list of Pydantic models into a matrix
        data_matrix = np.vstack([self._extract_features(p) for p in historical_payloads])
        
        self.model.fit(data_matrix)
        self.is_trained = True

    def predict_anomaly(self, payload: TelemetryPayload) -> bool:
        """
        Evaluates an incoming streaming telemetry payload in real-time.
        Returns True if flagged as an anomaly, False if normal.
        """
        if not self.is_trained:
            # Fallback mechanism if streaming data hits the engine before warm-up training finishes
            return False
            
        features = self._extract_features(payload)
        
        # Isolation Forest outputs: 1 for inliers (normal), -1 for outliers (anomalies)
        prediction = self.model.predict(features)
        
        return bool(prediction[0] == -1)