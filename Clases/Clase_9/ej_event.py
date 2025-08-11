from multiprocessing import Process, Event
import time

def worker_waiter_event(event, i): # Renombrado
    """ Espera a que el evento se establezca. """
    print(f"Proceso {i} (Event): Esperando el evento...")
    event.wait() # Se bloquea aquí hasta que event.set() sea llamado
    print(f"Proceso {i} (Event): ¡Evento detectado! Continuando...")

def event_setter_event(event): # Renombrado
    """ Espera un poco y luego establece el evento. """
    print("Setter (Event): Voy a dormir por 3 segundos...")
    time.sleep(3)
    print("Setter (Event): ¡Estableciendo el evento!")
    event.set()

if __name__ == '__main__':
    event_ex = Event() # Renombrado, El evento empieza como 'no establecido'

    waiters_ev = [Process(target=worker_waiter_event, args=(event_ex, i)) for i in range(5)] # Renombrado
    setter_ev = Process(target=event_setter_event, args=(event_ex,)) # Renombrado

    for w in waiters_ev:
        w.start()
    setter_ev.start()

    for w in waiters_ev:
        w.join()
    setter_ev.join()
    print("Todos los procesos (Event) terminaron.")