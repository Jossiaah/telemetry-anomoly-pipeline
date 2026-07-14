# 🛰️ Real-Time Autonomous Telemetry & Anomaly Detection Pipeline

An end-to-end, high-performance streaming telemetry engine and unsupervised machine learning pipeline. This system simulates a distributed fleet of autonomous vehicles broadcasting high-frequency metric packets, applies real-time statistical inference via an **Isolation Forest** to catch hardware malfunctions, and displays live states inside an optimization-focused **Terminal User Interface (TUI)**.

## 🏗️ System Architecture & Data Flow

```text
[Simulated AV Fleet] (Async Loops)
        │
        ▼ (Strongly-Typed Pydantic Data Matrix)
[Virtualized Event Broker] (FastStream TestRabbitBroker)
        │
        ▼ (Non-Blocking Ingestion Worker)
[Unsupervised ML Engine] (Scikit-Learn Isolation Forest)
        │
        ├──► [✅ Normal Status Vector]  ──► Update Fleet Matrix UI Panel
        └──► [🚨 Structural Outlier]    ──► Fire System Warning Alert Log
```

## 🛠️ Key Technical Implementations
* **Asynchronous Execution Architecture:** Leverages Python `asyncio` and `FastStream` frameworks to run production-mimicking message subscribers and producers concurrently without blocking I/O threads.
* **Unsupervised Machine Learning Isolation:** Uses an Isolation Forest algorithm initialized via a data warm-up cold-start phase. No manual alert threshold tuning or labels required; the model classifies hardware degradation (e.g., thermal runway events) strictly on mathematical outlier distributions.
* **Low-Overhead Terminal UI Execution:** Implements a headless, terminal layout dashboard using `Rich` to handle split-screen canvas matrices, custom component spacing, scrolling warning logs, and continuous metric refreshes.
* **Robust MLOps CI/CD Automation:** Backed by automated **GitHub Actions workflows** that trigger continuous background health and model integrity test validation runs on a recurring cron schedule.

## 🚀 Getting Started & Local Launch

### 1. Environment Setup & Dependency Installation
Ensure you are using Python 3.10+ in a clean project environment:
```bash
# Clone the repository and navigate inside
git clone https://github.com
cd telemetry-anomaly-pipeline

# Initialize and spin up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install portably tracked structural requirements
pip install -r requirements.txt
```

### 2. Run the Main Streaming TUI Engine
Execute the self-contained processing pipeline entrypoint:
```bash
python run_pipeline.py
```
*To exit the full-screen terminal visualization matrix cleanly at any point, press `CTRL + C`.*

### 3. Run the Automated Integrity Suite
Execute the system validation tests locally using:
```bash
pytest tests/
```

## 📂 Project Organization Blueprint
```text
telemetry-anomaly-pipeline/
├── .github/workflows/      # Automated GitHub Cron Integrity Actions
├── config/                 # Dynamic system parameters config mappings
├── src/
│   ├── generator/          # Pydantic schema engines & telemetry simulators
│   ├── model/              # Isolation Forest outlier detection tracking modules
│   ├── pipeline/           # FastStream messaging consumers & stream loops
│   └── tui_dashboard.py    # Headless Rich Terminal UI layout configurations
├── tests/                  # Pytest modular system validation suites
├── run_pipeline.py         # Main operational runtime entrypoint
└── requirements.txt        # Production dependency tracking configurations
```
