# TP2 - Sistema de Scraping y Análisis Web Distribuido

Sistema distribuido en Python que realiza scraping y análisis web utilizando **asyncio** y **multiprocessing**.

## Autor
Josías Vilches  
Fecha: 23 de octubre de 2025

---

## Descripción

El sistema consta de dos servidores que trabajan coordinadamente:

- **Servidor A (AsyncIO)**: Servidor HTTP asíncrono que maneja peticiones de scraping
- **Servidor B (Multiprocessing)**: Servidor que procesa tareas CPU-bound en paralelo

### Arquitectura

```
Cliente HTTP
     
     → Servidor A (AsyncIO) 
              ↓                       
         Scraping HTML                
         Extracción de datos          
                                     
              → Socket ←
                                     
              → Servidor B         
                 (Multiprocessing)    
                                     
                        Screenshot  
                        Performance 
                        Images      
                                     
                   Pool de Procesos   
                                     
     ← Respuesta consolidada ←
```

---

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Opcional: pre-descargar drivers (reduce latencia en el primer arranque de Selenium):

```bash
python3 predownload_drivers.py
```

### 2. Notas sobre navegadores/Drivers para screenshots

Selenium requiere que exista un navegador instalado (Chrome/Chromium o Firefox).
Este proyecto incluye `webdriver-manager` en `requirements.txt` para descargar
automáticamente el driver (ChromeDriver) en tiempo de ejecución. Aun así, debe
haber un navegador disponible en el sistema.

En Debian/Ubuntu puede instalar Chromium con:

```bash
sudo apt-get update && sudo apt-get install -y chromium-browser
```

Si prefiere manejar drivers manualmente, instale el driver correspondiente y
asegúrese de que esté en PATH.

Nota importante sobre el backend de screenshots
- El sistema usa actualmente Selenium para generar screenshots. El código intenta
   usar el binario de Chrome/Chromium del sistema cuando está disponible, y
   recurre a `webdriver-manager` o a Selenium Manager para descargar el driver
   automáticamente si hace falta.
- Variables de entorno útiles:
   - `BROWSER`: `chrome` o `firefox` (por defecto el código detecta automáticamente)
   - `CHROME_BIN`: ruta al binario de Chrome/Chromium si no está en PATH
   - `BROWSER_START_TIMEOUT`: segundos a esperar para que el navegador arranque (default: 60)
- Si tiene problemas con drivers o versiones (ej. mismatch entre Chromium y
   ChromeDriver), puede usar `predownload_drivers.py` (script incluido) para
   forzar la descarga previa de drivers antes de ejecutar los servidores.

