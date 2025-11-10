# test_screenshot.py
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so we can import local packages when running this
# script directly (sys.path[0] is the script's directory otherwise).
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from processor import screenshot

url = "https://example.com"
print("Selenium available:", screenshot.is_screenshot_available())
print("Using BROWSER env:", os.environ.get('BROWSER', '(not set)'))
img_b64 = screenshot.capture_screenshot(url, timeout=30)
if img_b64:
    # write to file
    import base64, datetime
    data = base64.b64decode(img_b64)
    fn = f"debug_screenshot_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
    with open(fn, "wb") as f:
        f.write(data)
    print("Screenshot saved to", fn)
else:
    print("Screenshot returned None. Check server stdout for errors.")