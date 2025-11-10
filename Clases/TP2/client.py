#!/usr/bin/env python3
"""
Cliente de prueba para el sistema de scraping
"""

import requests
import json
import sys
import argparse
import base64
import os
import copy
from datetime import datetime
from urllib.parse import urlparse


def save_screenshot(screenshot_base64: str, url: str, output_dir: str = "screenshots") -> str:
    """
    Guarda un screenshot en disco
    
    Args:
        screenshot_base64: Screenshot codificado en base64
        url: URL de origen
        output_dir: Directorio donde guardar
        
    Returns:
        str: Path del archivo guardado
    """
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Generar nombre de archivo
    domain = urlparse(url).netloc.replace('www.', '').replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{domain}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    # Decodificar y guardar
    screenshot_bytes = base64.b64decode(screenshot_base64)
    
    with open(filepath, 'wb') as f:
        f.write(screenshot_bytes)
    
    return filepath


def scrape_url(server_url: str, target_url: str, save_screenshots: bool = False):
    """
    Realiza una petición de scraping al servidor
    
    Args:
        server_url: URL del servidor de scraping
        target_url: URL a scrapear
    """
    try:
        print(f"Solicitando scraping de: {target_url}")
        print(f"Servidor: {server_url}\n")
        
        # Realizar petición
        response = requests.get(
            f"{server_url}/scrape",
            params={'url': target_url},
            timeout=60
        )
        
        # Verificar respuesta
        if response.status_code == 200:
            data = response.json()

            # Prepare a copy for printing: replace huge base64 screenshot with a placeholder
            printable = copy.deepcopy(data)
            try:
                proc = printable.get('processing_data', {})
                if proc and 'screenshot' in proc and proc['screenshot']:
                    b64 = proc['screenshot']
                    proc['screenshot'] = f"<base64 {len(b64)} chars>"
            except Exception:
                # best-effort: if anything goes wrong, continue without replacing
                pass

            print("=" * 70)
            print("RESPUESTA RECIBIDA")
            print("=" * 70)
            # Print an ordered/pretty JSON for readability
            print(json.dumps(printable, indent=2, ensure_ascii=False, sort_keys=True))
            print("=" * 70)

            # Also save the full JSON (ordered) to disk for later inspection
            try:
                out_dir = 'outputs'
                os.makedirs(out_dir, exist_ok=True)
                domain = urlparse(target_url).netloc.replace('www.', '').replace('.', '_')
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                out_path = os.path.join(out_dir, f"{domain}_{ts}.json")
                with open(out_path, 'w', encoding='utf-8') as jf:
                    json.dump(data, jf, ensure_ascii=False, indent=2, sort_keys=True)
                print(f"   JSON completo guardado en: {out_path}")
            except Exception as e:
                print(f"   Error guardando JSON: {e}")
            
            # Mostrar resumen
            print("\n RESUMEN:")
            print(f"  URL: {data.get('url')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Timestamp: {data.get('timestamp')}")
            
            if 'scraping_data' in data:
                scraping = data['scraping_data']
                print(f"\n  Título: {scraping.get('title')}")
                print(f"  Enlaces encontrados: {len(scraping.get('links', []))}")
                print(f"  Imágenes: {scraping.get('images_count')}")
                
                if 'structure' in scraping:
                    structure = scraping['structure']
                    print(f"  Headers: H1={structure.get('h1', 0)}, H2={structure.get('h2', 0)}, H3={structure.get('h3', 0)}")
            
            if 'processing_data' in data:
                processing = data['processing_data']
                
                if 'performance' in processing:
                    perf = processing['performance']
                    print(f"\n   Rendimiento:")
                    print(f"     Tiempo de carga: {perf.get('load_time_ms', 0)} ms")
                    print(f"     Tamaño total: {perf.get('total_size_kb', 0)} KB")
                    print(f"     Número de requests: {perf.get('num_requests', 0)}")
                
                if 'screenshot' in processing:
                    screenshot = processing['screenshot']
                    if screenshot:
                        print(f"   Screenshot: Capturado ({len(screenshot)} caracteres base64)")
                        
                        # Guardar screenshot si está habilitado
                        if save_screenshots:
                            try:
                                filepath = save_screenshot(screenshot, target_url)
                                print(f"   Screenshot guardado en: {filepath}")
                            except Exception as e:
                                print(f"   Error guardando screenshot: {e}")
                    else:
                        print(f"   Screenshot: No disponible")
                
                if 'thumbnails' in processing:
                    thumbnails = processing['thumbnails']
                    print(f"    Thumbnails: {len(thumbnails)} generados")
            
            print("\n Scraping completado exitosamente!")
            
        else:
            print(f" Error: Status code {response.status_code}")
            print(response.text)
            
    except requests.Timeout:
        print(" Error: Timeout al conectar con el servidor")
        sys.exit(1)
    
    except requests.ConnectionError:
        print(f" Error: No se pudo conectar con el servidor en {server_url}")
        print("   Asegúrate de que el servidor esté corriendo")
        sys.exit(1)
    
    except Exception as e:
        print(f" Error inesperado: {e}")
        sys.exit(1)


def health_check(server_url: str):
    """
    Verifica el estado del servidor
    
    Args:
        server_url: URL del servidor
    """
    try:
        print(f"Verificando estado del servidor: {server_url}")
        
        response = requests.get(f"{server_url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f" Servidor saludable: {data}")
        else:
            print(f"  Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f" Servidor no disponible: {e}")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Cliente de prueba para sistema de scraping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s -s http://localhost:8000 -u https://example.com
  %(prog)s --health
  %(prog)s -s http://localhost:8000 -u https://python.org --save-screenshots
        """
    )
    
    parser.add_argument(
        '-s', '--server',
        type=str,
        default='http://localhost:8000',
        help='URL del servidor de scraping (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '-u', '--url',
        type=str,
        help='URL a scrapear'
    )
    
    parser.add_argument(
        '--health',
        action='store_true',
        help='Verificar estado del servidor'
    )
    
    parser.add_argument(
        '--save-screenshots',
        action='store_true',
        help='Guardar screenshots en disco (directorio screenshots/)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Cliente de Scraping Web")
    print("=" * 70)
    print()
    
    if args.health:
        health_check(args.server)
    elif args.url:
        scrape_url(args.server, args.url, save_screenshots=args.save_screenshots)
    else:
        parser.print_help()
        print("\n  Debes especificar una URL con -u o usar --health")
        sys.exit(1)


if __name__ == '__main__':
    main()