Problemas frecuentes en entornos con Snap
- En algunas distribuciones (Ubuntu) Chromium/Firefox instalados vía `snap`
   pueden tener restricciones (sandbox/profiles) que impidan que Selenium
   levante una sesión correctamente (errores como "DevToolsActivePort file
   doesn't exist" o perfiles bloqueados). Si esto ocurre y no puede solucionarlo
   fácilmente, la opción recomendable es instalar Google Chrome/Chromium desde
   el paquete deb oficial o usar una imagen de contenedor que incluya Chrome.
---

## Uso

### Iniciar Servidor de Procesamiento (Parte B)

Primero iniciar el servidor de procesamiento:

```bash
python3 server_processing.py -i localhost -p 9000
```

**Opciones:**
- `-i, --ip`: Dirección IP de escucha (requerido)
- `-p, --port`: Puerto de escucha (requerido)
- `-n, --processes`: Número de procesos en el pool (opcional, default: CPU count)

**Ejemplo con más procesos:**
```bash
python3 server_processing.py -i localhost -p 9000 -n 8
```

### Iniciar Servidor de Scraping (Parte A)

Luego iniciar el servidor principal:

```bash
python3 server_scraping.py -i localhost -p 8000
```

**Opciones:**
- `-i, --ip`: Dirección IP de escucha (requerido)
- `-p, --port`: Puerto de escucha (requerido)
- `-w, --workers`: Número de workers (opcional, default: 4)
- `--processing-host`: Host del servidor B (opcional, default: localhost)
- `--processing-port`: Puerto del servidor B (opcional, default: 9000)

**Ejemplo con configuración personalizada:**
```bash
python3 server_scraping.py -i 0.0.0.0 -p 8000 -w 8 --processing-host localhost --processing-port 9000
```

### Realizar Peticiones

Una vez ambos servidores estén corriendo:

#### Con curl:
```bash
# Scraping básico
curl "http://localhost:8000/scrape?url=https://example.com" | jq

# Health check
curl "http://localhost:8000/health"
```

#### Con el cliente de prueba:
```bash
# Scraping básico (screenshot solo en JSON, no se guarda)
python3 client.py -u https://example.com

# Scraping guardando screenshots en disco
python3 client.py -u https://example.com --save-screenshots

# Health check
python3 client.py --health

# Con servidor personalizado
python3 client.py -s http://localhost:8000 -u https://python.org --save-screenshots
```

**Ubicación de screenshots:**
- Los screenshots se guardan en: `screenshots/<dominio>_<timestamp>.png`
- Ejemplo: `screenshots/example_com_20251023_150430.png`
- El directorio se crea automáticamente si no existe

### Salida del cliente y JSON completo

El cliente `client.py` ahora imprime una versión legible y ordenada del JSON
recibido y además guarda el JSON completo (incluyendo la cadena base64 del
screenshot) en `outputs/` con nombre ` <dominio>_<timestamp>.json`.

- En consola verás un JSON ordenado (claves en orden alfabético) donde el
   campo `processing_data.screenshot` se sustituye por un placeholder del tipo
   `"<base64 N chars>"` para evitar volcar la imagen entera en la terminal.
- Si usas `--save-screenshots`, además se guardará la imagen real en
   `screenshots/` y el cliente imprimirá la ruta del archivo guardado.
- El JSON completo se guarda para inspección posterior; esto facilita subir
   resultados o revisarlos sin perder los datos binarios en la terminal.

Ejemplo de ejecución:

```bash
python3 client.py -s http://localhost:8000 -u https://python.org --save-screenshots
```

Salida esperada (resumida):

- JSON ordenado impreso en consola (screenshot reemplazado por placeholder)
- Mensaje: `JSON completo guardado en: outputs/python_org_YYYYMMDD_HHMMSS.json`
- Mensaje: `Screenshot guardado en: screenshots/python_org_YYYYMMDD_HHMMSS.png`

#### Con navegador:
- Abrir: `http://localhost:8000/scrape?url=https://example.com`

---

## Estructura del Proyecto

```
TP2/
 server_scraping.py          # Servidor asyncio (Parte A)
 server_processing.py        # Servidor multiprocessing (Parte B)
 client.py                   # Cliente de prueba
 outputs/                    # JSON completos de ejecuciones (incluye base64)
 screenshots/                # PNG generados por --save-screenshots
 scraper/
    __init__.py
    html_parser.py          # Parsing HTML y extracción
    metadata_extractor.py  # Metadatos y Open Graph
    async_http.py           # Cliente HTTP asíncrono
 processor/
    __init__.py
   screenshot.py           # Capturas con Selenium
    performance.py          # Análisis de rendimiento
    image_processor.py      # Thumbnails con PIL
 common/
    __init__.py
    protocol.py             # Protocolo de comunicación
    serialization.py        # Serialización de datos
 tests/
    test_scraper.py
    test_processor.py
    test_screenshot.py
 requirements.txt
 README.md
```

---

## Funcionalidades Implementadas

### Parte A - Servidor de Scraping (AsyncIO)

 **4 funciones principales implementadas:**

1. **Scraping de contenido HTML**
   - Extracción de título, enlaces, estructura H1-H6
   - Conteo de imágenes y recursos
   - Cliente HTTP totalmente asíncrono con aiohttp

2. **Extracción de metadatos**
   - Meta tags básicos (description, keywords, author)
   - Open Graph tags (og:title, og:description, etc.)
   - Twitter Card tags
   - Favicon y URL canónica

3. **Comunicación asíncrona con Servidor B**
   - Socket asíncrono sin bloqueo del event loop
   - Peticiones paralelas de screenshot, performance e imágenes
   - Manejo de errores y timeouts

4. **Respuesta consolidada JSON**
   - Combina datos de scraping y procesamiento
   - Formato estandarizado según especificación
   - Transparencia total para el cliente

### Parte B - Servidor de Procesamiento (Multiprocessing)

 **Procesamiento paralelo implementado:**

1. **Captura de screenshots**
   - Selenium (Chrome/Chromium) en modo headless
   - Screenshots codificados en base64
   - Configuración de viewport y timeout

2. **Análisis de rendimiento**
   - Tiempo de carga (load_time_ms)
   - Tamaño total de recursos (total_size_kb)
   - Cantidad de requests
   - Conteo de recursos por tipo

3. **Procesamiento de imágenes**
   - Descarga de imágenes principales
   - Generación de thumbnails optimizados
   - Compresión y codificación base64

4. **Pool de procesos**
   - Distribución de tareas CPU-bound
   - N procesos configurables (default: CPU count)
   - Comunicación via sockets TCP

### Parte C - Transparencia para el Cliente

 **Implementado:**
- El cliente solo interactúa con Servidor A
- Toda la coordinación con Servidor B es transparente
- Respuesta única consolidada
- Manejo de errores unificado

---

## Formato de Respuesta

```json
{
  "url": "https://example.com",
  "timestamp": "2025-10-23T15:30:00",
  "scraping_data": {
    "title": "Example Domain",
    "links": ["https://www.iana.org/domains/example"],
    "meta_tags": {
      "description": "Example Domain",
      "og:title": "Example",
      "charset": "utf-8"
    },
    "structure": {
      "h1": 1,
      "h2": 0,
      "h3": 0,
      "h4": 0,
      "h5": 0,
      "h6": 0
    },
    "images_count": 0
  },
  "processing_data": {
    "screenshot": "iVBORw0KGgoAAAANSUhE...",
    "performance": {
      "load_time_ms": 245.67,
      "total_size_kb": 12.5,
      "num_requests": 3,
      "resources": {
        "images": 0,
        "scripts": 0,
        "stylesheets": 1,
        "other": 0
      }
    },
    "thumbnails": []
  },
  "status": "success"
}
```

---

## Tecnologías Utilizadas

- **Python 3.9+**
- **asyncio**: Event loop asíncrono
- **aiohttp**: Cliente y servidor HTTP asíncrono
- **multiprocessing**: Paralelización de tareas CPU-bound
- **BeautifulSoup4**: Parsing HTML
- **lxml**: Parser XML/HTML rápido
- **Selenium**: Capturas de screenshots
- **Pillow (PIL)**: Procesamiento de imágenes
- **sockets**: Comunicación entre servidores

---

## Manejo de Errores

El sistema implementa manejo robusto de errores:

-  URLs inválidas o inaccesibles
-  Timeouts en scraping (máximo 30 segundos)
-  Errores de comunicación entre servidores
-  Recursos no disponibles
-  Servidor de procesamiento no disponible
-  Excepciones en tareas de multiprocessing

---

## Requerimientos Cumplidos

###  Networking
- Servidor A soporta IPv4 e IPv6
- Comunicación socket TCP entre servidores
- Manejo de timeouts y errores de red

###  Concurrencia y Paralelismo
- **AsyncIO** en Servidor A:
  - Múltiples clientes asíncronos
  - aiohttp para requests HTTP
  - Sockets asíncronos
- **Multiprocessing** en Servidor B:
  - Pool de workers
  - Tareas CPU-bound en procesos separados

###  CLI con argparse
- Parsing completo de argumentos
- Mensajes de ayuda claros
- Valores por defecto razonables

---

## Testing

```bash
# Ejecutar tests (cuando estén implementados)
python -m pytest tests/

# Test manual con curl
curl "http://localhost:8000/scrape?url=https://example.com"

# Test de health
curl "http://localhost:8000/health"
```
---

## Pruebas IPv6

Se añadió un test E2E que verifica la conectividad IPv6 entre los servidores y la generación de artefactos (JSON completo y screenshot).

Resumen:
- Archivo de test: `tests/test_ipv6.py`
- Qué hace: Arranca el servidor de procesamiento (Parte B) y el servidor de scraping (Parte A) enlazados a direcciones IPv6 (p. ej. `::1`), realiza una petición `/scrape?url=https://example.com`, espera la respuesta, y comprueba que tanto el JSON completo en `outputs/` como el screenshot en `screenshots/` se generan.

Requisitos previos:
- Tener instalado `pytest` en el entorno (si usa el virtualenv incluido en `flask/`, active el venv antes):

```bash
# Desde el entorno virtual del proyecto (si aplica)
pip install pytest
```

Cómo ejecutar manualmente (pasos):

1) Iniciar el servidor de procesamiento (Parte B) ligado a IPv6 ::1 (o a la interfaz que prefiera):

