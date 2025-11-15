import imghdr
import numpy as np
import cv2
from fastapi import UploadFile, HTTPException
from ultralytics.engine.results import Results

from sentinel.config import settings

ALLOWED_IMAGE_TYPES = {"jpeg", "png", "bmp", "webp"}


async def decode_image(file: UploadFile) -> np.ndarray:
    contents = await file.read()

    if len(contents) > settings.api_max_image_size:
        raise HTTPException(
            status_code=400,
            detail=f"Image size exceeds maximum allowed size of {settings.api_max_image_size} bytes",
        )

    image_type = imghdr.what(None, h=contents)
    if image_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Failed to decode image. File may be corrupted.",
        )

    return image


def results_to_detections(results: Results) -> list[dict]:
    detections = []

    if results.boxes is None or len(results.boxes) == 0:
        return detections

    for i in range(len(results.boxes)):
        box = results.boxes.xyxy[i].cpu().numpy()
        conf = float(results.boxes.conf[i].cpu().numpy())
        cls = int(results.boxes.cls[i].cpu().numpy())

        detections.append(
            {
                "x1": float(box[0]),
                "y1": float(box[1]),
                "x2": float(box[2]),
                "y2": float(box[3]),
                "confidence": conf,
                "class_id": cls,
                "class_name": results.names[cls],
            }
        )

    return detections
