import random
import time
from datetime import datetime
from pydantic import BaseModel, Field

class TelemetryPayload(BaseModel):
    device_id: str = Field(..., description= "Unique identifier for the vehicle")
    timestamp: str = Field(..., description= "ISO tumestamp of telemetry generation")
    velocity: float = Field(..., description= "Speed in km/h")
    battery_temp: float = Field(..., description = "Core battery temperature in Celsius")
    brake_pressure: float = Field(..., description = "Hydrolic brake psi")
    gps_lat: float
    gps_lon: float

def generate_telemetry(device_id: str, inject_anomaly: bool = False) -> TelemetryPayload:
    """Generates continuous stream data, occasionally spiking metrics to simulate failures."""
    now = datetime.utcnow().isoformat()
    
    if inject_anomaly:
        # Simulate a dangerous battery thermal runaway event or brake failure
        return TelemetryPayload(
            device_id=device_id,
            timestamp=now,
            velocity=random.uniform(120.0, 160.0),
            battery_temp=random.uniform(85.0, 105.0), # Normal is 20-45
            brake_pressure=random.uniform(10.0, 50.0), # Dropped pressure
            gps_lat=37.7749 + random.uniform(-0.01, 0.01),
            gps_lon=-122.4194 + random.uniform(-0.01, 0.01)
        )
        
    return TelemetryPayload(
        device_id=device_id,
        timestamp=now,
        velocity=random.uniform(40.0, 90.0),
        battery_temp=random.uniform(25.0, 42.0),
        brake_pressure=random.uniform(200.0, 350.0),
        gps_lat=37.7749 + random.uniform(-0.005, 0.005),
        gps_lon=-122.4194 + random.uniform(-0.005, 0.005)
    )
