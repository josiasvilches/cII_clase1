import socket
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
    c.connect("\0demo_abstract")
    print(c.recv(1024))