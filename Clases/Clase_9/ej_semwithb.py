from multiprocessing import Process, BoundedSemaphore
import time
import random

MAX_CONNECTIONS_BS = 2 # Renombrado
connections_bs = BoundedSemaphore(MAX_CONNECTIONS_BS) # Renombrado

def get_connection_bs(process_id): # Renombrado
    """ Obtiene una conexión. """
    connections_bs.acquire()
    print(f"Proceso {process_id} (BSem-Pool): Conexión obtenida.")

def release_connection_bs(process_id): # Renombrado
    """ Libera una conexión. Lanza ValueError si se libera de más. """
    print(f"Proceso {process_id} (BSem-Pool): Liberando conexión.")
    connections_bs.release()

def use_resource_bs(process_id): # Renombrado
    """ Simula el uso de una conexión, con un error deliberado. """
    connection_held = False
    try:
        get_connection_bs(process_id)
        connection_held = True
        time.sleep(random.uniform(0.5, 1.5))
        
        release_connection_bs(process_id)
        connection_held = False # Liberada correctamente
        
        print(f"Proceso {process_id} (BSem-Pool): ¡Intentando liberar de nuevo por error!")
        release_connection_bs(process_id) # Esto debería causar ValueError
    except ValueError:
        print(f"Proceso {process_id} (BSem-Pool): ¡ERROR DETECTADO! Se intentó liberar una conexión de más.")
    except Exception as e:
        print(f"Proceso {process_id} (BSem-Pool): Otro error: {e}")
    finally:
        # Asegurar que si se obtuvo una conexión y no se liberó por una excepción ANTES del error,
        # se intente liberar.
        if connection_held: # Si el error ocurrió antes de la primera liberación
            try:
                release_connection_bs(process_id)
                print(f"Proceso {process_id} (BSem-Pool): Conexión liberada en finally.")
            except ValueError:
                 print(f"Proceso {process_id} (BSem-Pool): Error al liberar en finally (posiblemente ya estaba en el límite).")


if __name__ == '__main__':
    processes_bs_pool = [] # Renombrado
    for i in range(5):
        p = Process(target=use_resource_bs, args=(i,))
        processes_bs_pool.append(p)
        p.start()

    for p in processes_bs_pool:
        p.join()