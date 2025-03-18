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
