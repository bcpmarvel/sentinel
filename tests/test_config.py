from pathlib import Path
from sentinel.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.model_path == Path("models/yolov8n.pt")
    assert settings.conf_threshold == 0.5
    assert settings.iou_threshold == 0.45
    assert settings.max_detections == 300
    assert settings.input_size == 640


def test_settings_api_config():
    settings = Settings()
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.api_max_image_size == 10 * 1024 * 1024


def test_settings_logging_config():
    settings = Settings()
    assert settings.log_level == "INFO"
    assert settings.log_format == "console"
