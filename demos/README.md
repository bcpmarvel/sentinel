# Sentinel Demos

This directory contains sample inputs and scripts to demonstrate Sentinel's object detection and tracking capabilities.

## Directory Structure

```
demos/
├── inputs/          # Sample input data (committed to git)
│   ├── images/     # Sample images for testing
│   └── videos/     # Sample videos for testing
├── outputs/        # Generated outputs (gitignored)
│   ├── images/     # Annotated images
│   └── videos/     # Annotated videos
└── README.md       # This file
```

## Quick Start

### Single Image Detection

Process a single image with object detection:

```bash
uv run python -m sentinel.cli detect-image \
  demos/inputs/images/parking1.jpg \
  --output demos/outputs/images/parking1_annotated.jpg \
  --conf 0.5
```

### Batch Image Processing

Process all images in a directory:

```bash
uv run python -m sentinel.cli detect-image \
  demos/inputs/images \
  --output demos/outputs/images \
  --no-display \
  --conf 0.5
```

### Video Detection (Webcam)

Real-time detection from webcam:

```bash
uv run python -m sentinel.cli detect-video \
  --source 0 \
  --conf 0.5
```

### Video Detection (File)

Process a video file:

```bash
uv run python -m sentinel.cli detect-video \
  --source demos/inputs/videos/sample.mp4 \
  --conf 0.5
```

### Video with Tracking

Enable multi-object tracking:

```bash
uv run python -m sentinel.cli detect-video \
  --source 0 \
  --track \
  --conf 0.5
```

### Video with Zone Analytics

Track objects and analyze zones:

```bash
uv run python -m sentinel.cli detect-video \
  --source 0 \
  --track \
  --analytics \
  --zones zones.json
```

## Command Reference

### detect-image

Detect objects in single image or batch process directory.

**Options:**
- `--output, -o` - Output path for annotated image/directory
- `--conf, -c` - Confidence threshold (0.0-1.0, default: 0.5)
- `--device, -d` - Device for inference (mps|cuda|cpu, default: mps)
- `--model, -m` - Path to custom YOLO model
- `--track, -t` - Enable tracking (for sequential images)
- `--no-display` - Don't show window, save only
- `--quiet, -q` - Suppress console output

**Examples:**

```bash
# High confidence threshold
uv run python -m sentinel.cli detect-image \
  demos/inputs/images/pedestrian1.jpg \
  --output demos/outputs/images/pedestrian1.jpg \
  --conf 0.7

# CPU mode (no GPU)
uv run python -m sentinel.cli detect-image \
  demos/inputs/images/traffic.jpg \
  --output demos/outputs/images/traffic.jpg \
  --device cpu

# Batch process quietly
uv run python -m sentinel.cli detect-image \
  demos/inputs/images \
  --output demos/outputs/images \
  --no-display \
  --quiet
```

### detect-video

Detect and track objects in video or webcam feed.

**Options:**
- `--source, -s` - Video source (webcam index or file path, default: 0)
- `--conf, -c` - Confidence threshold (0.0-1.0, default: 0.5)
- `--device, -d` - Device for inference (mps|cuda|cpu, default: mps)
- `--model, -m` - Path to custom YOLO model
- `--track, -t` - Enable multi-object tracking
- `--analytics, -a` - Enable zone analytics (requires --track)
- `--zones, -z` - Path to zones JSON configuration
- `--quiet, -q` - Suppress console output

**Examples:**

```bash
# External webcam
uv run python -m sentinel.cli detect-video --source 1

# Video file with tracking
uv run python -m sentinel.cli detect-video \
  --source demos/inputs/videos/sample.mp4 \
  --track

# Full analytics pipeline
uv run python -m sentinel.cli detect-video \
  --source demos/inputs/videos/sample.mp4 \
  --track \
  --analytics \
  --zones zones.json \
  --conf 0.6
```

## Sample Images

The `demos/inputs/images/` directory includes:

- **parking1-4.jpg** - Parking lot scenes with vehicles
- **pedestrian1-2.jpg** - Street scenes with pedestrians
- **traffic.jpg** - Traffic intersection with multiple vehicles

These images are suitable for testing:
- Vehicle detection
- Person detection
- Multi-object scenes
- Various lighting conditions
- Different image resolutions

## YOLO Models

Sentinel uses **YOLO11** (Ultralytics, October 2024) - the latest generation of YOLO models with improved accuracy and performance.

**Available models** (auto-downloaded on first use):

| Model | Size | Parameters | Speed | mAP | Use Case |
|-------|------|------------|-------|-----|----------|
| yolo11n.pt | 5 MB | 2.6M | Fastest | 39.5 | Edge devices, real-time |
| yolo11s.pt | 20 MB | 9.4M | Very Fast | 47.0 | Balanced performance |
| **yolo11m.pt** | 40 MB | 20.1M | Fast | **51.5** | **Default - Best balance** |
| yolo11l.pt | 50 MB | 25.3M | Moderate | 53.4 | High accuracy |
| yolo11x.pt | 110 MB | 56.9M | Slowest | 54.7 | Maximum accuracy |

**To use a different model:**

```bash
uv run python -m sentinel.cli detect-image \
  demos/inputs/images/traffic.jpg \
  --output output.jpg \
  --model yolo11x.pt
```

Models are automatically downloaded to the project directory on first use and cached for future runs.

## Tips

### Performance

- Use `--device mps` on Apple Silicon for best performance
- Use `--device cuda` on NVIDIA GPUs
- Use `--device cpu` as fallback (slower)

### Confidence Threshold

- **0.3-0.4**: More detections, more false positives
- **0.5**: Balanced (default)
- **0.6-0.7**: Fewer detections, higher precision
- **0.8+**: Only very confident detections

### Output Management

All outputs are saved to `demos/outputs/` which is gitignored. This keeps the repository clean while allowing you to generate and inspect results locally.

To clean up outputs:

```bash
rm -rf demos/outputs/*
```

## Adding Your Own Samples

### Images

Place your test images in `demos/inputs/images/`:

```bash
cp /path/to/your/image.jpg demos/inputs/images/
```

### Videos

Place your test videos in `demos/inputs/videos/`:

```bash
cp /path/to/your/video.mp4 demos/inputs/videos/
```

Note: Videos are gitignored by default due to file size. Consider using short clips (5-10 seconds) for demos.

## Troubleshooting

### Model Not Found

Models are automatically downloaded on first use. If you see download issues, check your internet connection or try manually specifying a model:

```bash
--model yolo11n.pt  # Smaller, downloads faster
```

### GPU/MPS Not Available

If MPS/CUDA fails, the system will automatically fall back to CPU. To force CPU mode:

```bash
--device cpu
```

### Image Format Not Supported

Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`

Convert unsupported formats:

```bash
convert image.tiff image.jpg
```

## Next Steps

- Explore the [main README](../README.md) for full documentation
- Try different YOLO models (yolov8s, yolov8m, yolov8l)
- Create custom zone configurations for analytics
- Integrate with your own video sources
