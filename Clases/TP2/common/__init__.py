"""
Módulo Común
Contiene funcionalidades compartidas entre servidores
"""

from .protocol import (
    ProtocolMessage,
    create_screenshot_request,
    create_performance_request,
    create_image_processing_request,
    create_response,
    create_error_response,
    MSG_TYPE_SCREENSHOT,
    MSG_TYPE_PERFORMANCE,
    MSG_TYPE_IMAGE_PROCESSING,
    MSG_TYPE_RESPONSE,
    MSG_TYPE_ERROR
)

from .serialization import (
    serialize_json,
    deserialize_json,
    serialize_pickle,
    deserialize_pickle,
    encode_image_base64,
    decode_image_base64
)

__all__ = [
    'ProtocolMessage',
    'create_screenshot_request',
    'create_performance_request',
    'create_image_processing_request',
    'create_response',
    'create_error_response',
    'MSG_TYPE_SCREENSHOT',
    'MSG_TYPE_PERFORMANCE',
    'MSG_TYPE_IMAGE_PROCESSING',
    'MSG_TYPE_RESPONSE',
    'MSG_TYPE_ERROR',
    'serialize_json',
    'deserialize_json',
    'serialize_pickle',
    'deserialize_pickle',
    'encode_image_base64',
    'decode_image_base64'
]
