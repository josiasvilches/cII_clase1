import argparse


def cesar(texto, clave, cifrar=True):
    resultado = []
    desplazamiento = clave if cifrar else -clave
    for caracter in texto:
        if caracter.isalpha():
            base = ord('A') if caracter.isupper() else ord('a')
            nuevo_caracter = chr((ord(caracter) - base + desplazamiento) % 26 + base)
            resultado.append(nuevo_caracter)
        else:
            resultado.append(caracter)
    return ''.join(resultado)


parser = argparse.ArgumentParser(description="cifrado, descifrado de texto")
parser.add_argument("-i", "--input", required=True, help="Input File")
parser.add_argument("-o", "--output", required=True, help="Output File")
parser.add_argument("-m", "--mode", required=True, choices=["cifrar", "descifrar"], help="opciones: cifrar, descifrar")
parser.add_argument("-k", "--key", type=int, required=True, help="Key")

args = parser.parse_args()

# Leer archivo de entrada
with open(args.input, "r", encoding="utf-8") as f:
    contenido = f.read()

# Aplicar cifrado o descifrado
modo_cifrar = args.mode == "cifrar"
resultado = cesar(contenido, args.key, cifrar=modo_cifrar)

# Guardar en el archivo de salida
with open(args.output, "w", encoding="utf-8") as f:
    f.write(resultado)

print(f"Procesando {args.input} en modo {args.mode} con clave {args.key}. Guardando en {args.output}")

# para añadir próximamente

# ✔️ Agregar manejo de excepciones para errores en la lectura/escritura de archivos.
# ✔️ Soporte para caracteres especiales y tildes (porque ahora solo cifra letras de la A-Z).

