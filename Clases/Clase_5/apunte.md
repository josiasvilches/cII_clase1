Queue (cola) -> estructura de datos que sigue principio FIFO, herramienta que permite comunicación segura entre procesos (IPC) o entre hilos (threads)

USOS:
- transmisión de datos entre procesos sin la necesidad de compartir memoria
- mantener sincronizaci+on entre productores y consumidores
- desacoplar tareas (proceso genera datos, otro los procesa, no es necesario que se ejcuten al mismo ritmo)

IMPORTANCIA EN SO
- usado en colas de mensajes de kernel (permite que los procesos se ejecuten)
- ayudan a gestionar buffers de entrada/salida y planificación de tareas
- esenciales para programación concurrente segura (evita condiciones de carrera)

DIFERENCIAS PIPES - QUEUE
- comunicación: unidireccional - bidireccional
- compartición: flujo tipo archivo - objetos serializables
- sincronización: implícita por bloqueo - mejor soporte con herramientas (semáforos y locks)
- Python: os.pipe() / multiprocessing.Pipe() - multiprocessing.Queue()

FUNCIONAMIENTO interno
puede pensarse como estructura de almacenamiento de memoria compartida gestionada por So o biblioteca de programación 

CICLO DE VIDA 
Creación -> proceso (generalmente principal) crea instancia de queue
envío -> proceso (prod) pone (put) un objeto en la queue
espera -> queue mantiene almacenado hasta que consumidor lo tome
recepción -> otro proceso lo retira (get) de la queue
finalización -> todos los procesos terminan, queue cierra

MECANISMOS DE SINCRONIZACIÓN
usa locks y semafotos para evitar que 2 procesos escriban o lean a la vez
si queue está vacía con get() puede bloquearse (espera activa/pasiva)
si está llena, put() tbm puede bloquearse dependiendo de cómo se configura

COMPARACIÓN CICLO DE VIDA  
- creación: necesita definir extremos - más simple con objetos
- transferencia: flujo de bytes - basado en objetos
- bloqueos: bloqueo implícito - control más granular
- seguridad: manual (menos abstracto) - thread-safe (python)

teniendo en cuenta el archivo 'ej_queue.py'
Queue() -> crea cola compartida entre procesos
put() -> proceso productor inserta un valor
get() -> consumidor recupera ese valor
Process(...) -> define cada proceso con su función y argumentos
start() / join() -> lanzan y espera que terminen
.join() -> cerrar procesos de forma adecuada evitando zombis

teniendo en cuenta el archivo 'prod_cons.py'
None (sentinela) -> indica que no hay más mensajes
consumidor -> escucha en bucle hasta None
sleep (delays artificiales) -> simular tiempo cómputo

PREVENCIÓN PROBLEMAS COMUNES
- Deadlock (espera circular entre procesos)-> usar None como sentinela, verificar orden de cierre
- Bloqueo Infinito (consumidor nunca recibe señal de fin)-> enviar señal de fin a cada consumidor
- Pérdida de datos (procesos finalizan antes de procesar todo) -> usar join() para asegurar que cada p se termine
- Confusión entre procesos -> incluir nombre de productor en mensaje

RESUMEN
- Queue -> si se necesita multiprocesamiento, buffer de mensajes, seguriddad sin preocuparte por locks
- Pipes -> directo (low level), comunicación sencilla entre 2 procesos, control manual sobre flujo de bytes