from multiprocessing import Process, Event, Value
import ctypes
import time
import random

def monitor_sensor_event(event, temperature, sensor_id): # Renombrado
    """ Simula un sensor que mide temperatura y activa un evento. """
    while True:
        # En un sistema real, la lectura de temperatura podría ser una operación bloqueante
        # o requerir su propia sincronización si el sensor es compartido.
        # Aquí, asumimos que la lectura es simple.
        temp = random.uniform(15.0, 35.0)
        
        # Actualizar un valor compartido es opcional, el Event es el mecanismo principal aquí.
        # Si se actualiza, se necesitaría un Lock para shared_temp.
        # temperature.value = temp 
        
        print(f"Sensor {sensor_id} (Event): Temperatura = {temp:.2f}°C")
        if temp > 30.0:
            print(f"Sensor {sensor_id} (Event): ¡ALERTA! Temperatura > 30°C. ¡Activando evento!")
            event.set() # Activa la alarma
            break # El sensor deja de medir una vez que activa la alarma
        
        if event.is_set(): # Otro sensor podría haber activado la alarma
            print(f"Sensor {sensor_id} (Event): Alarma ya activada por otro. Terminando.")
            break
        time.sleep(1)

def alarm_system_event(event): # Renombrado
    """ Espera el evento de alarma. """
    print("Sistema de Alarma (Event): Esperando señal de alerta...")
    event.wait() # Se bloquea hasta que event.set() es llamado
    print("Sistema de Alarma (Event): ¡ALARMA RECIBIDA! ¡ACTIVANDO SIRENA!")
    # Aquí iría el código para activar la sirena, enviar notificaciones, etc.

if __name__ == '__main__':
    alarm_event_ex = Event() # Renombrado
    # shared_temp_ev = Value(ctypes.c_float, 20.0) # Opcional, no usado directamente por Event

    sensor1_ev = Process(target=monitor_sensor_event, args=(alarm_event_ex, None, 1)) # Renombrado
    sensor2_ev = Process(target=monitor_sensor_event, args=(alarm_event_ex, None, 2)) # Renombrado
    alarm_proc_ev = Process(target=alarm_system_event, args=(alarm_event_ex,)) # Renombrado

    alarm_proc_ev.start()
    sensor1_ev.start()
    sensor2_ev.start()

    alarm_proc_ev.join() # El sistema de alarma terminará cuando reciba la señal
    
    # Una vez que la alarma ha sonado y terminado, podemos detener los sensores.
    # En un sistema real, se usaría un mecanismo de cierre más elegante (otro Event, Pipe, etc.)
    print("Sistema de Alarma (Event) terminado. Deteniendo sensores...")
    if sensor1_ev.is_alive(): sensor1_ev.terminate()
    if sensor2_ev.is_alive(): sensor2_ev.terminate()
    
    # Esperar a que terminen si fueron terminados
    sensor1_ev.join(timeout=1)
    sensor2_ev.join(timeout=1)
    
    print("Sistema de Monitoreo (Event) terminado.")