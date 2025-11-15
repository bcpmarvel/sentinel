from fastapi import Request

from sentinel.detection.service import DetectionService


def get_detection_service(request: Request) -> DetectionService:
    return request.app.state.detection_service
