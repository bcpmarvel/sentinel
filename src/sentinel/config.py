from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    model_path: Path = Path("models/yolov8n.pt")
    device: str = "mps"
    conf_threshold: float = 0.5
    iou_threshold: float = 0.45
    max_detections: int = 300
    input_size: int = 640

    video_source: str | int = 0
    display_width: int = 1280
    display_height: int = 720

    enable_tracking: bool = False
    tracker_max_age: int = 30
    tracker_min_hits: int = 3
    tracker_iou_threshold: float = 0.3

    enable_analytics: bool = False
    zones_config_path: Path = Path("zones.json")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = ["*"]
    api_max_image_size: int = 10 * 1024 * 1024

    log_level: str = "INFO"
    log_format: str = "console"


settings = Settings()