```bash
python3 server_processing.py -i ::1 -p 9000
```

2) Iniciar el servidor de scraping (Parte A) ligado a IPv6 y apuntando al servidor B:

```bash
python3 server_scraping.py -i :: -p 8000 --processing-host ::1 --processing-port 9000
```

3) Ejecutar el test específico (o toda la suite):

```bash
# Ejecutar solo el test IPv6
python -m pytest tests/test_ipv6.py::test_ipv6_e2e_tmp_output -q

# O ejecutar todos los tests
python -m pytest tests/ -q
```

Notas y troubleshooting:
- El test asume que la máquina tiene soporte IPv6 y que `::1` está disponible. Si su host no tiene IPv6 configurado, el test fallará. Puede adaptar el test para usar `127.0.0.1` si necesita validación solo en IPv4.
- Asegúrese de que las dependencias estén instaladas en el mismo intérprete que usará para ejecutar `pytest` (por ejemplo, active `flask/` venv si corresponde).
- El test arranca procesos temporales; si ve puertos ocupados o procesos colgados, detenga procesos previos (p. ej. `pkill -f server_processing.py` / `pkill -f geckodriver`), o reinicie la máquina.
- Los artefactos generados por el test se almacenan en:
   - `outputs/` (JSON completos)
   - `screenshots/` (PNG cuando se usa `--save-screenshots` dentro del flujo de prueba)

