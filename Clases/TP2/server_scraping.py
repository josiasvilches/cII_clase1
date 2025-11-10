#!/usr/bin/env python3
"""
Servidor de Scraping Asíncrono (Parte A)
Servidor HTTP que maneja solicitudes de scraping usando asyncio
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from typing import Dict, Any
from aiohttp import web
import aiohttp

# Importar módulos locales
from scraper.async_http import AsyncHTTPClient
from scraper.html_parser import parse_html, extract_image_urls
from scraper.metadata_extractor import extract_metadata
from common.protocol import (
    create_screenshot_request,
    create_performance_request,
    create_image_processing_request,
    ProtocolMessage,
    MSG_TYPE_RESPONSE,
    MSG_TYPE_ERROR
)


class ScrapingServer:
    """Servidor de scraping asíncrono"""
    
    def __init__(self, processing_host: str = 'localhost', processing_port: int = 9000):
        """
        Inicializa el servidor de scraping
        
        Args:
            processing_host: Host del servidor de procesamiento
            processing_port: Puerto del servidor de procesamiento
        """
        self.processing_host = processing_host
        self.processing_port = processing_port
        self.http_client = None
    
    async def initialize(self):
        """Inicializa recursos asíncronos"""
        self.http_client = AsyncHTTPClient(timeout=30)
        await self.http_client.create_session()
    
    async def cleanup(self):
        """Limpia recursos asíncronos"""
        if self.http_client:
            await self.http_client.close_session()
    
    async def handle_scrape(self, request: web.Request) -> web.Response:
        """
        Maneja peticiones de scraping
        
        Args:
            request: Request de aiohttp
            
        Returns:
            Response JSON con los datos extraídos
        """
        # Obtener URL del query parameter
        url = request.query.get('url')
        
        if not url:
            return web.json_response(
                {'error': 'URL parameter is required'},
                status=400
            )
        
        try:
            # Realizar scraping completo
            result = await self.scrape_url(url)
            
            return web.json_response(result, status=200)
            
        except asyncio.TimeoutError:
            return web.json_response(
                {'error': f'Timeout al acceder a {url}', 'status': 'failed'},
                status=504
            )
        
        except aiohttp.ClientError as e:
            return web.json_response(
                {'error': f'Error de cliente: {str(e)}', 'status': 'failed'},
                status=502
            )
        
        except Exception as e:
            return web.json_response(
                {'error': f'Error interno: {str(e)}', 'status': 'failed'},
                status=500
            )
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Realiza el scraping completo de una URL
        
        Args:
            url: URL a scrapear
            
        Returns:
            Dict con todos los datos extraídos y procesados
        """
        # 1. Obtener HTML de forma asíncrona
        html_content, status_code, headers = await self.http_client.fetch_url(url)
        
        # 2. Parsear HTML y extraer información (I/O no bloqueante)
        scraping_data = await asyncio.to_thread(parse_html, html_content, url)
        
        # 3. Extraer metadatos
        metadata = await asyncio.to_thread(extract_metadata, html_content)
        scraping_data['meta_tags'] = metadata
        
        # 4. Extraer URLs de imágenes
        from bs4 import BeautifulSoup
        soup = await asyncio.to_thread(BeautifulSoup, html_content, 'lxml')
        image_urls = await asyncio.to_thread(extract_image_urls, soup, url, 5)
        
        # 5. Comunicarse con servidor de procesamiento para tareas CPU-bound
        processing_data = await self.request_processing(url, image_urls)
        
        # 6. Construir respuesta consolidada
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'scraping_data': scraping_data,
            'processing_data': processing_data,
            'status': 'success'
        }
        
        return result
    
    async def request_processing(self, url: str, image_urls: list) -> Dict[str, Any]:
        """
        Solicita procesamiento al servidor B de forma asíncrona
        
        Args:
            url: URL de la página
            image_urls: Lista de URLs de imágenes
            
        Returns:
            Dict con datos procesados
        """
        try:
            # Crear tareas para solicitar procesamiento en paralelo
            # Cada tarea abre su propia conexión para evitar conflictos
            tasks = [
                self.request_screenshot(url),
                self.request_performance(url),
                self.request_image_processing(url, image_urls)
            ]
            
            # Ejecutar todas las tareas en paralelo
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Construir resultado
            processing_data = {
                'screenshot': results[0] if not isinstance(results[0], Exception) else None,
                'performance': results[1] if not isinstance(results[1], Exception) else {},
                'thumbnails': results[2] if not isinstance(results[2], Exception) else []
            }
            
            return processing_data
            
        except ConnectionRefusedError:
            print(f"Error: No se pudo conectar al servidor de procesamiento en {self.processing_host}:{self.processing_port}")
            return {
                'screenshot': None,
                'performance': {'error': 'Processing server unavailable'},
                'thumbnails': []
            }
        
        except Exception as e:
            print(f"Error al comunicarse con servidor de procesamiento: {str(e)}")
            return {
                'screenshot': None,
                'performance': {'error': str(e)},
                'thumbnails': []
            }
    
    async def request_screenshot(self, url: str) -> str:
        """Solicita screenshot al servidor de procesamiento"""
        reader, writer = None, None
        try:
            # Abrir conexión dedicada
            reader, writer = await asyncio.open_connection(
                self.processing_host,
                self.processing_port
            )
            
            # Crear y enviar petición
            request = create_screenshot_request(url)
            await request.send_message(writer)
            
            # Recibir respuesta
            response = await ProtocolMessage.receive_message(reader)
            
            if response.msg_type == MSG_TYPE_RESPONSE:
                return response.data.get('screenshot')
            else:
                return None
                
        except Exception as e:
            print(f"Error en request_screenshot: {str(e)}")
            return None
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()
    
    async def request_performance(self, url: str) -> Dict:
        """Solicita análisis de rendimiento al servidor de procesamiento"""
        reader, writer = None, None
        try:
            # Abrir conexión dedicada
            reader, writer = await asyncio.open_connection(
                self.processing_host,
                self.processing_port
            )
            
            request = create_performance_request(url)
            await request.send_message(writer)
            
            response = await ProtocolMessage.receive_message(reader)
            
            if response.msg_type == MSG_TYPE_RESPONSE:
                return response.data.get('performance', {})
            else:
                return {}
                
        except Exception as e:
            print(f"Error en request_performance: {str(e)}")
            return {}
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()
    
    async def request_image_processing(self, url: str, image_urls: list) -> list:
        """Solicita procesamiento de imágenes al servidor de procesamiento"""
        reader, writer = None, None
        try:
            # Abrir conexión dedicada
            reader, writer = await asyncio.open_connection(
                self.processing_host,
                self.processing_port
            )
            
            request = create_image_processing_request(url, image_urls)
            await request.send_message(writer)
            
            response = await ProtocolMessage.receive_message(reader)
            
            if response.msg_type == MSG_TYPE_RESPONSE:
                return response.data.get('thumbnails', [])
            else:
                return []
                
        except Exception as e:
            print(f"Error en request_image_processing: {str(e)}")
            return []
        finally:
            if writer:
                writer.close()
                await writer.wait_closed()
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Endpoint de health check"""
        return web.json_response({'status': 'healthy', 'service': 'scraping-server'})


async def create_app(server: ScrapingServer) -> web.Application:
    """
    Crea la aplicación web
    
    Args:
        server: Instancia del servidor de scraping
        
    Returns:
        Aplicación web configurada
    """
    app = web.Application()
    
    # Registrar rutas
    app.router.add_get('/scrape', server.handle_scrape)
    app.router.add_get('/health', server.handle_health)
    
    # Inicializar y cleanup
    app.on_startup.append(lambda _: server.initialize())
    app.on_cleanup.append(lambda _: server.cleanup())
    
    return app


def parse_arguments():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--ip',
        type=str,
        required=True,
        help='Dirección de escucha (soporta IPv4/IPv6)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=4,
        help='Número de workers (default: 4)'
    )
    
    parser.add_argument(
        '--processing-host',
        type=str,
        default='localhost',
        help='Host del servidor de procesamiento (default: localhost)'
    )
    
    parser.add_argument(
        '--processing-port',
        type=int,
        default=9000,
        help='Puerto del servidor de procesamiento (default: 9000)'
    )
    
    return parser.parse_args()


def main():
    """Función principal"""
    args = parse_arguments()
    
    print("=" * 60)
    print("Servidor de Scraping Web Asíncrono (Parte A)")
    print("=" * 60)
    print(f"Escuchando en: {args.ip}:{args.port}")
    print(f"Workers: {args.workers}")
    print(f"Servidor de procesamiento: {args.processing_host}:{args.processing_port}")
    print("=" * 60)
    print("\nEndpoints disponibles:")
    print("  GET /scrape?url=<URL>  - Realizar scraping de una URL")
    print("  GET /health            - Health check")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    
    # Crear servidor
    server = ScrapingServer(args.processing_host, args.processing_port)
    
    # Ejecutar aplicación
    try:
        app = asyncio.run(create_app(server))
        web.run_app(
            app,
            host=args.ip,
            port=args.port,
            print=None  # Desactivar logs de aiohttp para tener control de output
        )
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario")
        sys.exit(0)


if __name__ == '__main__':
    main()
