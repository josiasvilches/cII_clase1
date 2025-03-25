import sys
import gc

# Crear un objeto anidado
y = [1]      # y tiene una referencia
x = [2, y]   # x tiene una referencia y también referencia a y

# Medimos cuántas referencias tiene y
print("Conteo inicial de referencias de y:", sys.getrefcount(y))  # Debería ser 3 (y, x[1] y argumento en print)

# Eliminamos la única referencia directa a y
del y

# Forzamos la recolección de basura (no es estrictamente necesario)
gc.collect()

# ¿Cuántas referencias tiene ahora x[1]?
print("Conteo de referencias de x[1]:", sys.getrefcount(x[1]))  # Debería seguir siendo 2 (x[1] y print)
