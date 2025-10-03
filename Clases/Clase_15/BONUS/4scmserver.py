import socket, os, array
SRV = "/tmp/fdpass.sock"
try: os.unlink(SRV)
except FileNotFoundError: pass

# Prepara un archivo a compartir
fd_to_share = os.open("/etc/hostname", os.O_RDONLY)

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind(SRV)
    s.listen(1)
    conn, _ = s.accept()
    with conn:
        # Prepara mensaje de control con el FD
        fds = array.array("i", [fd_to_share])
        anc = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds.tobytes())]
        conn.sendmsg([b"FD"], anc)  # el payload de datos es arbitrario

os.close(fd_to_share)