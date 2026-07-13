import asyncio
import logging
from faststream import FastStream
from faststream.broker.core.mixins import StreamMessage
from faststream.rabbit import InMemoryBroker # Lightweight, zero-install event broker
from src.generator.simulator import generate_telemetry, TelemetryPayload

# Set up clean production logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelemetryPipeline")

# Initialize the broker and the main application engine
broker = InMemoryBroker()
app = FastStream(broker)

# Define our localized data streaming channel
TELEMETRY_QUEUE = "vehicle.telemetry.raw"

@broker.subscriber(TELEMETRY_QUEUE)
async def process_telemetry_event(payload: TelemetryPayload, msg: StreamMessage) -> None:
    """
    Asynchronously consumes raw vehicle telemetry messages from the event queue.
    This acts as the core injection point for our ML model scoring engine.
    """
    logger.info(
        f"[CONSUMER] Received event from Device {payload.device_id} | "
        f"Velocity: {payload.velocity:.2f} km/h | Temp: {payload.battery_temp:.1f}°C"
    )
    
    # TODO: Connect the Isolation Forest model step here to score the incoming record:
    # is_anomaly = model.predict(payload)


async def simulate_fleet_stream(fleet_size: int = 3, run_duration_seconds: int = 10):
    """
    Simulates a running fleet of autonomous vehicles asynchronously publishing 
    telemetry payloads directly to the event broker channel.
    """
    devices = [f"AV-FLEET-{i:03d}" for i in range(1, fleet_size + 1)]
    logger.info(f"[PRODUCER] Initializing stream simulator for fleet: {devices}")
    
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < run_duration_seconds:
        for device_id in devices:
            # Randomly inject an anomaly 5% of the time to keep data realistic
            inject_anomaly = (asyncio.get_event_loop().time() % 7 < 0.5) 
            
            # Generate the typed Pydantic data record
            payload = generate_telemetry(device_id=device_id, inject_anomaly=inject_anomaly)
            
            # Publish securely to the in-memory stream queue
            await broker.publish(payload, queue=TELEMETRY_QUEUE)
            
        # Yield control back to the event loop to prevent thread locking
        await asyncio.sleep(1.0)

@app.after_startup
async def run_pipeline_simulation():
    """Triggers automatically as soon as the FastStream app finishes booting up."""
    logger.info("[SYSTEM] Real-time engine started successfully.")
    # Run a quick 10-second simulation cycle to test throughput
    await simulate_fleet_stream(fleet_size=3, run_duration_seconds=10)
