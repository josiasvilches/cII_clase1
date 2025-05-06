from multiprocessing import Process, Value

def sumar_100(contador):
    for _ in range(100):
        contador.value += 1

if __name__ == '__main__':
    from time import sleep
    contador = Value('i', 0)
    p1 = Process(target=sumar_100, args=(contador,))
    p2 = Process(target=sumar_100, args=(contador,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Valor final:", contador.value)

    