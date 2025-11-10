#!/usr/bin/env python3
"""
Módulo de Parsing HTML
Extrae información de páginas HTML usando BeautifulSoup
"""

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any
import re


def parse_html(html_content: str, base_url: str) -> Dict[str, Any]:
    """
    Parsea el contenido HTML y extrae toda la información relevante
    
    Args:
        html_content: String con el HTML de la página
        base_url: URL base para resolver enlaces relativos
        
    Returns:
        Dict con toda la información extraída
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    return {
        'title': extract_title(soup),
        'links': extract_links(soup, base_url),
        'images_count': count_images(soup),
        'structure': extract_structure(soup)
    }


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extrae el título de la página
    
    Args:
        soup: Objeto BeautifulSoup
        
    Returns:
        str: Título de la página o string vacío si no se encuentra
    """
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text(strip=True)
    
    # Intentar con h1 si no hay title tag
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text(strip=True)
    
    return ""


def extract_links(soup: BeautifulSoup, base_url: str, limit: int = 100) -> List[str]:
    """
    Extrae todos los enlaces de la página
    
    Args:
        soup: Objeto BeautifulSoup
        base_url: URL base para resolver enlaces relativos
        limit: Número máximo de enlaces a extraer
        
    Returns:
        List[str]: Lista de URLs encontradas
    """
    links = []
    seen = set()
    
    for link_tag in soup.find_all('a', href=True):
        href = link_tag['href']
        
        # Resolver URL relativa a absoluta
        absolute_url = urljoin(base_url, href)
        
        # Filtrar enlaces válidos (http/https)
        if absolute_url.startswith(('http://', 'https://')) and absolute_url not in seen:
            links.append(absolute_url)
            seen.add(absolute_url)
            
            if len(links) >= limit:
                break
    
    return links


def count_images(soup: BeautifulSoup) -> int:
    """
    Cuenta el número de imágenes en la página
    
    Args:
        soup: Objeto BeautifulSoup
        
    Returns:
        int: Cantidad de imágenes
    """
    # Contar tags <img>
    img_tags = len(soup.find_all('img'))
    
    # Contar imágenes en CSS background (aproximado)
    style_tags = soup.find_all('style')
    css_images = 0
    for style in style_tags:
        css_content = style.string or ''
        css_images += len(re.findall(r'url\(["\']?[^")\']+\.(jpg|jpeg|png|gif|webp|svg)', css_content, re.I))
    
    return img_tags + css_images


def extract_structure(soup: BeautifulSoup) -> Dict[str, int]:
    """
    Extrae la estructura de headers (H1-H6) de la página
    
    Args:
        soup: Objeto BeautifulSoup
        
    Returns:
        Dict: Cantidad de cada tipo de header
    """
    structure = {}
    
    for i in range(1, 7):
        header_tag = f'h{i}'
        count = len(soup.find_all(header_tag))
        structure[header_tag] = count
    
    return structure


def extract_image_urls(soup: BeautifulSoup, base_url: str, limit: int = 10) -> List[str]:
    """
    Extrae URLs de las imágenes principales de la página
    
    Args:
        soup: Objeto BeautifulSoup
        base_url: URL base para resolver URLs relativas
        limit: Número máximo de imágenes a extraer
        
    Returns:
        List[str]: Lista de URLs de imágenes
    """
    images = []
    seen = set()
    
    for img_tag in soup.find_all('img', src=True):
        src = img_tag.get('src', '')
        
        # Resolver URL relativa
        absolute_url = urljoin(base_url, src)
        
        # Filtrar imágenes válidas
        if absolute_url.startswith(('http://', 'https://')) and absolute_url not in seen:
            # Filtrar por extensión de imagen común
            if re.search(r'\.(jpg|jpeg|png|gif|webp)($|\?)', absolute_url, re.I):
                images.append(absolute_url)
                seen.add(absolute_url)
                
                if len(images) >= limit:
                    break
    
    return images


def get_text_content(soup: BeautifulSoup, max_length: int = 1000) -> str:
    """
    Extrae el texto visible de la página
    
    Args:
        soup: Objeto BeautifulSoup
        max_length: Longitud máxima del texto
        
    Returns:
        str: Texto de la página
    """
    # Remover scripts y estilos
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Obtener texto
    text = soup.get_text(separator=' ', strip=True)
    
    # Limpiar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    # Limitar longitud
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text
