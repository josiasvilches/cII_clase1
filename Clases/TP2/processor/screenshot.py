#!/usr/bin/env python3
"""
Módulo de Captura de Screenshots
Genera screenshots de páginas web usando Selenium.

Notas:
- Usa `webdriver-manager` para descargar el driver (ChromeDriver) de forma automática.
  Esto evita pasos manuales de instalación en la mayoría de entornos.
"""

import io
import base64
from typing import Optional
import os
import tempfile
import shutil
import time

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    # Firefox imports
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    # Try to import webdriver_manager (optional). If missing, we'll rely on Selenium Manager.
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.firefox import GeckoDriverManager
        WM_AVAILABLE = True
    except Exception:
        WM_AVAILABLE = False

    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False


def _create_driver(browser: str = 'chrome', width: int = 1280, height: int = 720, headless: bool = True, timeout: int = 30):
    """Create a WebDriver for the requested browser.

    browser: 'chrome' or 'firefox'
    Uses webdriver-manager if available, otherwise relies on Selenium Manager (selenium>=4.10).
    """
    if browser == 'firefox':
        opts = FirefoxOptions()
        if headless:
            # Prefer the explicit attribute for Firefox headless mode
            try:
                opts.headless = True
            except Exception:
                opts.add_argument('--headless')
            # Also set MOZ_HEADLESS env var which can help in some environments
            os.environ.setdefault('MOZ_HEADLESS', '1')
            # Disable content sandbox where it causes startup issues (snap/containers)
            os.environ.setdefault('MOZ_DISABLE_CONTENT_SANDBOX', '1')
            try:
                opts.set_preference('security.sandbox.content.level', 0)
            except Exception:
                pass
        opts.add_argument(f'--width={width}')
        opts.add_argument(f'--height={height}')
        opts.set_preference('general.useragent.override', 'Mozilla/5.0 (Web Scraper Bot)')

        if WM_AVAILABLE:
            # Create a temporary driver log file for easier debugging
            log_path = os.path.join(tempfile.gettempdir(), f"geckodriver-{int(time.time())}.log")
            service = FirefoxService(GeckoDriverManager().install(), log_path=log_path)
            print(f"[screenshot] geckodriver log -> {log_path}")
            driver = webdriver.Firefox(service=service, options=opts)
        else:
            # Rely on Selenium Manager to find/download geckodriver
            driver = webdriver.Firefox(options=opts)

    else:
        # default to chrome
        opts = ChromeOptions()
        # detect local chrome/chromium binary (env overrides executable detection)
        chrome_bin = os.environ.get('CHROME_BIN')
        if not chrome_bin:
            # try common binary names
            chrome_bin = shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium-browser') or shutil.which('chromium')
        if chrome_bin:
            try:
                opts.binary_location = chrome_bin
            except Exception:
                pass
        # modern headless flag for Chrome
        if headless:
            opts.add_argument('--headless=new')
        opts.add_argument(f'--window-size={width},{height}')
        # robust flags for headless and sandboxed environments (snap/containers)
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--disable-extensions')
        opts.add_argument('--remote-debugging-port=0')
        opts.add_argument('--disable-setuid-sandbox')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--user-agent=Mozilla/5.0 (Web Scraper Bot)')

        # If we detected a local chrome/chromium binary, prefer Selenium Manager
        # (Selenium will locate/download the matching chromedriver). This avoids
        # mismatches between chromedriver and the installed browser (common with snap).
        if chrome_bin:
            print(f"[screenshot] using chrome binary: {chrome_bin} (Selenium Manager will select driver)")
            try:
                driver = webdriver.Chrome(options=opts)
            except Exception as e:
                print(f"[screenshot] Selenium Manager failed to start Chrome: {e}")
                # fallback to webdriver-manager if available
                if WM_AVAILABLE:
                    log_path = os.path.join(tempfile.gettempdir(), f"chromedriver-{int(time.time())}.log")
                    service = ChromeService(ChromeDriverManager().install(), log_path=log_path)
                    print(f"[screenshot] chromedriver log -> {log_path}")
                    driver = webdriver.Chrome(service=service, options=opts)
                else:
                    raise
        else:
            if WM_AVAILABLE:
                # Create a temporary driver log file for easier debugging
                log_path = os.path.join(tempfile.gettempdir(), f"chromedriver-{int(time.time())}.log")
                service = ChromeService(ChromeDriverManager().install(), log_path=log_path)
                print(f"[screenshot] chromedriver log -> {log_path}")
                driver = webdriver.Chrome(service=service, options=opts)
            else:
                # Rely on Selenium Manager to locate the correct driver for installed browser
                driver = webdriver.Chrome(options=opts)

    # Timeouts
    try:
        driver.set_page_load_timeout(timeout)
    except Exception:
        pass
    try:
        driver.implicitly_wait(1)
    except Exception:
        pass
    return driver


