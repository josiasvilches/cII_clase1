import os

fifo_path = 'canal_fifo'

if not os.path.exists(fifo_path):
    os.mkfifo(fifo_path)
    print(f"FIFO creado en {fifo_path}")
else:
    print("El FIFO ya existe")

# no se utiliza porque ya está creado el fifo por un ejemplo anterior