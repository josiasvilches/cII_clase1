"""
Módulo de Procesamiento
Contiene funcionalidades para procesamiento CPU-bound
"""

from .screenshot import capture_screenshot, is_screenshot_available
from .performance import analyze_performance, analyze_performance_detailed
from .image_processor import process_images, process_images_parallel

__all__ = [
    'capture_screenshot',
    'is_screenshot_available',
    'analyze_performance',
    'analyze_performance_detailed',
    'process_images',
    'process_images_parallel'
]
