import socket, os
SRV = "/tmp/uds_dgram_srv"
CLI = "/tmp/uds_dgram_cli"

try: os.unlink(CLI)
except FileNotFoundError: pass

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as c:
    c.bind(CLI)               # en DGRAM local, cada lado suele tener su path
    c.sendto(b"hola", SRV)
    data, _ = c.recvfrom(2048)
    print(data)