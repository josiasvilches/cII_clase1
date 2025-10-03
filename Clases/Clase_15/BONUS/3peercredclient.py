import socket
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
    c.connect("/tmp/peercd.sock")
    print(c.recv(1024))