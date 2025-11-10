#!/usr/bin/env python3
"""
Módulo de Cliente HTTP Asíncrono
Realiza requests HTTP de forma asíncrona usando aiohttp
"""

import aiohttp
import asyncio
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse


class AsyncHTTPClient:
    """Cliente HTTP asíncrono para scraping"""
    
    def __init__(self, timeout: int = 30, max_redirects: int = 10):
        """
        Inicializa el cliente HTTP asíncrono
        
        Args:
            timeout: Tiempo máximo de espera en segundos
            max_redirects: Número máximo de redirects a seguir
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_redirects = max_redirects
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close_session()
    
    async def create_session(self):
        """Crea una sesión HTTP asíncrona"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=aiohttp.TCPConnector(limit=10),
                headers={'User-Agent': 'Mozilla/5.0 (Web Scraper Bot)'}
            )
    
    async def close_session(self):
        """Cierra la sesión HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
            await asyncio.sleep(0.250)  # Dar tiempo para cerrar conexiones
    
    async def fetch_url(self, url: str) -> Tuple[str, int, Dict]:
        """
        Obtiene el contenido de una URL de forma asíncrona
        
        Args:
            url: URL a consultar
            
        Returns:
            Tuple[str, int, Dict]: (contenido HTML, status code, headers)
            
        Raises:
            aiohttp.ClientError: Si hay error en la petición
            asyncio.TimeoutError: Si se excede el timeout
        """
        if not self.session:
            await self.create_session()
        
        # Validar URL
        if not self._is_valid_url(url):
            raise ValueError(f"URL inválida: {url}")
        
        try:
            async with self.session.get(
                url,
                allow_redirects=True,
                max_redirects=self.max_redirects
            ) as response:
                
                # Verificar tipo de contenido
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    raise ValueError(f"Tipo de contenido no HTML: {content_type}")
                
                # Leer contenido
                html_content = await response.text()
                status_code = response.status
                headers = dict(response.headers)
                
                return html_content, status_code, headers
                
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Timeout al acceder a {url}")
        
        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Error al acceder a {url}: {str(e)}")
    
    async def fetch_multiple_urls(self, urls: list) -> Dict[str, Tuple]:
        """
        Obtiene el contenido de múltiples URLs de forma concurrente
        
        Args:
            urls: Lista de URLs a consultar
            
        Returns:
            Dict: Diccionario con URL como clave y (contenido, status, headers) o error como valor
        """
        if not self.session:
            await self.create_session()
        
        tasks = []
        for url in urls:
            task = self._fetch_with_error_handling(url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Crear diccionario de resultados
        url_results = {}
        for url, result in zip(urls, results):
            url_results[url] = result
        
        return url_results
    
    async def _fetch_with_error_handling(self, url: str) -> Tuple:
        """Wrapper para fetch_url con manejo de errores"""
        try:
            return await self.fetch_url(url)
        except Exception as e:
            return None, 0, {'error': str(e)}
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Valida que la URL sea válida
        
        Args:
            url: URL a validar
            
        Returns:
            bool: True si es válida, False en caso contrario
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False
    
    async def download_binary(self, url: str) -> bytes:
        """
        Descarga contenido binario (ej: imágenes)
        
        Args:
            url: URL del recurso a descargar
            
        Returns:
            bytes: Contenido binario
        """
        if not self.session:
            await self.create_session()
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise aiohttp.ClientError(f"Status {response.status} al descargar {url}")
        
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Timeout al descargar {url}")
        
        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Error al descargar {url}: {str(e)}")


async def fetch_url_simple(url: str, timeout: int = 30) -> str:
    """
    Función auxiliar simple para obtener HTML de una URL
    
    Args:
        url: URL a consultar
        timeout: Timeout en segundos
        
    Returns:
        str: Contenido HTML
    """
    async with AsyncHTTPClient(timeout=timeout) as client:
        html_content, status, headers = await client.fetch_url(url)
        return html_content
