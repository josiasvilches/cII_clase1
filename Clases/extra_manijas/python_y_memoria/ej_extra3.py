# Stack & Heap

def prueba_stack():
    x = [1, 2, 3]  # Se crea una lista en el Heap
    print("Dirección de x en el Stack:", id(x))  # Muestra la referencia en el Stack
    print("Dirección de la lista en el Heap:", id(x[0]))  # Muestra un objeto dentro de la lista

prueba_stack()

