import sys
from datetime import datetime
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.columns import Columns
from src.generator.simulator import TelemetryPayload

class TelemetryTUI:
    def __init__(self):
        self.total_processed = 0
        self.anomaly_count = 0
        self.latest_metrics = {}
        # Keep track of the last 10 anomalies for the scrolling log
        self.anomaly_log = []

    def process_new_event(self, payload: TelemetryPayload, is_anomaly: bool):
        """Updates the internal TUI state with incoming stream packets."""
        self.total_processed += 1
        
        # Track latest status per device
        self.latest_metrics[payload.device_id] = {
            "velocity": f"{payload.velocity:.1f} km/h",
            "temp": f"{payload.battery_temp:.1f} °C",
            "brake": f"{payload.brake_pressure:.1f} psi",
            "status": "[bold red]🚨 ANOMALY[/]" if is_anomaly else "[bold green]✅ NORMAL[/]"
        }

        if is_anomaly:
            self.anomaly_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = (timestamp, payload.device_id, f"{payload.velocity:.1f}", f"{payload.battery_temp:.1f}")
            self.anomaly_log.insert(0, log_entry)
            if len(self.anomaly_log) > 10:
                self.anomaly_log.pop()

    def generate_layout(self) -> Layout:
        """Dynamically generates the structural layout matrix grid."""
        layout = Layout()
        
        # Split layout into header, body, and footer
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )

        # Body split into left (fleet metrics) and right (anomaly logging engine)
        layout["body"].split_row(
            Layout(name="fleet", ratio=1),
            Layout(name="logs", ratio=1)
        )

        # 1. Render Header Panel
        layout["header"].update(Panel(
            f"[bold cyan]🛰️  AV TELEMETRY STREAM PIPELINE[/] | "
            f"Analyzed: [bold white]{self.total_processed}[/] | "
            f"Threats Flagged: [bold red]{self.anomaly_count}[/]",
            border_style="cyan"
        ))

        # 2. Render Live Active Fleet State Table
        fleet_table = Table(title="📦 Active Autonomous Fleet Status", expand=True)
        fleet_table.add_column("Device ID", style="bold white")
        fleet_table.add_column("Speed", justify="right")
        fleet_table.add_column("Battery Temp", justify="right")
        fleet_table.add_column("Brake Pressure", justify="right")
        fleet_table.add_column("ML Assessment", justify="center")

        for dev_id, metrics in sorted(self.latest_metrics.items()):
            fleet_table.add_row(
                dev_id, metrics["velocity"], metrics["temp"], metrics["brake"], metrics["status"]
            )
        layout["fleet"].update(Panel(fleet_table, border_style="blue"))

        # 3. Render Historical Anomaly Scrolling Feed
        log_table = Table(title="🚨 Real-Time Security & Failure Log", expand=True)
        log_table.add_column("Time", style="dim cyan", width=10)
        log_table.add_column("Device ID", style="bold red", width=15)
        log_table.add_column("Speed (km/h)", justify="right")
        log_table.add_column("Temp (°C)", justify="right")

        for row in self.anomaly_log:
            log_table.add_row(*row)
        layout["logs"].update(Panel(log_table, border_style="red"))

        # 4. Render Footer Context
        layout["footer"].update(Panel(
            "[dim]Unsupervised Isolation Forest Engine Active • Press CTRL+C to stop simulation pipeline safely[/]",
            border_style="dim"
        ))

        return layout