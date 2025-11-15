import time
from fastapi import APIRouter, UploadFile, File, Depends, Request
from starlette.concurrency import run_in_threadpool

from sentinel.api.schemas import DetectionResponse, HealthResponse
from sentinel.api.dependencies import get_detection_service
from sentinel.api.utils import decode_image, results_to_detections
from sentinel.detection.service import DetectionService
from sentinel.logging import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/api")


@router.post("/detect", response_model=DetectionResponse, status_code=200)
async def detect(
    file: UploadFile = File(..., description="Image file to process"),
    service: DetectionService = Depends(get_detection_service),
) -> DetectionResponse:
    try:
        start_time = time.time()

        image = await decode_image(file)
        height, width = image.shape[:2]

        results = await run_in_threadpool(service.process, image)

        detections = results_to_detections(results)

        processing_time = (time.time() - start_time) * 1000

        log.info(
            "detection_complete",
            processing_time_ms=round(processing_time, 2),
            image_width=width,
            image_height=height,
            detection_count=len(detections),
        )

        return DetectionResponse(
            detections=detections,
            image_width=width,
            image_height=height,
            processing_time_ms=processing_time,
            model_name=str(service.detector.model.ckpt_path.name),
            device=service.detector.device,
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error("detection_failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal server error during detection"
        )


@router.get("/health", response_model=HealthResponse, status_code=200)
async def health(request: Request) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        model_loaded=hasattr(request.app.state, "detection_service"),
        device=request.app.state.device,
    )
