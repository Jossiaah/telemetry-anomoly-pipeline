import asyncio
import logging
from faststream import FastStream
from faststream.rabbit import RabbitBroker, TestRabbitBroker # Native localized stream architecture

# Set up logging architecture
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelemetryPipeline")

# Initialize the production-ready RabbitBroker
broker = RabbitBroker()
app = FastStream(broker)


from src.generator.simulator import generate_telemetry, TelemetryPayload
from src.model.detector import TelemetryAnomalyDetector

detector = TelemetryAnomalyDetector(contamination=0.05)
TELEMETRY_QUEUE = "vehicle.telemetry.raw"

@broker.subscriber(TELEMETRY_QUEUE)
async def process_telemetry_event(payload: TelemetryPayload) -> None:
    """
    Asynchronously consumes vehicle events and passes them through the 
    Isolation Forest engine for real-time inference.
    """
    is_anomaly = detector.predict_anomaly(payload)
    
    if is_anomaly:
        logger.warning(
            f"🚨 [ANOMALY DETECTED] Device: {payload.device_id} | "
            f"Temp: {payload.battery_temp:.1f}°C | Brake Psi: {payload.brake_pressure:.1f} | "
            f"Speed: {payload.velocity:.1f} km/h"
        )
    else:
        logger.info(
            f"✅ [NORMAL] Device: {payload.device_id} | "
            f"Speed: {payload.velocity:.1f} km/h | Temp: {payload.battery_temp:.1f}°C"
        )

async def simulate_fleet_stream(fleet_size: int = 3, run_duration_seconds: int = 10):
    """Asynchronously streams data from the fleet into the messaging queue."""
    devices = [f"AV-FLEET-{i:03d}" for i in range(1, fleet_size + 1)]
    logger.info(f"[PRODUCER] Starting active telemetry streams for: {devices}")
    
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < run_duration_seconds:
        for device_id in devices:
            # Generate metrics and randomly inject anomaly frames based on current time
            inject_anomaly = (asyncio.get_event_loop().time() % 4 < 0.5)
            payload = generate_telemetry(device_id=device_id, inject_anomaly=inject_anomaly)
            await broker.publish(payload, queue=TELEMETRY_QUEUE)
            
        await asyncio.sleep(0.8)

async def initialize_and_run_local():
    """
    Simulates a historical cold-start to train the ML model baseline 
    and handles the async runtime loops under a virtualized local broker context.
    """
    logger.info("[SYSTEM] Initializing pipeline warm-up phase...")
    
    # 1. Generate normal historical operational data to train our baseline
    historical_data = []
    for _ in range(100):
        historical_data.append(generate_telemetry(device_id="AV-BASELINE-WARMUP", inject_anomaly=False))
        
    # 2. Train the unsupervised Isolation Forest model
    logger.info(f"[ML ENGINE] Training Isolation Forest baseline on {len(historical_data)} historical vectors...")
    detector.fit_baseline(historical_data)
    logger.info("[ML ENGINE] Model training complete. Streaming system is live.")
    
    # 3. Spin up the real-time simulation fleet inside the virtual broker context
    async with TestRabbitBroker(broker):
        await simulate_fleet_stream(fleet_size=3, run_duration_seconds=12)
