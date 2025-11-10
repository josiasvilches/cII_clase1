"""
Módulo de Scraping
Contiene funcionalidades para scraping web asíncrono
"""

from .async_http import AsyncHTTPClient, fetch_url_simple
from .html_parser import parse_html, extract_links, extract_image_urls
from .metadata_extractor import extract_metadata

__all__ = [
    'AsyncHTTPClient',
    'fetch_url_simple',
    'parse_html',
    'extract_links',
    'extract_image_urls',
    'extract_metadata'
]
