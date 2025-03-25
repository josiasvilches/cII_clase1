# Mutables e Inmutables
# Objetos inmutables (int)
x = 10
print("ID original de x:", id(x))

x += 5  # Se crea un nuevo objeto en el Heap
print("ID de x después de modificarlo:", id(x))  # ¡Es distinto!

# Objetos mutables (list)
y = [1, 2, 3]
print("ID original de y:", id(y))

y = y + [5]  # Se modifica el mismo objeto
print("ID de y después de modificarlo:", id(y))  # ¡Es el mismo!

