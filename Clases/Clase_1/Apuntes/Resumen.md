argumento de linea de comandos -> información extra a un script como parámetros
sys.argv -> lista que contiene argumentos que se pasan cuando se ejecuta el script desde el terminal (siempre y cuando se le pasen argumentos), 
funciona como una lista, en caso de que llamemos a un elemento que no existe nos tira un error de índice fuera de rango


GETOPT -> módulo que ayuda a manejar argumentos de línea de comandos
cuándo es útil? para argumentos opcionales (-f, --file), asociar valores a opciones (-o output.txt), facilitar el uso del script

los comandos que no necesitan valores se deben definir sin ':' y sin '=', caso contrario cuando si queremos que tengamos un valor, se declaran con ':' como: '-f:' y '-o:' ["help", "file=", "output="]

ARGPARSE -> similar a getopt pero más intuitivo y poderoso, tiene sintaxis más clara, genera automáticamente mensajes de error, permite definir tipos de datos (si argumento debe ser lista, entero, etc.) 
y finalmente argumentos posicionales y opcionales
para que los argumentos sean obligatorios mientras que los estemos declarando debemos añadir 'required=True'

Tipos de Datos que maneja argparse:
 - int "-n", "--num"
 - lista "-l", "--list" nargs="+" (a la hora de hacer la lista en el argumento se hace con espacios)
 - booleano "-v", "--verbose" (action="store_true")

cuando ejecutamos 'sis.getrefcount(x)' crea una referencia temporal extra dentro de la llamada a la función, por eso podemos llegar a tener una referencia 'extra'

HEAP -> montículo, contiene todos los datos de objetos creados en tiempo de ejecución, no es liberado automáticamente, se encarga GC
STACK -> almacena var. locales y referencias a objetos, LIFO, liberado automáticamente cuando la fc. se termina

EJ visual: x = [1, 2, 3]
stack -> guarda X
heap -> guarda [1, 2, 3]


Mutabilidad e inmutabilidad
Mutables -> pueden modificarse luego de creación (lista, diccionarios, conjuntos) -> mantienen referencia en memoria aunque cambie su contenido
Inmutables -> no pueden modificarse (enteros, cadenas, tuplas) -> generan nuevas referencias si intentamos modificarlos

un ejemplo que puede confundir sería una lista (mut) 'cambie' su dirección en memoria
y.append(5) -> modifica lista en mismo lugar
y = y + [5] -> crea nueva lista en memoria y cambia referencia de y



------
Proceso -> programa en ejecución, ejecutado por CPU y administrado por SO
programa -> conjunto de instrucciones almacenadas en disco

atrib. clave:
 - PID -> ID único asignado por SO
 - Estado -> indica si está en ejecución, esperando recursos o terminado
 - Espacio direcciones -> código, datos, pila y otros segmentos de memoria
 - Tabla de archivos abiertos -> archivos y dispositivos que el proceso tiene abiertos
 - Contexto de ejecución -> incluye registros de CPU, contador de programa, otras estructuras necesarias para retomar su ejecución luego de una interrupción

DIFERENCIAS Programa - Proceso

ejecutado en: disco     RAM
ej:        firefox      firefox con varias pestañas abiertas

------
fork() -> permite que un proceso cree un proceso hijo, duplicando contexto, se ejecutan en el mismo punto del código pero con valores distintos de PID
exec() -> en lugar de duplicar proceso, creamos un proceso hijo totalmente distinto

-----
Procesos Zombis -> proceso que terminó su ejecución pero su entrada en tabla de procesos sigue existiendo porque padre no leyó su estado de salida
Proceso Huérfano -> proceso padre termina antes que hijo, dejándolo sin supervisión, normalmente en linux son 'adoptados' por init o systemd}
-----

