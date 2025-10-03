import socket

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind("\0demo_abstract")  # no crea archivo en /tmp
    s.listen(1)
    conn, _ = s.accept()
    with conn:
        conn.sendall(b"hola abstract\n")