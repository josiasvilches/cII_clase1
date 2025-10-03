#!/usr/bin/env python3
import socket
import json
import time
import threading
import queue
import os
from datetime import datetime

# patron Productor-Consumidor usando Unix sockets

class TaskQueue:
    """
    Cola de tareas usando Unix sockets para IPC
    """
    
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.server_socket = None
        self.task_queue = queue.Queue()
        self.workers = []
        self.running = False
    
    def start_server(self):
        """
        Inicia el servidor de cola de tareas
        """
        # Limpiar socket existente
        try:
            os.unlink(self.socket_path)
        except OSError:
            pass
        
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(10)
        
        self.running = True
        print(f"Task queue server corriendo en {self.socket_path}")
        
        while self.running:
            try:
                client_socket, _ = self.server_socket.accept()
                
                # Manejar cliente en thread separado
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Error aceptando conexión: {e}")
    
    def handle_client(self, client_socket):
        """
        Maneja un cliente (producer o consumer)
        """
        try:
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    try:
                        message = json.loads(data.decode('utf-8'))
                        
                        if message['type'] == 'produce':
                            # Cliente quiere agregar tarea
                            task = {
                                'id': message['task']['id'],
                                'data': message['task']['data'],
                                'timestamp': datetime.now().isoformat()
                            }
                            self.task_queue.put(task)
                            
                            response = {'status': 'queued', 'task_id': task['id']}
                            client_socket.send(json.dumps(response).encode('utf-8'))
                            
                        elif message['type'] == 'consume':
                            # Cliente quiere obtener tarea
                            try:
                                task = self.task_queue.get(timeout=1)
                                response = {'status': 'success', 'task': task}
                            except queue.Empty:
                                response = {'status': 'empty'}
                            
                            client_socket.send(json.dumps(response).encode('utf-8'))
                            
                    except json.JSONDecodeError:
                        error_response = {'status': 'error', 'message': 'Invalid JSON'}
                        client_socket.send(json.dumps(error_response).encode('utf-8'))
                        
        except Exception as e:
            print(f"Error manejando cliente: {e}")
    
    def stop(self):
        """
        Detiene el servidor
        """
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        try:
            os.unlink(self.socket_path)
        except OSError:
            pass

class TaskProducer:
    """
    Proceso que produce tareas
    """
    
    def __init__(self, socket_path):
        self.socket_path = socket_path
    
    def submit_task(self, task_id, task_data):
        """
        Envía una tarea a la cola
        """
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        try:
            client_socket.connect(self.socket_path)
            
            message = {
                'type': 'produce',
                'task': {
                    'id': task_id,
                    'data': task_data
                }
            }
            
            client_socket.send(json.dumps(message).encode('utf-8'))
            response = json.loads(client_socket.recv(1024).decode('utf-8'))
            
            return response
            
        finally:
            client_socket.close()

class TaskConsumer:
    """
    Proceso que consume tareas
    """
    
    def __init__(self, socket_path, worker_id):
        self.socket_path = socket_path
        self.worker_id = worker_id
    
    def get_task(self):
        """
        Obtiene una tarea de la cola
        """
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        try:
            client_socket.connect(self.socket_path)
            
            message = {'type': 'consume'}
            client_socket.send(json.dumps(message).encode('utf-8'))
            response = json.loads(client_socket.recv(1024).decode('utf-8'))
            
            return response
            
        finally:
            client_socket.close()
    
    def process_tasks(self):
        """
        Loop principal del worker
        """
        print(f"Worker {self.worker_id} iniciado")
        
        while True:
            try:
                response = self.get_task()
                
                if response['status'] == 'success':
                    task = response['task']
                    print(f"Worker {self.worker_id} procesando tarea {task['id']}: {task['data']}")
                    
                    # Simular procesamiento
                    time.sleep(2)
                    
                    print(f"Worker {self.worker_id} completó tarea {task['id']}")
                    
                elif response['status'] == 'empty':
                    # No hay tareas, esperar un poco
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Worker {self.worker_id} error: {e}")
                time.sleep(5)

def demo_ipc_patterns():
    """
    Demonstración de patrones IPC
    """
    socket_path = "/tmp/task_queue_socket"
    
    # Iniciar servidor en thread separado
    task_queue = TaskQueue(socket_path)
    server_thread = threading.Thread(target=task_queue.start_server)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(1)  # Dar tiempo al servidor para inicializar
    
    # Crear producer
    producer = TaskProducer(socket_path)
    
    # Crear consumers
    consumers = []
    for i in range(2):
        consumer = TaskConsumer(socket_path, f"worker-{i}")
        consumer_thread = threading.Thread(target=consumer.process_tasks)
        consumer_thread.daemon = True
        consumer_thread.start()
        consumers.append(consumer_thread)
    
    # Producir tareas
    for i in range(5):
        task_data = f"Procesar archivo {i}.txt"
        result = producer.submit_task(f"task-{i}", task_data)
        print(f"Tarea enviada: {result}")
        time.sleep(1)
    
    # Dejar que los workers procesen
    print("Esperando que los workers procesen las tareas...")
    time.sleep(15)
    
    task_queue.stop()

if __name__ == "__main__":
    demo_ipc_patterns()