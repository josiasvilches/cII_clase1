import os

pid = os.fork()

if pid == 0:  # Proceso hijo
    os.execlp("ls", "ls", "-l")  # Reemplaza el hijo con `ls -l`
else:
    # os.wait()  # El padre espera que el hijo termine
    print("El proceso hijo terminó")
