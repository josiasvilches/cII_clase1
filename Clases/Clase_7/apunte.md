señales -> mecanismo de comunicación asincrónica entre procesos (a veces dentro de un proceso), son equivalentes a interrupciones pero a nivel software

USOS:
- notificar eventos -> CTRL + C o errores como división por 0
- Controlar procesos (pausar, continuar o terminar)
- Sincronziar acciones entre procesos concurrentes

Cada señal tiene nombre simbólico (SGINT(2), SIGTERM, etc.) y un número asociado
- Sincronas -> generadas por error en programa (SIGFPE, división por 0)
- Asíncronas -> enviadas en otro proceso o el sistema (SIGKILL, SIGUSR1)
- TIempo real -> señales numeradas a partir de SIGRTMIN con colas y entrega ordenada

Proceso recibe señal
- ignora (si se le permite)
- usa handler por defecto (finaliza proceso) o 
- define propio manejador de señlaes

signal.signal()
python permite manejar señales mediante módulo signal, deja asocial una señal con una función handler que se ejecuta cuando la señal es recibida

funciones y constantes claves:
- signal.signal(signum, handler) -> Asocia un handler (función) a una señal.
Ej: signal.signal(signal.SIGINT, my_handler)
- signal.SIGINT, signal.SIGTERM, signal.SIGUSR1, etc. -> Constantes que representan las señales.

- signal.getsignal(signum) -> Devuelve el handler actual para una señal.

- signal.pause() -> Suspende el proceso hasta que reciba una señal.

no todas las señales se pueden capturar o ignorar (SIGKILL y SIGTOP no se pueden manejar)
handler debe ser una función que reciba 2 argumentos 
def handler (signum, frame): signum -> numero de señal, frame -> objeto frame con el contexto (ignorado normalmente)

SIGKILL y SIGSTOP -> el SO reserva esas señales para tener control absoluto sobre los procesos, incluso si están mal programados

SIGINT _> señal estándar que ell terminal envía al proceso cuando presionas ctrl c, asincrona y se puede manejer o ignorar
SIGUSr1 -> asincrona pero es una señal definida por usuario, no se activa sola, debe ser enviada desde otro proceso con kill o sigqueue

kill -> llamada al sistema, envia señal específica a un proceso identificado por su PID
    sintaxis en terminal
        kill -SIGUSR1 <pid>
    sintaxis en Python
    import os, signal
        os.kill(pid, signal.SIGUSR1)

para enviar señales en python sería os.kill()

sigqueue()->más avanzado que kill, disponible en C, adjunta datos (valor entero) a señal enviada, Python no lo soporta nativamente

MANEJO SEGURO DE SEÑALES
cuando una señal interrumpe un proceso puede hacerlo en cualquier punto de ejecución, si el handler intenta hacer operaciones que no son seguras para interrupciones (escribir en disco o uso de recursos compartidos), se generan condiciones de carrera, bloqueos o corrupciones de estado

ASYNC-SIGNAL-SAFE
funciones de SO que se invocan de manera segura desde handler de señal
ejemplos seguros
- write(), read()
- _exit() (no confundir con exit() en C)
- signal(), kill()
- sigaction(), sigprocmask()

no seguros:
- printf(), malloc(), free()
- operaciones con logs, archivos, etc.
- cualquier cosa que llame funciones complejas por debajos

Python -> debe tener los handlers más simples posible, setea variable e imprime mensaje corto, llamar a exit() de ser necesario, ideal usar flags (var. globales)

MULTITHREADED
señales asociadas a proceso, pueden ser entregadas a cualquier hilo que no haya bloqueado esa señal, esto acomplejiza todo porque:
- todos los hilos comparten mismo espacio de señales
- un hilo recibe señal que otro esperaba
- algunos hilos pueden estar ejecutando código no async-signal-safe cuando reciben señal

MANEJO SEÑALES EN MULTIHILO
C con POSIX -> uso de pthread_sigmask() para bloquear señales en ciertos hilos
    se pueden tener hilos dedicados a señales que espera con sigwait()

Python -> sólo hilo principal recibe señales, ningún otro threading.Thread recibe señal directa de sistema

No se puede instalar un handler en hilo secundario, no se ejecuta nunca, si querés que pase, se debe usar alguna estructura compartida (flag, queue, Event)

Porque queue.Queue está pensada para sincronización entre hilos, y es thread-safe, Una variable global común puede causar race conditions (condiciones de carrera) si no usás locks.

Señales vs otros usos de IPC
señales -> mecanismos antiguos y básicos para comunicación y control entre procesos en sistemas UNIX

señal -> comunicación asíncrona entre procesos o desde SO, eventos breves que notifican que algo ocurrió (SIGINT, SIGUSR1), el proceso puede ignorarlas, usar comportamiento por defecto, o definir handler personalizado

| Mecanismo         | Características principales                                      |
|------------------|------------------------------------------------------------------|
| **Señales**       | Comunicación simple, sin datos asociados (excepto en señales reales). Buenas para notificar. |
| **Pipes**         | Canal unidireccional, útil para transmitir flujos de datos.     |
| **Named Pipes (FIFOs)** | Permiten comunicación entre procesos sin relación padre-hijo. |
| **Sockets**       | Comunicación entre procesos locales o remotos, bidireccional.   |
| **Shared Memory** | Rápida, pero necesita sincronización (semaforos, mutexes).      |
| **Message Queues**| Envío de mensajes estructurados, con colas ordenadas.           |
| **Files**         | Comunicación lenta pero persistente.                            |

cuando conviene usar señales? cuando sólo necesito notificar que algo ocurrió (sin datos), busco interrumpir o controlar procesos o manejar eventos especiales como SIGCHILD, SIGALRM

cuando NO conviene? si necesito pasar datos complejos, múltimples procesos y necesito control fino de concurrencia, entornos hulihilo complejos donde señales suelen ser impredecibles

señales -> codazo, rápido, no decís mucho pero sabes que quieren algo
pipe -> nota por debajo de puerta
socket -> videollamda
shared memory -> dejas archivo editable y ambos escriben ahí
queue -> fila de pedidos para que el otro los atienda 1x1