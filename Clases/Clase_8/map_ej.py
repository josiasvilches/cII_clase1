from multiprocessing import Pool

def cuadrado(x):
    return x * x

if __name__ == '__main__':
    with Pool(processes=4) as pool:
        resultados = pool.map(cuadrado, [1, 2, 3, 4, 5])
    print("Resultados:", resultados)
