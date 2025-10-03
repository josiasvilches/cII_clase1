import socket, array, os

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
    c.connect("/tmp/fdpass.sock")
    # Recibir con buffer para ancillary data
    fds = array.array("i")
    msg, anc, flags, addr = c.recvmsg(1024, socket.CMSG_SPACE(array.array("i", [0]).itemsize))
    for level, ctype, data in anc:
        if level == socket.SOL_SOCKET and ctype == socket.SCM_RIGHTS:
            fds.frombytes(data[:fds.itemsize])
    if not fds:
        raise SystemExit("No llegó ningún FD")

    borrowed_fd = fds[0]
    # Leer del descriptor recibido (como si lo hubiéramos abierto aquí)
    os.lseek(borrowed_fd, 0, os.SEEK_SET)
    print(os.read(borrowed_fd, 4096).decode(errors="replace"))
    os.close(borrowed_fd)