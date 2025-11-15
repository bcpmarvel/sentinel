from pydantic import BaseModel, Field


class DetectionBox(BaseModel):
    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    class_id: int = Field(..., description="Class ID")
    class_name: str = Field(..., description="Class name")


class DetectionResponse(BaseModel):
    detections: list[DetectionBox] = Field(..., description="List of detected objects")
    image_width: int = Field(..., description="Input image width")
    image_height: int = Field(..., description="Input image height")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    device: str = Field(..., description="Device used for inference")
