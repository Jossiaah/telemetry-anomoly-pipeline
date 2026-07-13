import asyncio
from src.pipeline.stream import initialize_and_run_local

if __name__ == "__main__":
    print("[LAUNCHER] Starting Telemetry Anomaly Pipeline Execution Engine...")
    asyncio.run(initialize_and_run_local())
    print("[LAUNCHER] Simulation runtime complete. Exiting cleanly.")
