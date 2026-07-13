import asyncio
import logging
from faststream import FastStream
from faststream.rabbit import RabbitBroker, TestRabbitBroker
from rich.live import Live

from src.generator.simulator import generate_telemetry, TelemetryPayload
from src.model.detector import TelemetryAnomalyDetector
from src.tui_dashboard import TelemetryTUI

# Set up logging architecture (Silencing background logs so they don't break our TUI graphics)
logging.basicConfig(level=logging.ERROR)

broker = RabbitBroker()
app = FastStream(broker)
detector = TelemetryAnomalyDetector(contamination=0.05)
tui = TelemetryTUI()

TELEMETRY_QUEUE = "vehicle.telemetry.raw"

@broker.subscriber(TELEMETRY_QUEUE)
async def process_telemetry_event(payload: TelemetryPayload) -> None:
    """Consumes real-time event topics and pipes calculations to the TUI display layer."""
    is_anomaly = detector.predict_anomaly(payload)
    # Feed metrics straight to our terminal interface object
    tui.process_new_event(payload, is_anomaly)

async def simulate_fleet_stream(fleet_size: int = 4, run_duration_seconds: int = 30):
    """Asynchronously streams data from the fleet into the messaging queue."""
    devices = [f"AV-FLEET-{i:03d}" for i in range(1, fleet_size + 1)]
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < run_duration_seconds:
        for device_id in devices:
            # Inject structural failures dynamically over time
            inject_anomaly = (asyncio.get_event_loop().time() % 5 < 0.6)
            payload = generate_telemetry(device_id=device_id, inject_anomaly=inject_anomaly)
            await broker.publish(payload, queue=TELEMETRY_QUEUE)
            
        await asyncio.sleep(0.4) # Faster refresh rate for responsive UI visuals

async def initialize_and_run_local():
    """Warms up the ML model and runs the main display refresh sequence loop."""
    # 1. Generate baseline operational vectors
    historical_data = [generate_telemetry(device_id="AV-WARMUP", inject_anomaly=False) for _ in range(120)]
    detector.fit_baseline(historical_data)
    
    # 2. Spin up the rich live display wrapper loop and async stream event processor
    async with TestRabbitBroker(broker):
        # The Live context manager handles cleanly rewriting the console frames smoothly
        with Live(tui.generate_layout(), refresh_per_second=4, screen=True) as live:
            
            # Run background processing task for the simulated devices
            stream_task = asyncio.create_task(simulate_fleet_stream(fleet_size=4, run_duration_seconds=45))
            
            while not stream_task.done():
                live.update(tui.generate_layout())
                await asyncio.sleep(0.25)
                
            await stream_task
