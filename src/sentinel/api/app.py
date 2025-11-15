from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sentinel.config import settings
from sentinel.detection.models import YOLODetector
from sentinel.detection.service import DetectionService
from sentinel.api.routes import router
from sentinel.api.middleware import RequestLoggingMiddleware
from sentinel.logging import configure_logging, get_logger

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(
        "loading_model", model_path=str(settings.model_path), device=settings.device
    )
    detector = YOLODetector(settings.model_path, settings.device)

    app.state.detector = detector
    app.state.detection_service = DetectionService(
        detector=detector,
        enable_tracking=False,
    )
    app.state.device = settings.device

    log.info("model_loaded", device=settings.device)

    yield

    log.info("shutting_down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="CV Detection API",
        description="Object detection and tracking API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    return app


app = create_app()
