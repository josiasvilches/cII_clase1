def read_fifo(fifo_r):
    print("Esperando mensaje...")
    mensaje = fifo_r.readline().strip()
    return mensaje

def write_fifo(fifo_w, message):
    fifo_w.write(message + "\n")
    fifo_w.flush()
