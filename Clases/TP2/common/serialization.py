#!/usr/bin/env python3
"""
Módulo de Serialización
Maneja la serialización y deserialización de datos para comunicación entre servidores
"""

import json
import pickle
import base64
from typing import Any, Dict


def serialize_json(data: Dict[str, Any]) -> bytes:
    """
    Serializa datos a JSON y los convierte a bytes
    
    Args:
        data: Diccionario con datos a serializar
        
    Returns:
        bytes: Datos serializados
    """
    json_str = json.dumps(data, ensure_ascii=False)
    return json_str.encode('utf-8')


def deserialize_json(data: bytes) -> Dict[str, Any]:
    """
    Deserializa bytes a diccionario desde JSON
    
    Args:
        data: Bytes con datos serializados
        
    Returns:
        Dict: Datos deserializados
    """
    json_str = data.decode('utf-8')
    return json.loads(json_str)


def serialize_pickle(data: Any) -> bytes:
    """
    Serializa datos usando pickle
    
    Args:
        data: Objeto a serializar
        
    Returns:
        bytes: Datos serializados
    """
    return pickle.dumps(data)


def deserialize_pickle(data: bytes) -> Any:
    """
    Deserializa datos usando pickle
    
    Args:
        data: Bytes con datos serializados
        
    Returns:
        Any: Objeto deserializado
    """
    return pickle.loads(data)


def encode_image_base64(image_bytes: bytes) -> str:
    """
    Codifica una imagen en base64 para enviarla en JSON
    
    Args:
        image_bytes: Bytes de la imagen
        
    Returns:
        str: Imagen codificada en base64
    """
    return base64.b64encode(image_bytes).decode('utf-8')


def decode_image_base64(base64_str: str) -> bytes:
    """
    Decodifica una imagen desde base64
    
    Args:
        base64_str: String con imagen en base64
        
    Returns:
        bytes: Bytes de la imagen
    """
    return base64.b64decode(base64_str.encode('utf-8'))
