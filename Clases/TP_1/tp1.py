import multiprocessing as mp
import json
import hashlib
import time
import random
from datetime import datetime
from collections import deque
import numpy as np
import os

class BiometricData:
    """clase que maneja datos biométricos"""
    @staticmethod
    def generate_sample():
        """genera muestra de datos biométricos"""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "frecuencia": random.randint(60, 200),
            "presion": [random.randint(90, 200), random.randint(70, 110)],
            "oxigeno": random.randint(85, 100)
        }

class BiometricProcessor:
    """clase base que procesa señales biométricas"""
    
    def __init__(self, signal_type, input_pipe, output_queue, start_event, sync_barrier):
        self.signal_type = signal_type
        self.input_pipe = input_pipe
        self.output_queue = output_queue
        self.window = deque(maxlen=30)  
        self.start_event = start_event  # Event para coordinar inicio
        self.sync_barrier = sync_barrier  # Barrier para sincronizar envío de resultados
    
    def extract_signal(self, data):
        """Extrae la señal específica del dato completo"""
        if self.signal_type == "frecuencia":
            return data["frecuencia"]
        elif self.signal_type == "presion":
            # Usamos la presion sistólica para el análisis
            return data["presion"][0]
        elif self.signal_type == "oxigeno":
            return data["oxigeno"]
        else:
            raise ValueError(f"Tipo de señal desconocido: {self.signal_type}")
    
    def calculate_statistics(self):
        """Calcula media y desviación estándar de la ventana actual"""
        if len(self.window) == 0:
            return 0.0, 0.0
        
        values = np.array(list(self.window))
        media = np.mean(values)
        desv = np.std(values)
        return float(media), float(desv)
    
    def process(self):
        """Procesa los datos recibidos"""
        # Esperar señal de inicio
        print(f"Procesador {self.signal_type}: Esperando señal de inicio...")
        self.start_event.wait()
        print(f"Procesador {self.signal_type}: Iniciado!\n")
        
        sample_count = 0
        
        try:
            while sample_count < 60:
                # Recibir datos del pipe
                data = self.input_pipe.recv()
                
                # Extraer la señal específica
                signal_value = self.extract_signal(data)
                
                # Agregar a la ventana móvil
                self.window.append(signal_value)
                
                # Calcular estadísticas
                media, desv = self.calculate_statistics()
                
                # Crear resultado
                resultado = {
                    "tipo": self.signal_type,
                    "timestamp": data["timestamp"],
                    "media": media,
                    "desv": desv
                }
                
                # Sincronizar con otros procesadores antes de enviar resultado
                try:
                    self.sync_barrier.wait(timeout=5.0)  # Esperar a que todos estén listos
                    
                    # Enviar resultado al verificador
                    self.output_queue.put(resultado)
                    
                except mp.BrokenBarrierError:
                    print(f"Procesador {self.signal_type}: Barrier rota, enviando resultado sin sincronización")
                    self.output_queue.put(resultado)
                
                sample_count += 1
                
        except Exception as e:
            print(f"Error en procesador {self.signal_type}: {e}")
        finally:
            self.input_pipe.close()
            print(f"Procesador {self.signal_type}: Terminado")


class BlockchainVerifier:
    """Clase para verificar datos y construir la cadena de bloques"""
    
    def __init__(self, queues, file_lock, start_event):
        self.queues = queues
        self.blockchain = []
        self.file_lock = file_lock  # Lock para proteger escritura del archivo
        self.start_event = start_event  # Event para coordinar inicio
        
    def wait_for_results(self, timestamp):
        """Espera los tres resultados para un timestamp específico"""
        results = {}
        
        # Recibir resultados de las tres colas
        for queue in self.queues:
            result = queue.get()
            results[result["tipo"]] = result
        
        return results
    
    def validate_data(self, results):
        """Valida los datos y detecta alertas"""
        alerta = False
        
        # Verificar frecuencia < 200
        if results["frecuencia"]["media"] >= 200:
            alerta = True
        
        # Verificar oxigeno entre 92 y 100
        oxigeno_media = results["oxigeno"]["media"]
        if not (90 <= oxigeno_media <= 100):
            alerta = True
        
        # Verificar presion sistólica < 200
        if results["presion"]["media"] >= 200:
            alerta = True
        
        return alerta
    
    def calculate_hash(self, block_data, prev_hash, timestamp):
        """Calcula el hash SHA-256 del bloque"""
        content = prev_hash + str(block_data) + timestamp
        return hashlib.sha256(content.encode()).hexdigest()
    
    def create_block(self, results):
        """Crea un nuevo bloque para la cadena"""
        timestamp = results["frecuencia"]["timestamp"]  # Todos tienen el mismo timestamp
        
        # Verificar datos y detectar alertas
        alerta = self.validate_data(results)
        
        # Obtener hash del bloque anterior
        prev_hash = self.blockchain[-1]["hash"] if self.blockchain else "0"
        
        # Crear datos del bloque
        datos = {
            "frecuencia": {"media": results["frecuencia"]["media"], "desv": results["frecuencia"]["desv"]},
            "presion": {"media": results["presion"]["media"], "desv": results["presion"]["desv"]},
            "oxigeno": {"media": results["oxigeno"]["media"], "desv": results["oxigeno"]["desv"]}
        }
        
        # Calcular hash del bloque
        block_hash = self.calculate_hash(datos, prev_hash, timestamp)
        
        # Crear bloque
        block = {
            "timestamp": timestamp,
            "datos": datos,
            "alerta": alerta,
            "prev_hash": prev_hash,
            "hash": block_hash
        }
        
        return block
    
    def process_blocks(self):
        """Procesa los bloques durante 60 segundos"""
        # Esperar a que todos los procesadores estén listos antes de empezar
        print("Verificador: Esperando señal de inicio...")
        self.start_event.wait()
        print("Verificador: Iniciado!\n")
        
        block_count = 0
        
        try:
            while block_count < 60:
                # Esperar resultados de los tres procesadores
                results = self.wait_for_results(None)
                
                # Crear bloque
                block = self.create_block(results)
                
                # Agregar a la cadena
                self.blockchain.append(block)
                
                # Mostrar información del bloque
                print(f"Bloque {block_count + 1}: Hash={block['hash'][:16]}... Alerta={block['alerta']}")
                
                # Guardar inmediatamente cada bloque (con sincronización)
                self.save_blockchain_atomic()
                
                block_count += 1
                
        except Exception as e:
            print(f"Error en verificador: {e}")
        
        print("Verificador: Terminado")
    
    def save_blockchain_atomic(self, filename="blockchain.json"):
        """Guarda la cadena de bloques con sincronización usando Lock"""
        try:
            # Obtener la ruta del directorio donde está el script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(script_dir, filename)
            
            with self.file_lock:  # Uso del Lock para proteger escritura del archivo
                with open(full_path, 'w') as f:
                    json.dump(self.blockchain, f, indent=2)
                # No mostrar mensaje cada vez para evitar spam
        except Exception as e:
            print(f"Error al guardar blockchain: {e}")
    
    def save_blockchain(self, filename="blockchain.json"):
        """Guarda la cadena de bloques en un archivo JSON (versión final)"""
        try:
            # Obtener la ruta del directorio donde está el script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(script_dir, filename)
            
            with self.file_lock:  # Uso del Lock para proteger escritura del archivo
                with open(full_path, 'w') as f:
                    json.dump(self.blockchain, f, indent=2)
                print(f"Cadena de bloques guardada en {full_path}")
        except Exception as e:
            print(f"Error al guardar blockchain: {e}")


