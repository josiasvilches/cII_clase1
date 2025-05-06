from multiprocessing import Pool
import time

def saludar(nombre):
    time.sleep(1)
    return f"Hola, {nombre}!"

if __name__ == '__main__':
    with Pool(3) as pool:
        resultados = [
            pool.apply_async(saludar, args=(nombre,))
            for nombre in ["Ana", "Luis", "Pedro"]
        ]
        for r in resultados:
            print(r.get())  # Espera a que cada resultado esté listo
