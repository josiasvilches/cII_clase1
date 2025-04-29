import signal
import time

# Variable de control
interrupciones = 0
max_interrupciones = 3

def mi_handler(signum, frame):
    global interrupciones
    interrupciones += 1
    print(f"\n[INFO] Señal recibida: {signum}. Interrupciones: {interrupciones}")
    if interrupciones >= max_interrupciones:
        print("[INFO] Límite alcanzado. Terminando proceso.")
        exit(0)

signal.signal(signal.SIGINT, mi_handler)

print("Presioná Ctrl+C para enviar SIGINT...")
while True:
    print("Trabajando... (Ctrl+C para interrumpir)")
    time.sleep(1)