Si desea integrar este test en CI, asegúrese de que el runner tenga IPv6 habilitado o adapte el test para simular la parte de red.



---

## Notas Importantes

1. **Selenium + webdriver-manager**: Requiere un navegador instalado (Chrome/Chromium o Firefox).
   El sistema intentará usar el binario instalado y descargará drivers automáticamente
   con `webdriver-manager` si hace falta. Si detectas mismatches de versión, usa el
   script `predownload_drivers.py` o instala un driver compatible manualmente.

2. **Variables de entorno útiles** (opcionales):
   - `BROWSER`: fuerza el backend de screenshots (`chrome` o `firefox`).
   - `CHROME_BIN`: ruta absoluta al binario de Chrome/Chromium si no está en PATH.
   - `BROWSER_START_TIMEOUT`: segundos a esperar por el navegador al arrancar (default: 60).

3. **Orden de inicio**: Siempre iniciar primero el servidor de procesamiento (Parte B), luego el de scraping (Parte A).

4. **Timeouts**:
   - Requests de scraping: timeout configurado por el servidor (sugerido: 30s por página).
   - Inicio del navegador: controlar con `BROWSER_START_TIMEOUT` para evitar bloqueos prolongados.

5. **IPv6**: Para usar IPv6, especificar dirección IPv6 válida (ej: `::1` para localhost).

6. **Salida y artefactos**: El cliente guarda:
   - Screenshots en `screenshots/<dominio>_<timestamp>.png` cuando se usa `--save-screenshots`.
   - JSON completo (incluyendo base64) en `outputs/<dominio>_<timestamp>.json`.

---

## Troubleshooting

### Error: "Connection refused" al iniciar Servidor A
- Asegúrate de que el Servidor B esté corriendo primero
- Verifica que los puertos coincidan

### Screenshots no funcionan
- Asegúrate de tener un navegador compatible instalado (Chrome o Chromium).
- Verifica que `chromium-browser` esté disponible si usas Chromium.
- Si utilizas un entorno headless/CI, instala un navegador o usa una imagen
   de contenedor que incluya Chrome/Chromium.
 - Si ves errores como "DevToolsActivePort file doesn't exist" o que el
    driver arranca pero no se completa el handshake, puede deberse a:
    - Flags del navegador faltantes (el código añade --headless=new, --no-sandbox,
       --disable-dev-shm-usage entre otras).
    - Restricciones de `snap` (Chromium/Firefox instalados vía snap) que
       impiden abrir puertos o crear perfiles temporales.
 - Recomendación: si estás usando Ubuntu con snaps y tienes problemas, instala
    Google Chrome/Chromium mediante el paquete deb o usa una imagen de contenedor
    que incluya Chrome para evitar issues de confinamiento.

### Errores de importación
- Instala todas las dependencias: `pip install -r requirements.txt`

---

## Autor y Fecha de Entrega

**Alumno**: Josías Vilches  
**Materia**: Computación II  
**Fecha de entrega**: 14/11/2025  
**Fecha de implementación**: 23/10/2025

---

## Licencia

Este proyecto es parte de un trabajo práctico académico.
