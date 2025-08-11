from multiprocessing import Process, Queue, current_process
import time
import logging
import random # Añadido para el sleep

# Configuración básica de logging para el proceso logger
# Esto solo se configura en el proceso logger.
def setup_logger():
    logger = logging.getLogger('distributed_logger')
    logger.setLevel(logging.INFO)
    # Evitar añadir múltiples handlers si la función se llama varias veces
    if not logger.handlers: 
        fh = logging.FileHandler('distributed_app.log', mode='w') # 'w' para empezar limpio
        formatter = logging.Formatter('%(asctime)s - %(processName)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def logger_process_q(queue): # Renombrado
    """ Proceso dedicado a escribir logs desde una cola. """
    logger = setup_logger()
    print("Logger Process (Queue): Iniciado y esperando mensajes.")
    while True:
        try:
            # Espera por un mensaje, con timeout para permitir cierre si es necesario
            record = queue.get(timeout=1) 
            if record == "STOP_LOGGING":
                logger.info("Señal de parada recibida. Terminando logger.")
                print("Logger Process (Queue): Señal de parada recibida. Terminando.")
                break
            logger.info(record)
        except Exception: # queue.Empty si hay timeout y nada en la cola
            # Si la cola está vacía, simplemente continuamos esperando.
            # Podríamos añadir lógica aquí para terminar si no hay actividad por mucho tiempo.
            pass 
    print("Logger Process (Queue): Terminado.")

def worker_process_q_log(log_queue, worker_id): # Renombrado
    """ Worker que realiza trabajo y envía logs a la cola. """
    proc_name = current_process().name # Para incluir en el log
    for i in range(5):
        msg = f"Worker {worker_id} ({proc_name}): Realizando paso {i}"
        print(msg) # También imprime en consola para ver actividad
        log_queue.put(msg) # Envía el mensaje al proceso logger
        time.sleep(random.uniform(0.3, 1.0))
    log_queue.put(f"Worker {worker_id} ({proc_name}): Trabajo finalizado.")
    print(f"Worker {worker_id} ({proc_name}): Trabajo finalizado y mensaje enviado.")

if __name__ == '__main__':
    log_queue_ex = Queue() # Renombrado
    
    logger_p = Process(target=logger_process_q, args=(log_queue_ex,), name="LoggerProcess") # Renombrado
    logger_p.start()

    worker_procs = [Process(target=worker_process_q_log, args=(log_queue_ex, i), name=f"Worker-{i}") for i in range(3)] # Renombrado
    for w in worker_procs:
        w.start()

    # Espera a que los workers terminen
    for w in worker_procs:
        w.join()
    print("Todos los workers (Queue-Log) han terminado.")

    # Envía la señal de parada al logger
    log_queue_ex.put("STOP_LOGGING")
    
    # Espera a que el logger termine
    logger_p.join(timeout=5) # Añade timeout por si acaso
    if logger_p.is_alive():
        print("Logger process (Queue-Log) no terminó a tiempo, forzando.")
        logger_p.terminate()
        logger_p.join()

    print("Todos los procesos (Queue-Log) terminados. Revisa 'distributed_app.log'.")