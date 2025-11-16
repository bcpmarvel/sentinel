# Sentinel

Real-time object detection and tracking system with YOLOv8 and BoT-SORT.

## Features

- YOLOv8 object detection (30+ FPS on M1/M2)
- BoT-SORT multi-object tracking
- Zone-based analytics (counting, dwell time)
- REST API for image detection
- WebSocket streaming
- GPU acceleration (MPS/CUDA)

## Installation

Requires Python 3.12+

```bash
git clone <repo-url>
cd cv-detection-tracking
uv sync
```

Download a YOLOv8 model:
```bash
mkdir -p models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O models/yolov8n.pt
```

## Usage

### CLI

**Basic detection:**
```bash
detect --source 0  # webcam
detect --source video.mp4  # file
```

**With tracking:**
```bash
detect --source 0 --track
```

**With zone analytics:**
```bash
detect --source 0 --track --analytics --zones zones.json
```

**Options:**
```bash
detect --source 0 \
  --model models/yolov8s.pt \
  --device mps \
  --conf 0.6 \
  --track \
  --analytics \
  --zones zones.json \
  --config config.toml
```

### API Server

**Start server:**
```bash
serve
```

**Detect objects in image:**
```bash
curl -X POST http://localhost:8000/api/detect \
  -F "file=@image.jpg"
```

**Health check:**
```bash
curl http://localhost:8000/api/health
```

## Configuration

Create `.env` or use `--config`:

```bash
# Model
MODEL_PATH=models/yolov8n.pt
DEVICE=mps  # mps, cuda, cpu
CONF_THRESHOLD=0.5
IOU_THRESHOLD=0.45

# API
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=["http://localhost:3000"]

# Logging
LOG_FORMAT=json  # json, console
LOG_LEVEL=INFO
```

## Project Structure

```
src/sentinel/
├── api/          # FastAPI routes, schemas, dependencies
├── analytics/    # Zone analytics, dwell time tracking
├── detection/    # YOLOv8 detector, service
├── visualization/# Annotators for drawing
├── cli.py        # CLI entrypoint
├── server.py     # API server entrypoint
├── config.py     # Pydantic settings
└── pipeline.py   # Video processing pipeline
```

## Stack

- **YOLOv8** (Ultralytics) - Object detection
- **BoT-SORT** - Multi-object tracking
- **PyTorch** - Inference with MPS/CUDA
- **FastAPI** - REST API
- **Supervision** - Video annotations
- **OpenCV** - Video I/O
- **Structlog** - Structured logging
- **Typer** - CLI framework

## Performance

| Metric | Target | Hardware |
|--------|--------|----------|
| FPS | 30+ | M1 MacBook @ 720p |
| Latency | <50ms | Per-frame inference |
| Startup | <3s | Model loading |

## Zone Analytics

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

Metrics:
- Object count in zone
- Average/max dwell time
- Entry/exit events

## API Response

```json
{
  "detections": [
    {
      "x1": 123.4,
      "y1": 456.7,
      "x2": 789.0,
      "y2": 321.5,
      "confidence": 0.89,
      "class_id": 0,
      "class_name": "person"
    }
  ],
  "image_width": 1280,
  "image_height": 720,
  "processing_time_ms": 45.2,
  "model_name": "yolov8n.pt",
  "device": "mps"
}
```

## Development

```bash
# Install dev dependencies
uv sync --dev

# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Run tests
uv run pytest
```
