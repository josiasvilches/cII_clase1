LOCK -> proceso adquiere con acquire() (cierra ese lock), y libera con release()
acquire(blocking=True, timeout=-1): permite intentos de adquisición no bloqueantes o con tiempo de espera
With lock (forma recomendada de usar el lock)

RLOCK -> lock reentrante (permite a mismo proceso adquirir lock múltiples veces sin bloquearse a sí mismo), usado en funciones recursivas o llamadas anidadas. Sólo el dueño puede liberar el rlock (proceso que lo adquirió)

Rlock es más lento que Lock por la gestión adicional del dueño y contador

Semáforo -> primitiva de sincronización que gestiona contador interno, su diferencia de Lock es que inicia con valor N y permite que N procesos estén en el semáforo simultáneamente

cualquier proceso puede llamar a release(), el problema es que puede corromper la lógica del recurso

BoundedSemaphore -> idéntico a Semáforo, impide que se llame a release() mǘas veces de las que se llamó a acquire(), es recomendable usarlo si se quiere evitar errores de programación (si hay un release accidental)

Condition -> primitiva de sincronización (procesos esperan hasta que una condición se cumpla), asociada con un lock o rlock
notify() -> eficiente si sabes que solo un proceso puede proceder
notityall() -> simple y seguro si no hay certeza de qué procesos pueden proceder (puede provocar estampida)

Event -> funciona con bandera (flag) booleana segura para procesos, puede estar en estado establecito (set) o NO establecido (clear)
is_set() -> verifica si está establecido (TRUE) o no (false)
set() -> despierta todos los p que están esperando
clear() -> restablece el evento

Barrier -> num fijo de p esperen mutuamente en un punto específico antes de que cualquiera de ellos pueda continuar, recomendado en computación paralela, en inicialización sincronizada, etc.
wait() es llamada bloqueante, reset() restablece barrera a estado inicial, permitiendo reutilización y abort() pone barrera en estado roto, cada wait que se mande lanzan BrokenBarrierError (barrera rota)

Queue -> estrucutura tipo FIFO, diseñada para ser segura para la comunicación entre p, permite que muchos p añadan (put()) o quiten (get()) objetos de la cola sin preocuparse por condicion de carrera, recomendado para paso de mensajes, distribución de tareas, recolección de resultados, etc.

Value -> crea objeto de memoria compartida que almacena un único valor de tipo de dato específico (ctypes), se usa cuando tenemos contadores compartidos, flags de estado o necesitamos resultados simples

Array -> crea arreglo de memoria compartida (simil a Value pero para múltiples elementos), se usa cuando tengamos buffeers compartidos, procesamiento de datos en paralelo, almacenamiento de estado distribuido, etc.