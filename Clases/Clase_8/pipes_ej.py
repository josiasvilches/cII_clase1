from multiprocessing import Process, Pipe

def hijo(conn):
    conn.send("Hola padre")
    conn.close()

if __name__ == '__main__':
    padre_conn, hijo_conn = Pipe()
    p = Process(target=hijo, args=(hijo_conn,))
    p.start()
    print("Mensaje del hijo:", padre_conn.recv())
    p.join()
