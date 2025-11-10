#!/usr/bin/env python3
"""
Módulo de Procesamiento de Imágenes
Descarga imágenes y genera thumbnails optimizados
"""

import io
import base64
import requests
from typing import List, Optional, Tuple
from PIL import Image, ImageOps


def download_image(url: str, timeout: int = 10) -> Optional[bytes]:
    """
    Descarga una imagen desde una URL
    
    Args:
        url: URL de la imagen
        timeout: Timeout en segundos
        
    Returns:
        bytes: Bytes de la imagen o None si falla
    """
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Web Scraper Bot)'},
            stream=True
        )
        
        if response.status_code == 200:
            # Verificar que sea una imagen
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type:
                return response.content
        
        return None
        
    except Exception as e:
        print(f"Error descargando imagen {url}: {str(e)}")
        return None


def create_thumbnail(image_bytes: bytes, size: Tuple[int, int] = (150, 150)) -> Optional[str]:
    """
    Crea un thumbnail de una imagen
    
    Args:
        image_bytes: Bytes de la imagen original
        size: Tamaño del thumbnail (ancho, alto)
        
    Returns:
        str: Thumbnail codificado en base64 o None si falla
    """
    try:
        # Abrir imagen desde bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convertir a RGB si es necesario (para PNGs con transparencia)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Crear thumbnail manteniendo proporción
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Guardar en buffer
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85, optimize=True)
        buffer.seek(0)
        
        # Codificar en base64
        thumbnail_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return thumbnail_base64
        
    except Exception as e:
        print(f"Error creando thumbnail: {str(e)}")
        return None


def process_images(image_urls: List[str], max_images: int = 5) -> List[str]:
    """
    Descarga imágenes y genera thumbnails
    
    Args:
        image_urls: Lista de URLs de imágenes
        max_images: Número máximo de imágenes a procesar
        
    Returns:
        List[str]: Lista de thumbnails en base64
    """
    thumbnails = []
    
    # Limitar número de imágenes
    urls_to_process = image_urls[:max_images]
    
    for url in urls_to_process:
        # Descargar imagen
        image_bytes = download_image(url)
        
        if image_bytes:
            # Crear thumbnail
            thumbnail = create_thumbnail(image_bytes)
            
            if thumbnail:
                thumbnails.append(thumbnail)
    
    return thumbnails


def optimize_image(image_bytes: bytes, max_size: int = 800, quality: int = 85) -> Optional[bytes]:
    """
    Optimiza una imagen reduciendo su tamaño
    
    Args:
        image_bytes: Bytes de la imagen original
        max_size: Tamaño máximo del lado más largo
        quality: Calidad de compresión (1-100)
        
    Returns:
        bytes: Imagen optimizada o None si falla
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # Redimensionar si es muy grande
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convertir a RGB si es necesario
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Guardar optimizada
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error optimizando imagen: {str(e)}")
        return None


def get_image_info(image_bytes: bytes) -> dict:
    """
    Obtiene información sobre una imagen
    
    Args:
        image_bytes: Bytes de la imagen
        
    Returns:
        dict: Información de la imagen (formato, tamaño, dimensiones)
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        return {
            'format': image.format,
            'mode': image.mode,
            'width': image.width,
            'height': image.height,
            'size_bytes': len(image_bytes)
        }
        
    except Exception as e:
        return {'error': str(e)}


def create_multiple_thumbnails(image_bytes: bytes, sizes: List[Tuple[int, int]]) -> List[Optional[str]]:
    """
    Crea múltiples thumbnails de diferentes tamaños
    
    Args:
        image_bytes: Bytes de la imagen original
        sizes: Lista de tuplas (ancho, alto) para los thumbnails
        
    Returns:
        List: Lista de thumbnails en base64
    """
    thumbnails = []
    
    for size in sizes:
        thumbnail = create_thumbnail(image_bytes, size)
        thumbnails.append(thumbnail)
    
    return thumbnails


def process_images_parallel(image_urls: List[str], max_images: int = 5) -> dict:
    """
    Procesa múltiples imágenes y retorna información detallada
    
    Args:
        image_urls: Lista de URLs de imágenes
        max_images: Número máximo de imágenes
        
    Returns:
        dict: Diccionario con thumbnails e información
    """
    result = {
        'thumbnails': [],
        'processed_count': 0,
        'failed_count': 0
    }
    
    urls_to_process = image_urls[:max_images]
    
    for url in urls_to_process:
        image_bytes = download_image(url)
        
        if image_bytes:
            thumbnail = create_thumbnail(image_bytes)
            if thumbnail:
                result['thumbnails'].append(thumbnail)
                result['processed_count'] += 1
            else:
                result['failed_count'] += 1
        else:
            result['failed_count'] += 1
    
    return result
