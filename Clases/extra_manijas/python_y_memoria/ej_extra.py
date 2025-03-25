import sys

# Crear un objeto
x = [1, 2, 3]

# Ver cuántas referencias tiene
print("Conteo inicial de referencias de x:", sys.getrefcount(x))

def f(x):
    y = x
    z = x
    print("Conteo de referencias de x dentro de f:", sys.getrefcount(x))  # +2 referencias dentro de f

# Ejecutar la función
f(x)

# Después de salir de f, y y z deberían ser eliminados automáticamente
print("Conteo de referencias de x después de llamar a f:", sys.getrefcount(x))
