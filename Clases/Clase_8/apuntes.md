proceso -> instancia de ejecución de un programa, espacio propio de memoria, recursos del sistema y ejecutada de forma aislada de otros procesos

hilo (thread) -> unidad de ejecución dentro de un proceso, todos los hilos de un p comparten mismo espacio de memoria, facilita comunicación pero intruce riesgos como condiciones de carrera

ventajas multiprocessing en Python
- evita el GIL -> python permite ejecutar un hilo a la vez en multiCPU por el GIL
- verdadero paralelismo (aprovechamiento de múltiples nucleos)
- aislamiento (errores no afectan a los demás directamente)

desventajas
- +uso de memoria
- comunicación compleja entre hilos

CICLO DE VIDA DE PROCESO
1. Creación (Process())
2. Inicio (start())
3. Ejecución
4. Terminación (terminate())
5. Espera del padre (join())

MÉTODOS IMPORTANTES EN PROCESS
start() -> inicia ejecución del proceso
join() -> espera a que proceso finalice
is_alive() -> devuelve True si proceso aún está activo
terminate() -> finaliza proceso de manera forzada

GESTIÓN PROCESOS PADRES - HIJOS
Padre -> crea y lanza uno o + procesos hijos, puede esperar a que hijos terminen (join), consultar si siguen vivos (is_alive), obtener info como PID (.pid) o nombre (.name)


c. COMUNICACIÓN ENTRE PROCESOS
para que 2 procesos colaboren, necesitamos mecanismo de cumonucación (pipes, queues)

| Característica | Pipe               | Queue                    |
| -------------- | ------------------ | ------------------------ |
| Conexión       | Entre dos extremos | Múltiples procesos       |
| Sincronización | Manual             | Automática (thread-safe) |
| Complejidad    | Más bajo nivel     | Más fácil de usar        |
 
queues: put() -> inserta en cola, get() -> lee

d. SINCRONIZACIÓN BÁSICA CON LOCK
por qué sincronizar? cuando muchos procesos acceden/modifican datos compartidos puede producirse 'condiciones de carrera', por lo tanto el resultado final depende del orden en el cual los procesos accedieron a los datos (esto termina siendo indeseable y no deterministico)

se utiliza Lock como mecanismo de sincronización, garantiza que un proceso a la vez acceda al sector crítico del código

LOCK
actúa como una puerta cerrada, el proceso debe adquirilo antes de entrar a SC y liberarlo al salir
Python -> with lock -> garantiza que solo un proceso a la vez acceda a print (ejemplo)

e. POOL DE PROCESOS
Pool (grupo de procesos) -> forma eficiente de gestionar múltiples procesos, en lugar de creaer y destruir procesos, Python crea un grupo reutilizable de procesos para ejecutar tareas cuando están disponibles

ideales para procesar grandes cantidaddes de datos en paralelos y aprovechar mútliples núcleos sin sobrecargar el sistema

Métodos
- map() -> aplica función a cada elemento de un iterable, devuelve resultados en orden
- apply() -> ejecuta única función con un argumento
- map_async() -> como map, no bloquea, se puede usar con callback
- apply_async() -> como apply, no bloquea, permite programación más simple

f. MEMORIA COMPARTIDA BÁSICA (Value y Array)
es necesario compartir datos simples entre procesos tales como números o una pequeña lista, ahí entra value (comparte un valor, int, float, etc.) y array (comparte lista de valores)

sintaxis en Python:
from multiprocessing import Value, Array
# Compartir un entero
contador = Value('i', 0)  # 'i' para int, 'd' para double
# Compartir una lista de 5 enteros
lista = Array('i', 5)