def main_process(pipes, start_event):
    """Proceso principal que genera datos biométricos"""
    print("Proceso principal: Preparando generación de datos...")
    
    # Dar tiempo a que todos los procesos se inicialicen
    time.sleep(2)
    
    # Señalar a todos los procesos que pueden comenzar
    print("Proceso principal: Señalando inicio a todos los procesos...")
    start_event.set()
    
    print("Iniciando generación de datos biométricos...")
    
    for i in range(60):
        # Generar muestra
        sample = BiometricData.generate_sample()
        
        # Enviar a todos los procesadores
        for pipe in pipes:
            pipe.send(sample)
        
        print(f"Muestra {i+1}/60 enviada: {sample['timestamp']}")
        
        # Esperar 1 segundo
        time.sleep(1)
    
    # Cerrar pipes
    for pipe in pipes:
        pipe.close()
    
    print("Generación de datos completada")


def processor_worker(signal_type, input_pipe, output_queue, start_event, sync_barrier):
    """Worker para el proceso de análisis"""
    processor = BiometricProcessor(signal_type, input_pipe, output_queue, start_event, sync_barrier)
    processor.process()


def verifier_worker(queues, file_lock, start_event):
    """Worker para el proceso verificador"""
    verifier = BlockchainVerifier(queues, file_lock, start_event)
    verifier.process_blocks()
    verifier.save_blockchain()


def main():
    """Función principal del sistema"""
    print("=== Sistema Concurrente de Análisis Biométrico ===")
    print()
    
    # Crear primitivas de sincronización
    file_lock = mp.Lock()  # Lock para proteger archivo blockchain
    start_event = mp.Event()  # Event para coordinar inicio
    sync_barrier = mp.Barrier(3)  # Barrier para sincronizar los 3 procesadores
    
    # Crear pipes para comunicación principal -> procesadores
    pipes_main = []
    pipes_proc = []
    
    for i in range(3):
        main_pipe, proc_pipe = mp.Pipe()
        pipes_main.append(main_pipe)
        pipes_proc.append(proc_pipe)
    
    # Crear queues para comunicación procesadores -> verificador
    queues = [mp.Queue() for _ in range(3)]
    
    # Tipos de señales
    signal_types = ["frecuencia", "presion", "oxigeno"]
    
    # Crear procesos
    processes = []
    
    # Proceso principal (generador)
    main_proc = mp.Process(target=main_process, args=(pipes_main, start_event))
    processes.append(main_proc)
    
    # Procesos analizadores
    for i in range(3):
        proc = mp.Process(
            target=processor_worker, 
            args=(signal_types[i], pipes_proc[i], queues[i], start_event, sync_barrier)
        )
        processes.append(proc)
    
    # Proceso verificador
    verifier_proc = mp.Process(target=verifier_worker, args=(queues, file_lock, start_event))
    processes.append(verifier_proc)
    
    try:
        # Iniciar todos los procesos
        print("Iniciando todos los procesos...")
        for proc in processes:
            proc.start()
        
        # Esperar a que terminen
        for proc in processes:
            proc.join()
        
        print("Todos los procesos han terminado correctamente")
        
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario")
        for proc in processes:
            if proc.is_alive():
                proc.terminate()
                proc.join()
    
    except Exception as e:
        print(f"Error en el sistema: {e}")
        for proc in processes:
            if proc.is_alive():
                proc.terminate()
                proc.join()


if __name__ == "__main__":
    main()