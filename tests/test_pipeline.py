import pytest
from src.generator.simulator import generate_telemetry, TelemetryPayload
from src.model.detector import TelemetryAnomalyDetector

def test_telemetry_generator_schema():
    """Verifies the simulation engine generates structurally correct type-safe data."""
    payload = generate_telemetry(device_id="TEST-AV-001", inject_anomaly=False)
    
    assert isinstance(payload, TelemetryPayload)
    assert payload.device_id == "TEST-AV-001"
    assert 40.0 <= payload.velocity <= 90.0
    assert 25.0 <= payload.battery_temp <= 42.0

def test_anomaly_injection_profile():
    """Confirms that abnormal data structures are successfully triggered upon command."""
    payload = generate_telemetry(device_id="TEST-AV-ERR", inject_anomaly=True)
    
    # Anomaly values should break far past standard operational bounds
    assert payload.battery_temp >= 85.0
    assert payload.velocity >= 120.0

def test_isolation_forest_unsupervised_flow():
    """Validates cold-start training logic and streaming real-time scoring vectors."""
    detector = TelemetryAnomalyDetector(contamination=0.05)
    
    # 1. Verify model handles cold start safely before training completes
    fallback_payload = generate_telemetry("AV-EARLY")
    assert detector.predict_anomaly(fallback_payload) is False
    
    # 2. Train baseline model with clean data matrices
    normal_training_set = [generate_telemetry("AV-TRAIN", inject_anomaly=False) for _ in range(50)]
    detector.fit_baseline(normal_training_set)
    assert detector.is_trained is True
    
    # 3. Challenge the model with a clear structural anomaly payload
    anomaly_payload = generate_telemetry("AV-MALFUNCTION", inject_anomaly=True)
    prediction = detector.predict_anomaly(anomaly_payload)
    
    # The Isolation forest should flag this outlier vector instantly
    assert prediction is True
