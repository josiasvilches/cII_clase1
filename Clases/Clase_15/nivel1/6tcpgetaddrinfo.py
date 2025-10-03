import socket

def connect_first(host, port):
    # getaddrinfo devuelve posibles (familia, tipo, protocolo, canonname, sockaddr)
    for fam, stype, proto, _canon, sockaddr in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM):
        try:
            with socket.socket(fam, stype, proto) as s:
                s.connect(sockaddr)
                s.sendall(b"hola\n")
                return s.recv(1024)
        except OSError:
            continue
    raise OSError("No se pudo conectar en ninguna familia/dirección")

if __name__ == "__main__":
    print(connect_first("localhost", 9005))