#!/usr/bin/env python3
"""
Módulo de Análisis de Rendimiento
Analiza el rendimiento de carga de páginas web
"""

import time
import requests
from typing import Dict, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def analyze_performance(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Analiza el rendimiento de una página web
    
    Args:
        url: URL de la página a analizar
        timeout: Timeout en segundos
        
    Returns:
        Dict con métricas de rendimiento
    """
    performance_data = {
        'load_time_ms': 0,
        'total_size_kb': 0,
        'num_requests': 0,
        'resources': {
            'images': 0,
            'scripts': 0,
            'stylesheets': 0,
            'other': 0
        }
    }
    
    try:
        # Medir tiempo de carga de la página principal
        start_time = time.time()
        
        response = requests.get(
            url,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Web Scraper Bot)'}
        )
        
        load_time = (time.time() - start_time) * 1000  # Convertir a milisegundos
        performance_data['load_time_ms'] = round(load_time, 2)
        
        # Tamaño de la página principal
        html_size = len(response.content)
        performance_data['total_size_kb'] = round(html_size / 1024, 2)
        performance_data['num_requests'] = 1  # Al menos la página principal
        
        # Analizar recursos
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            resource_counts = count_resources(soup)
            performance_data['resources'] = resource_counts
            performance_data['num_requests'] += sum(resource_counts.values())
        
        return performance_data
        
    except requests.Timeout:
        performance_data['error'] = 'Timeout'
        return performance_data
    
    except requests.RequestException as e:
        performance_data['error'] = str(e)
        return performance_data
    
    except Exception as e:
        performance_data['error'] = f'Error inesperado: {str(e)}'
        return performance_data


def count_resources(soup: BeautifulSoup) -> Dict[str, int]:
    """
    Cuenta los recursos externos de la página
    
    Args:
        soup: Objeto BeautifulSoup con el HTML
        
    Returns:
        Dict con conteo de recursos por tipo
    """
    resources = {
        'images': 0,
        'scripts': 0,
        'stylesheets': 0,
        'other': 0
    }
    
    # Contar imágenes
    images = soup.find_all('img', src=True)
    resources['images'] = len(images)
    
    # Contar scripts
    scripts = soup.find_all('script', src=True)
    resources['scripts'] = len(scripts)
    
    # Contar hojas de estilo
    stylesheets = soup.find_all('link', rel='stylesheet')
    resources['stylesheets'] = len(stylesheets)
    
    # Otros recursos (videos, iframes, etc.)
    videos = soup.find_all('video')
    iframes = soup.find_all('iframe')
    resources['other'] = len(videos) + len(iframes)
    
    return resources


def measure_ttfb(url: str, timeout: int = 30) -> float:
    """
    Mide el Time To First Byte (TTFB)
    
    Args:
        url: URL a medir
        timeout: Timeout en segundos
        
    Returns:
        float: TTFB en milisegundos
    """
    try:
        start_time = time.time()
        
        response = requests.get(
            url,
            timeout=timeout,
            stream=True,
            headers={'User-Agent': 'Mozilla/5.0 (Web Scraper Bot)'}
        )
        
        # El tiempo hasta recibir el primer byte
        ttfb = (time.time() - start_time) * 1000
        
        # Cerrar la conexión sin leer todo el contenido
        response.close()
        
        return round(ttfb, 2)
        
    except Exception:
        return 0.0


def estimate_page_weight(soup: BeautifulSoup, base_url: str) -> int:
    """
    Estima el peso total de la página (aproximado)
    
    Args:
        soup: Objeto BeautifulSoup
        base_url: URL base de la página
        
    Returns:
        int: Peso estimado en KB
    """
    # Esta es una estimación aproximada
    # En un análisis real, necesitaríamos descargar todos los recursos
    
    estimated_size = 0
    
    # Tamaño base del HTML
    html_size = len(str(soup))
    estimated_size += html_size
    
    # Estimar tamaño de imágenes (promedio 50KB por imagen)
    images = len(soup.find_all('img'))
    estimated_size += images * 50 * 1024
    
    # Estimar tamaño de scripts (promedio 30KB por script)
    scripts = len(soup.find_all('script', src=True))
    estimated_size += scripts * 30 * 1024
    
    # Estimar tamaño de CSS (promedio 20KB por stylesheet)
    stylesheets = len(soup.find_all('link', rel='stylesheet'))
    estimated_size += stylesheets * 20 * 1024
    
    return round(estimated_size / 1024, 2)  # Retornar en KB


def analyze_performance_detailed(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Análisis de rendimiento más detallado
    
    Args:
        url: URL a analizar
        timeout: Timeout en segundos
        
    Returns:
        Dict con métricas detalladas
    """
    performance = analyze_performance(url, timeout)
    
    # Agregar TTFB
    ttfb = measure_ttfb(url, timeout)
    performance['ttfb_ms'] = ttfb
    
    # Calcular métricas adicionales
    if 'error' not in performance:
        # Tiempo de procesamiento del servidor
        performance['server_processing_ms'] = round(ttfb * 0.7, 2)  # Aproximado
        
        # Tiempo de red
        performance['network_ms'] = round(performance['load_time_ms'] - ttfb, 2)
    
    return performance
