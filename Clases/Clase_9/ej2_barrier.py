from multiprocessing import Process, Barrier, Array
import time
import random

def update_row_barrier(barrier, row_index, matrix, num_cols, num_phases): # Renombrado
    """ Actualiza una fila de la matriz en varias fases usando Barrier. """
    for phase in range(num_phases):
        print(f"Proceso {row_index} (Mat-Bar): Iniciando Fase {phase} para fila {row_index}...")
        # Simula cálculo basado en valores anteriores
        # Aquí, simplemente incrementamos elementos de la fila
        with matrix.get_lock(): # Protege el acceso al Array compartido
            for col in range(num_cols):
                matrix[row_index * num_cols + col] += (row_index + 1) * (phase + 1) * random.randint(1,5)
            
            current_row_vals = matrix[row_index * num_cols : (row_index + 1) * num_cols]
            print(f"Proceso {row_index} (Mat-Bar): Fila {row_index} en Fase {phase} = {current_row_vals}")
            
        time.sleep(random.uniform(0.1, 0.5)) # Simula tiempo de cómputo
        arrival_idx = barrier.wait() # Espera a que todas las filas se actualicen en esta fase
        if arrival_idx == 0: # Solo un proceso (el que llega con índice 0) imprime esto
            print(f"--- Fase {phase} completada por todos los procesos (Mat-Bar). Barrera cruzada. ---")


if __name__ == '__main__':
    ROWS_BAR = 3 # Renombrado
    COLS_BAR = 4 # Renombrado
    PHASES_BAR = 2 # Renombrado
    
    # Matriz compartida (Array), inicializada a ceros
    shared_matrix_bar = Array('i', [0] * (ROWS_BAR * COLS_BAR)) # Renombrado
    
    # Barrera para ROWS_BAR procesos
    barrier_mat = Barrier(ROWS_BAR) # Renombrado
    
    processes_mat_bar = [] # Renombrado
    print("Iniciando actualización de matriz por fases (Barrier)...")
    print(f"Matriz inicial (Barrier): {shared_matrix_bar[:]}")
    for i in range(ROWS_BAR):
        p = Process(target=update_row_barrier, args=(barrier_mat, i, shared_matrix_bar, COLS_BAR, PHASES_BAR))
        processes_mat_bar.append(p)
        p.start()

    for p in processes_mat_bar:
        p.join()
        
    print(f"\nActualización (Barrier) finalizada. Matriz final:")
    for r in range(ROWS_BAR):
        print(shared_matrix_bar[r * COLS_BAR : (r + 1) * COLS_BAR])