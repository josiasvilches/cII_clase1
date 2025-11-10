#!/usr/bin/env python3
"""
Módulo de Protocolo de Comunicación
Define el protocolo de comunicación entre servidor A (asyncio) y servidor B (multiprocessing)
"""

import struct
from typing import Dict, Any
from .serialization import serialize_json, deserialize_json


# Tipos de mensajes
MSG_TYPE_SCREENSHOT = 1
MSG_TYPE_PERFORMANCE = 2
MSG_TYPE_IMAGE_PROCESSING = 3
MSG_TYPE_RESPONSE = 100
MSG_TYPE_ERROR = 255


class ProtocolMessage:
    """Clase para manejar mensajes del protocolo"""
    
    def __init__(self, msg_type: int, data: Dict[str, Any]):
        self.msg_type = msg_type
        self.data = data
    
    def encode(self) -> bytes:
        """
        Codifica el mensaje en bytes para enviar por socket
        Formato: [4 bytes longitud][1 byte tipo][N bytes datos JSON]
        
        Returns:
            bytes: Mensaje codificado
        """
        # Serializar datos
        data_bytes = serialize_json(self.data)
        
        # Calcular longitud total (tipo + datos)
        total_length = 1 + len(data_bytes)
        
        # Crear header: longitud (4 bytes) + tipo (1 byte)
        header = struct.pack('!IB', total_length, self.msg_type)
        
        # Retornar header + datos
        return header + data_bytes
    
    @staticmethod
    def decode(data: bytes) -> 'ProtocolMessage':
        """
        Decodifica bytes a un mensaje del protocolo
        
        Args:
            data: Bytes con el mensaje completo
            
        Returns:
            ProtocolMessage: Mensaje decodificado
        """
        # Extraer header (5 bytes: 4 de longitud + 1 de tipo)
        length, msg_type = struct.unpack('!IB', data[:5])
        
        # Extraer datos JSON
        json_data = data[5:]
        message_data = deserialize_json(json_data)
        
        return ProtocolMessage(msg_type, message_data)
    
    @staticmethod
    async def receive_message(reader) -> 'ProtocolMessage':
        """
        Recibe un mensaje completo desde un StreamReader asíncrono
        
        Args:
            reader: asyncio.StreamReader
            
        Returns:
            ProtocolMessage: Mensaje recibido
        """
        # Leer header (4 bytes de longitud + 1 byte de tipo)
        header = await reader.readexactly(5)
        length, msg_type = struct.unpack('!IB', header)
        
        # Leer datos (length ya incluye el byte del tipo, por eso restamos 1)
        data_bytes = await reader.readexactly(length - 1)
        message_data = deserialize_json(data_bytes)
        
        return ProtocolMessage(msg_type, message_data)
    
    async def send_message(self, writer):
        """
        Envía el mensaje a través de un StreamWriter asíncrono
        
        Args:
            writer: asyncio.StreamWriter
        """
        encoded = self.encode()
        writer.write(encoded)
        await writer.drain()


def create_screenshot_request(url: str, task_id: str = None) -> ProtocolMessage:
    """Crea una solicitud de screenshot"""
    return ProtocolMessage(MSG_TYPE_SCREENSHOT, {
        'url': url,
        'task_id': task_id
    })


def create_performance_request(url: str, task_id: str = None) -> ProtocolMessage:
    """Crea una solicitud de análisis de rendimiento"""
    return ProtocolMessage(MSG_TYPE_PERFORMANCE, {
        'url': url,
        'task_id': task_id
    })


def create_image_processing_request(url: str, images: list, task_id: str = None) -> ProtocolMessage:
    """Crea una solicitud de procesamiento de imágenes"""
    return ProtocolMessage(MSG_TYPE_IMAGE_PROCESSING, {
        'url': url,
        'images': images,
        'task_id': task_id
    })


def create_response(data: Dict[str, Any], task_id: str = None) -> ProtocolMessage:
    """Crea una respuesta exitosa"""
    response_data = data.copy()
    if task_id:
        response_data['task_id'] = task_id
    return ProtocolMessage(MSG_TYPE_RESPONSE, response_data)


def create_error_response(error: str, task_id: str = None) -> ProtocolMessage:
    """Crea una respuesta de error"""
    return ProtocolMessage(MSG_TYPE_ERROR, {
        'error': error,
        'task_id': task_id
    })
