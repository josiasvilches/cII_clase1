import socket, os
SRV = "/tmp/uds_dgram_srv"

try: os.unlink(SRV)
except FileNotFoundError: pass

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
    s.bind(SRV)
    print("UDS-DGRAM listo", SRV)
    while True:
        data, addr = s.recvfrom(2048)  # addr es la ruta del cliente
        s.sendto(data, addr)