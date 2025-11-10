#!/bin/bash
# Script de instalación para el TP2

echo "================================================"
echo "Instalación TP2 - Sistema de Scraping Web"
echo "================================================"
echo ""

# Verificar Python
echo "1. Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo " Python 3 no está instalado"
    exit 1
fi

python_version=$(python3 --version)
echo " $python_version encontrado"
echo ""

# Instalar dependencias
echo "2. Instalando dependencias de Python..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo " Error instalando dependencias"
    exit 1
fi

echo " Dependencias instaladas"
echo ""

# Instalar Playwright
echo "3. Instalando navegador Playwright (Chromium)..."
echo "   Esto puede tardar unos minutos..."
echo "3. Asegúrese de que un navegador sin cabeza esté disponible en el sistema (Chrome/Chromium)."
echo "   En Debian/Ubuntu puede instalar Chromium con:"
echo "   sudo apt-get update && sudo apt-get install -y chromium-browser"
echo "   O para Chrome, descargue el paquete .deb de Google Chrome desde Google e instálelo."
echo ""
echo "   Si prefiere descargar controladores por adelantado, webdriver-manager se puede usar programáticamente o"
echo "   a través del paquete `webdriver-manager` incluido en los requisitos."

if [ $? -ne 0 ]; then
    echo "  Error instalando Playwright. Screenshots no estarán disponibles."
    echo "   El sistema funcionará pero sin capturas de pantalla."
else
    echo " Playwright instalado correctamente"
fi

echo ""
echo "================================================"
echo " Instalación completada!"
echo "================================================"
echo ""
echo "Para iniciar el sistema:"
echo ""
echo "1. Terminal 1 - Servidor de Procesamiento (Parte B):"
echo "   python3 server_processing.py -i localhost -p 9000"
echo ""
echo "2. Terminal 2 - Servidor de Scraping (Parte A):"
echo "   python3 server_scraping.py -i localhost -p 8000"
echo ""
echo "3. Terminal 3 - Cliente de prueba:"
echo "   python3 client.py -u https://example.com"
echo ""
