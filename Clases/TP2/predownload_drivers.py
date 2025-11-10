# predownload_drivers.py
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
print("ChromeDriver:", ChromeDriverManager().install())
print("GeckoDriver:", GeckoDriverManager().install())