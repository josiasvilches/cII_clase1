FIFOs -> también conocidos como named pipes, mecanismo de comunicación entre procesos (intercambio de datos unidireccional a través de sistema de archivos)

persistentes en sistema de archivos (a diferencia de los anónimos os.pipe() que son temporales y existen durante la vida del padre), usan ruta con nombre (permite que procesos no emparentados se comuniquen), comportamiento como archivos especiales, podés abrirlos con open() en Python o cat, echo

si nadie lee el fifo se queda bloqueado (en espera hasta que alguien lo lea)

fifos en python -> los usas como archivos normales (open()) o os.open(), la diferencia es en el comportamiento de bloqueo

cursores y descriptores de archivo
proceso abre archivo o FIFO se le asigna un descriptor de archivo, mantiene posición propia de cursor (indica dónde va leyendo o escribiendo), si 2 procesos distintos abren el mismo FIFO para leer cada uno va a tener su posición de lectura (no comparten cursor por más de que usen el mismo FIFO)

no hay sincronización automática entre múltiples lectores, se lee 2 veces el mismo mensaje si 2 procesos se conectan al FIFO en paralelo, o en otro caso, que 1 lector consuma los datos antes que el otro llegue y no reciba 
