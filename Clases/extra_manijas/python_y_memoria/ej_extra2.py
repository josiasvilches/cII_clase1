a = [1, 2, 3]   # Se crea una lista en el Heap
b = a           # Se copia la referencia, no el objeto
c = [1, 2, 3]   # Se crea una nueva lista en el Heap

print("Dirección de memoria", id(a))
print("Dirección de memoria", id(b))
print("Dirección de memoria", id(c))
