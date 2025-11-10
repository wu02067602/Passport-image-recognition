"""
護照辨識系統

此套件提供護照影像辨識功能，使用 Gemini API 進行 OCR 和資訊擷取。
"""

from .models.image_recognizer import ImageRecognizer, ImageSizeError, ImageNotFoundError
from .parsers.response_parser import ResponseParser, PassportInfo
from .controllers.passport_recognition_controller import PassportRecognitionController

__all__ = [
    'ImageRecognizer',
    'ImageSizeError',
    'ImageNotFoundError',
    'ResponseParser',
    'PassportInfo',
    'PassportRecognitionController'
]

__version__ = '0.1.0'
