import threading
import socketserver

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):   # para atender a cada cliente
        data = str(self.request.recv(1024), 'ascii')   # castea a string usando ascii
        cur_thread = threading.current_thread() # obtener el hilo actual
        response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')   # convierte el nombre del hilo y el mensaje a bytes para enviarlos al cliente
        self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):   # hago un mixin de tcp y threading, que hereda de ambos
    allow_reuse_address = True # permite reutilizar el puerto

if __name__ == "__main__":

    HOST, PORT = "localhost", 9999
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler) # uso mi nueva clase mixin de threading tcp
    with server:
        ip, port = server.server_address
        print(f"Servidor iniciado en {ip}:{port}")

        server.serve_forever