import os
import sys
import time
import signal
import subprocess
import requests
import glob


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def _python():
    # Use the same python interpreter running the tests
    return sys.executable


def wait_for_health(url, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def terminate_proc(p):
    try:
        p.terminate()
        p.wait(timeout=5)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass


def test_ipv6_e2e_tmp_output(tmp_path):
    """End-to-end basic test over IPv6: start servers, call /health and /scrape.

    This test will:
    - start server_processing.py bound to ::1:9000
    - start server_scraping.py bound to :: :8000 and pointing to ::1:9000
    - wait for /health over IPv6
    - call /scrape?url=https://example.com and expect status success
    - verify outputs/*.json and screenshots/*.png were created for example.com
    """

    py = _python()

    # Start server_processing
    sp_proc = subprocess.Popen([py, os.path.join(PROJECT_ROOT, 'server_processing.py'), '-i', '::1', '-p', '9000'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        # Start server_scraping (bind to all :: so IPv6 works)
        ss_proc = subprocess.Popen([py, os.path.join(PROJECT_ROOT, 'server_scraping.py'), '-i', '::', '-p', '8000',
                                    '--processing-host', '::1', '--processing-port', '9000'],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        try:
            # Wait for scraping server health
            health_url = 'http://[::1]:8000/health'
            assert wait_for_health(health_url, timeout=30), "Scraping server didn't respond on /health via IPv6"

            # Make the scrape request
            scrape_url = 'http://[::1]:8000/scrape'
            params = {'url': 'https://example.com'}
            r = requests.get(scrape_url, params=params, timeout=60)
            assert r.status_code == 200, f"Unexpected status code: {r.status_code}"
            data = r.json()
            assert data.get('status') == 'success', f"Scrape failed: {data}"

            # Check outputs and screenshots for example.com
            outputs = glob.glob(os.path.join(PROJECT_ROOT, 'outputs', 'example_com_*.json'))
            screenshots = glob.glob(os.path.join(PROJECT_ROOT, 'screenshots', 'example_com_*.png'))

            assert outputs, 'No outputs/example_com_*.json found'
            assert screenshots, 'No screenshots/example_com_*.png found'

        finally:
            # Stop scraping server
            terminate_proc(ss_proc)
    finally:
        # Stop processing server
        terminate_proc(sp_proc)
