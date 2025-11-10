#!/usr/bin/env python3
"""
Módulo de Extracción de Metadatos
Extrae meta tags relevantes de páginas HTML
"""

from bs4 import BeautifulSoup
from typing import Dict, Any


def extract_metadata(html_content: str) -> Dict[str, Any]:
    """
    Extrae todos los metadatos relevantes de la página
    
    Args:
        html_content: String con el HTML de la página
        
    Returns:
        Dict con todos los metadatos extraídos
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    metadata = {}
    
    # Meta tags básicos
    metadata.update(extract_basic_meta_tags(soup))
    
    # Open Graph tags
    metadata.update(extract_open_graph_tags(soup))
    
    # Twitter Card tags
    metadata.update(extract_twitter_tags(soup))
    
    return metadata


def extract_basic_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae meta tags básicos (description, keywords, author, etc.)
    
    Args:
        soup: Objeto BeautifulSoup
        
    Returns:
        Dict con meta tags básicos
    """
    basic_meta = {}
    
    # Meta tags comunes
    meta_names = ['description', 'keywords', 'author', 'viewport', 'robots', 'generator']
    
    for name in meta_names:
        meta_tag = soup.find('meta', attrs={'name': name})
        if meta_tag and meta_tag.get('content'):
            basic_meta[name] = meta_tag.get('content')
    
    # Charset
    charset_tag = soup.find('meta', attrs={'charset': True})
    if charset_tag:
        basic_meta['charset'] = charset_tag.get('charset')
    
    return basic_meta


def extract_open_graph_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae Open Graph meta tags
    
    Args:
        soup: Objeto BeautifulSoup
        
    Returns:
        Dict con Open Graph tags (con prefijo og:)
    """
    og_tags = {}
    
    # Buscar todos los meta tags con property que empiece con "og:"
    og_meta_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
    
    for tag in og_meta_tags:
        property_name = tag.get('property')
        content = tag.get('content')
        
        if property_name and content:
            og_tags[property_name] = content
    
    return og_tags


def extract_twitter_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae Twitter Card meta tags
    
    Args:
        soup: Objeto BeautifulSoup
        
    Returns:
        Dict con Twitter Card tags (con prefijo twitter:)
    """
    twitter_tags = {}
    
    # Buscar todos los meta tags con name que empiece con "twitter:"
    twitter_meta_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
    
    for tag in twitter_meta_tags:
        name = tag.get('name')
        content = tag.get('content')
        
        if name and content:
            twitter_tags[name] = content
    
    return twitter_tags


def extract_json_ld(soup: BeautifulSoup) -> list:
    """
    Extrae datos estructurados JSON-LD
    
    Args:
        soup: Objeto BeautifulSoup
        
    Returns:
        List con objetos JSON-LD encontrados
    """
    import json
    
    json_ld_data = []
    
    # Buscar scripts con type="application/ld+json"
    json_ld_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
    
    for script in json_ld_scripts:
        try:
            if script.string:
                data = json.loads(script.string)
                json_ld_data.append(data)
        except json.JSONDecodeError:
            # Ignorar JSON mal formado
            continue
    
    return json_ld_data


def get_favicon_url(soup: BeautifulSoup, base_url: str) -> str:
    """
    Extrae la URL del favicon
    
    Args:
        soup: Objeto BeautifulSoup
        base_url: URL base para resolver URLs relativas
        
    Returns:
        str: URL del favicon o string vacío
    """
    from urllib.parse import urljoin
    
    # Buscar link con rel="icon" o rel="shortcut icon"
    icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
    
    if icon_link and icon_link.get('href'):
        return urljoin(base_url, icon_link.get('href'))
    
    # Favicon por defecto
    return urljoin(base_url, '/favicon.ico')


def extract_canonical_url(soup: BeautifulSoup) -> str:
    """
    Extrae la URL canónica de la página
    
    Args:
        soup: Objeto BeautifulSoup
        
    Returns:
        str: URL canónica o string vacío
    """
    canonical_link = soup.find('link', rel='canonical')
    
    if canonical_link and canonical_link.get('href'):
        return canonical_link.get('href')
    
    return ""
