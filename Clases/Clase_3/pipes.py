import os

def main():
    # 1. Crear el pipe
    r, w = os.pipe()  # r = descriptor de lectura, w = escritura

    pid = os.fork()

    if pid == 0:
        # Proceso hijo: leer
        os.close(w)  # Cerrar extremo de escritura
        r_fd = os.fdopen(r, 'r')  # Convertir descriptor en objeto de archivo
        mensaje = r_fd.read()
        print(f"Hijo recibió: {mensaje}")
        r_fd.close()

    else:
        # Proceso padre: escribir
        os.close(r)  # Cerrar extremo de lectura
        w_fd = os.fdopen(w, 'w')  # Convertir descriptor en archivo
        w_fd.write("Hola desde el padre\n")
        w_fd.close()

if __name__ == "__main__":
    main()
