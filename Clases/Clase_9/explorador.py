from multiprocessing import Process, RLock, Value
import ctypes
import time

class AccountRL: # Renombrado para evitar conflicto con otros Account
    def __init__(self, lock):
        self.balance = Value(ctypes.c_double, 1000.0)
        self.lock = lock # Debe ser un RLock

    def _internal_update(self, amount, process_id, operation_name):
        # Este método es llamado por deposit y withdraw, ya dentro del lock
        # No necesita 'with self.lock:' aquí si es llamado por un método que ya lo tiene.
        # Pero si pudiera ser llamado externamente, necesitaría 'with self.lock:'
        print(f"Proceso {process_id}: {operation_name} {abs(amount)}...")
        time.sleep(0.1)
        self.balance.value += amount
        print(f"Proceso {process_id}: Nuevo balance {self.balance.value}")


    def deposit(self, amount, process_id):
        with self.lock: # Adquiere RLock
            print(f"Proceso {process_id}: Entrando a deposit.")
            self._internal_update(amount, process_id, "Depositando")
            print(f"Proceso {process_id}: Saliendo de deposit.")


    def withdraw_and_log(self, amount, process_id):
        with self.lock: # Adquiere RLock
            print(f"Proceso {process_id}: Entrando a withdraw_and_log.")
            if self.balance.value >= amount:
                self._internal_update(-amount, process_id, "Retirando") # Llama a otro método
                print(f"Proceso {process_id}: Retiro exitoso.")
                return True
            else:
                print(f"Proceso {process_id}: Fondos insuficientes.")
                return False

def task_rl(account, i):
    account.deposit(200, i)
    account.withdraw_and_log(100, i)

if __name__ == '__main__':
    rl = RLock() # Importante que sea RLock
    acc_rl = AccountRL(rl)

    procs = [Process(target=task_rl, args=(acc_rl, i)) for i in range(2)]
    for p in procs: p.start()
    for p in procs: p.join()
    print(f"Balance final de la cuenta (RLock): {acc_rl.balance.value}")