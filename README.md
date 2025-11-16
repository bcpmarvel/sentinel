<div align="center">

# 🎯 Sentinel

**Real-time object detection and tracking system**

[![CI](https://github.com/bcpmarvel/sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/bcpmarvel/sentinel/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**YOLO11** × **BoT-SORT** × **FastAPI**

[Features](#-features) • [Quick Start](#-quick-start) • [Demo](#-demo) • [API](#-api) • [Documentation](#-documentation)

</div>

---

## 🎬 Demo

### 📸 Object Detection

<table>
  <tr>
    <td align="center" width="50%">
      <b>Pedestrian Detection</b><br>
      <img src="demos/outputs/images/pedestrian.jpg" alt="YOLO11 pedestrian detection" width="100%">
    </td>
    <td align="center" width="50%">
      <b>Traffic Detection</b><br>
      <img src="demos/outputs/images/traffic.jpg" alt="YOLO11 traffic detection" width="100%">
    </td>
  </tr>
</table>

### 🎥 Multi-Object Tracking

<div align="center">
  <img src="demos/outputs/videos/mot17-05-preview.gif" alt="BoT-SORT multi-object tracking demo" width="480">
  <br>
  <i>Real-time tracking of 20+ pedestrians with trajectory prediction</i>
  <br><br>
  <a href="https://github.com/bcpmarvel/sentinel/releases/download/v0.1.0/mot17-05-tracked.mp4">📥 Download Full Quality Video</a> (34MB MP4)
</div>

---

## ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🎯 **YOLO11 Detection** | State-of-the-art object detection at 30+ FPS | ✅ |
| 🔄 **BoT-SORT Tracking** | Multi-object tracking with trajectory prediction | ✅ |
| 📊 **Zone Analytics** | Count objects, measure dwell time, detect entries/exits | ✅ |
| 🚀 **REST API** | Production-ready FastAPI server | ✅ |
| 🔌 **WebSocket Streaming** | Real-time video streaming | ✅ |
| ⚡ **GPU Acceleration** | MPS (Apple Silicon) and CUDA support | ✅ |
| 🐳 **Docker Ready** | Containerized deployment with docker-compose | ✅ |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- `uv` package manager ([install](https://docs.astral.sh/uv/))

### Installation

```bash
git clone https://github.com/bcpmarvel/sentinel.git
cd sentinel
uv sync
```

### Model Setup

YOLO11 models are automatically downloaded on first use. No manual download required.

### Run Detection

```bash
# Webcam detection
detect --source 0

# Video file with tracking
detect --source video.mp4 --track

# Zone analytics
detect --source 0 --track --analytics --zones zones.json
```

### Start API Server

```bash
serve
```

Test the API:
```bash
curl -X POST http://localhost:8000/api/detect -F "file=@image.jpg"
```

---

## 🐳 Docker Deployment

```bash
# Development (hot reload)
docker-compose up api

# Production
docker-compose --profile production up api-prod
```

---

## 🛠️ Usage

<details>
<summary><b>CLI Commands</b></summary>

### Basic Detection
```bash
detect --source 0                    # Webcam
detect --source video.mp4            # Video file
detect --source rtsp://camera.ip     # RTSP stream
```

### Advanced Options
```bash
detect --source 0 \
  --model yolo11s.pt \
  --device mps \
  --conf 0.6 \
  --track \
  --analytics \
  --zones zones.json \
  --config sentinel.toml
```

</details>

<details>
<summary><b>API Endpoints</b></summary>

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Detect Objects
```bash
curl -X POST http://localhost:8000/api/detect \
  -F "file=@image.jpg" \
  -F "conf_threshold=0.5"
```

### Response
```json
{
  "detections": [
    {
      "x1": 123.4, "y1": 456.7,
      "x2": 789.0, "y2": 321.5,
      "confidence": 0.89,
      "class_id": 0,
      "class_name": "person"
    }
  ],
  "image_width": 1280,
  "image_height": 720,
  "processing_time_ms": 45.2,
  "model_name": "yolo11m.pt",
  "device": "mps"
}
```

</details>

<details>
<summary><b>Zone Analytics</b></summary>

Create `zones.json` to define monitoring zones:

```json
[
  {
    "id": "zone_1",
    "name": "Entrance",
    "polygon": [[100, 100], [500, 100], [500, 400], [100, 400]],
    "color": [255, 0, 0]
  }
]
```

**Metrics tracked:**
- Object count in zone
- Average/max dwell time
- Entry/exit events

</details>

---

## ⚙️ Configuration

### Docker/API Deployment

Use `.env` for environment variables:

```bash
cp .env.example .env
```

```env
MODEL_NAME=yolo11m.pt
DEVICE=cpu
API_HOST=0.0.0.0
API_PORT=8000
LOG_FORMAT=json
```

### CLI Usage

Use `sentinel.toml` for advanced features:

```bash
cp sentinel.example.toml sentinel.toml
detect --config sentinel.toml --source 0
```

---

## 🏗️ Architecture

> **Note:** Architecture diagram placeholder

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Input     │─────▶│   YOLO11     │─────▶│  BoT-SORT   │
│ (Video/API) │      │  Detection   │      │  Tracking   │
└─────────────┘      └──────────────┘      └─────────────┘
                                                   │
                                                   ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Output    │◀─────│ Visualization│◀─────│  Analytics  │
│ (API/Stream)│      │  & Rendering │      │   (Zones)   │
└─────────────┘      └──────────────┘      └─────────────┘
```

<details>
<summary><b>Project Structure</b></summary>

```
src/sentinel/
├── api/              # FastAPI routes, schemas, dependencies
│   ├── app.py
│   ├── routes.py
│   ├── schemas.py
│   └── dependencies.py
├── analytics/        # Zone analytics, dwell time tracking
│   ├── service.py
│   ├── models.py
│   └── dwell.py
├── detection/        # YOLO11 detector, service
│   ├── service.py
│   └── models.py
├── visualization/    # Annotators for drawing
│   └── annotators.py
├── cli.py            # CLI entrypoint
├── server.py         # API server entrypoint
├── config.py         # Pydantic settings
└── pipeline.py       # Video processing pipeline
```

</details>

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Detection** | [YOLO11](https://github.com/ultralytics/ultralytics) (Ultralytics) |
| **Tracking** | [BoT-SORT](https://github.com/NirAharon/BoT-SORT) |
| **Deep Learning** | [PyTorch](https://pytorch.org) (MPS/CUDA) |
| **API Framework** | [FastAPI](https://fastapi.tiangolo.com) |
| **Computer Vision** | [OpenCV](https://opencv.org), [Supervision](https://supervision.roboflow.com) |
| **CLI** | [Typer](https://typer.tiangolo.com) |
| **Logging** | [Structlog](https://www.structlog.org) |
| **Packaging** | [uv](https://docs.astral.sh/uv/) |

---

## 🧪 Development

### Setup

```bash
uv sync --dev
```

### Code Quality

```bash
# Format
uv run ruff format .

# Lint
uv run ruff check .

# Fix
uv run ruff check --fix .
```

### Testing

```bash
uv run pytest
uv run pytest -v --cov=sentinel
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ultralytics](https://github.com/ultralytics/ultralytics) for YOLO11
- [BoT-SORT](https://github.com/NirAharon/BoT-SORT) for multi-object tracking
- [Roboflow](https://roboflow.com) for Supervision library

---

<div align="center">

**[⬆ Back to Top](#-sentinel)**

</div>
