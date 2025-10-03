import socket, struct, os

SO_PEERCRED = 17  # en Linux
fmt = "iii"       # pid, uid, gid

SRV = "/tmp/peercd.sock"
try: os.unlink(SRV)
except FileNotFoundError: pass

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.bind(SRV)
    s.listen(1)
    conn, _ = s.accept()
    with conn:
        pid, uid, gid = struct.unpack(fmt, conn.getsockopt(socket.SOL_SOCKET, SO_PEERCRED, struct.calcsize(fmt)))
        print({"pid": pid, "uid": uid, "gid": gid})
        conn.sendall(f"Hola UID={uid} PID={pid}\n".encode())