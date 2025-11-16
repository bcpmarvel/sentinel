from unittest.mock import Mock, MagicMock
import numpy as np
import pytest

from sentinel.detection.service import DetectionService
from sentinel.detection.models import YOLODetector


@pytest.fixture
def mock_detector():
    detector = Mock(spec=YOLODetector)
    detector.device = "cpu"
    detector.model_path = "models/yolov8n.pt"
    return detector


@pytest.fixture
def detection_service(mock_detector):
    return DetectionService(detector=mock_detector, enable_tracking=False)


def test_detection_service_initialization(detection_service, mock_detector):
    assert detection_service.detector == mock_detector
    assert detection_service.enable_tracking is False
    assert detection_service.conf_threshold == 0.5
    assert detection_service.iou_threshold == 0.45


def test_detection_service_process(detection_service, mock_detector):
    mock_result = MagicMock()
    mock_detector.predict.return_value = mock_result

    test_frame = np.zeros((640, 640, 3), dtype=np.uint8)
    result = detection_service.process(test_frame)

    assert result == mock_result
    mock_detector.predict.assert_called_once()


def test_detection_service_with_tracking(mock_detector):
    service = DetectionService(detector=mock_detector, enable_tracking=True)
    mock_result = MagicMock()
    mock_detector.track.return_value = mock_result

    test_frame = np.zeros((640, 640, 3), dtype=np.uint8)
    result = service.process(test_frame)

    assert result == mock_result
    mock_detector.track.assert_called_once()