def _create_driver_with_timeout(*args, timeout_sec: int = 20, **kwargs):
    """Create driver but fail fast if startup blocks: run creation in a thread and enforce timeout."""
    from concurrent.futures import ThreadPoolExecutor, TimeoutError

    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(_create_driver, *args, **kwargs)
        try:
            return fut.result(timeout=timeout_sec)
        except TimeoutError:
            # Attempt to cancel/run cleanup
            try:
                fut.cancel()
            except Exception:
                pass
            raise RuntimeError(f"Timeout while starting browser driver (>{timeout_sec}s)")


def capture_screenshot(url: str, timeout: int = 30, full_page: bool = False) -> Optional[str]:
    """Captura un screenshot de una página web y devuelve la imagen en base64.

    Args:
        url: URL a capturar
        timeout: Timeout en segundos para carga de página
        full_page: actualmente ignorado (Chrome headless captura viewport)

    Returns:
        Base64 string o None si falla.
    """
    if not SELENIUM_AVAILABLE:
        return None

    # Choose browser: env BROWSER overrides (values: 'chrome' or 'firefox')
    browser = os.environ.get('BROWSER', '').lower() or 'chrome'

    # Allow overriding the driver-start timeout via env var for debugging
    try:
        start_timeout = int(os.environ.get('BROWSER_START_TIMEOUT', '20'))
    except Exception:
        start_timeout = 20

    try:
        print(f"[screenshot] starting browser driver (browser={browser}, start_timeout={start_timeout}s)")
        driver = _create_driver_with_timeout(browser=browser, timeout=timeout, timeout_sec=start_timeout)
        try:
            driver.get(url)
            png = driver.get_screenshot_as_png()
            return base64.b64encode(png).decode('utf-8')
        finally:
            try:
                driver.quit()
            except Exception:
                pass

    except Exception as e:
        # If chrome failed and browser is chrome, try firefox as fallback
        if browser == 'chrome':
            try:
                driver = _create_driver(browser='firefox', timeout=timeout)
                try:
                    driver.get(url)
                    png = driver.get_screenshot_as_png()
                    return base64.b64encode(png).decode('utf-8')
                finally:
                    try:
                        driver.quit()
                    except Exception:
                        pass
            except Exception:
                pass

        print(f"Error al capturar screenshot de {url}: {e}")
        return None


def capture_screenshot_with_options(
    url: str,
    width: int = 1280,
    height: int = 720,
    timeout: int = 30,
    wait_for_selector: Optional[str] = None
) -> Optional[str]:
    """Captura screenshot con opciones (usa Selenium)."""
    if not SELENIUM_AVAILABLE:
        return None

    browser = os.environ.get('BROWSER', '').lower() or 'chrome'

    try:
        try:
            start_timeout = int(os.environ.get('BROWSER_START_TIMEOUT', '20'))
        except Exception:
            start_timeout = 20
        print(f"[screenshot] starting browser driver (browser={browser}, start_timeout={start_timeout}s)")
        driver = _create_driver_with_timeout(browser=browser, width=width, height=height, timeout=timeout, timeout_sec=start_timeout)
        try:
            driver.get(url)
            # TODO: implement wait_for_selector using selenium waits if needed
            png = driver.get_screenshot_as_png()
            return base64.b64encode(png).decode('utf-8')
        finally:
            try:
                driver.quit()
            except Exception:
                pass
    except Exception as e:
        # fallback attempt: if chrome failed, try firefox
        if browser == 'chrome':
            try:
                driver = _create_driver(browser='firefox', width=width, height=height, timeout=timeout)
                try:
                    driver.get(url)
                    png = driver.get_screenshot_as_png()
                    return base64.b64encode(png).decode('utf-8')
                finally:
                    try:
                        driver.quit()
                    except Exception:
                        pass
            except Exception:
                pass

        print(f"Error al capturar screenshot con opciones: {e}")
        return None


def is_screenshot_available() -> bool:
    """Indica si Selenium + webdriver-manager están disponibles."""
    return SELENIUM_AVAILABLE


# Fallback usando PIL para generar placeholder cuando no se puede capturar
def generate_placeholder_screenshot() -> str:
    try:
        from PIL import Image
        img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except ImportError:
        return ""
