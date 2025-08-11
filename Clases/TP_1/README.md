# Sistema Concurrente de Análisis Biométrico con Cadena de Bloques Local

## Descripción

Este proyecto implementa un sistema distribuido en procesos que simula el análisis biométrico en tiempo real de una prueba de esfuerzo, procesando las señales en paralelo y almacenando los resultados en una cadena de bloques local para garantizar la integridad de los datos.

## Arquitectura del Sistema

```
┌─────────────────────────┐                     
│  Proceso Principal      │  1 dato/seg         
│  (generador)            │─────────────┐       
└─────────────────────────┘             │       
        │ pipe/fifo                     │       
        ▼                               ▼       
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Proc A     │  │ Proc B     │  │ Proc C     │
│ Frecuencia │  │ Presión    │  │ Oxígeno    │
└─────┬──────┘  └─────┬──────┘  └─────┬──────┘
      │ queue         │ queue         │ queue  
      └───────┬────────┴────────┬──────┘       
              ▼                 ▼              
         ┌─────────────────────────┐           
         │  Proceso Verificador    │           
         └────────┬────────────────┘           
                  │ escribe bloque             
                  ▼                           
         ┌─────────────────────────┐           
         │  Cadena de Bloques      │           
         └─────────────────────────┘           
```

## Componentes

### 1. Proceso Principal (Generador)
- Genera datos biométricos simulados cada segundo
- Envía datos a los tres procesos analizadores mediante pipes
- Simula 60 segundos de datos

### 2. Procesos Analizadores (A, B, C)
- **Proceso A**: Analiza frecuencia cardíaca
- **Proceso B**: Analiza presión arterial  
- **Proceso C**: Analiza oxígeno en sangre
- Mantienen ventana móvil de 30 segundos
- Calculan media y desviación estándar
- Envían resultados al verificador mediante queues

### 3. Proceso Verificador
- Recibe resultados de los tres analizadores
- Detecta valores fuera de rango (alertas)
- Construye bloques de la cadena
- Calcula hashes SHA-256
- Persiste la cadena en `blockchain.json`

## Requisitos

- Python ≥ 3.9
- numpy
- multiprocessing (incluido en Python)
- hashlib (incluido en Python)
- json (incluido en Python)

## Instalación

1. Clona o descarga los archivos del proyecto
2. Instala las dependencias:
   ```bash
   pip install numpy
   ```

## Uso

### Ejecutar el Sistema Principal

```bash
python tp1.py
```

El sistema:
1. Iniciará la generación de datos biométricos
2. Procesará las señales en paralelo
3. Construirá la cadena de bloques
4. Generará el archivo `blockchain.json`
5. Mostrará información en tiempo real de cada bloque

### Verificar la Integridad de la Cadena

```bash
python verificar_cadena.py [archivo_blockchain]
```

Si no se especifica archivo, usa `blockchain.json` por defecto.

Este script:
- Verifica la integridad de todos los bloques
- Comprueba el encadenamiento correcto
- Genera un reporte detallado en `reporte.txt`

## Archivos Generados

- **`blockchain.json`**: Cadena de bloques completa con todos los datos
- **`reporte.txt`**: Reporte de análisis con estadísticas y verificación de integridad

## Estructura de Datos

### Datos Biométricos (Input)
```json
{
    "timestamp": "2024-01-01T12:00:00",
    "frecuencia": 75,
    "presion": [120, 80],
    "oxigeno": 98
}
```

### Bloque de la Cadena
```json
{
    "timestamp": "2024-01-01T12:00:00",
    "datos": {
        "frecuencia": {"media": 75.2, "desv": 5.1},
        "presion": {"media": 118.5, "desv": 8.2},
        "oxigeno": {"media": 97.8, "desv": 1.2}
    },
    "alerta": false,
    "prev_hash": "abc123...",
    "hash": "def456..."
}
```

## Criterios de Alerta

El sistema genera alertas cuando:
- Frecuencia cardíaca ≥ 200 bpm
- Oxígeno en sangre fuera del rango 90-100%
- Presión sistólica ≥ 200 mmHg

## Características Técnicas

- **Comunicación IPC**: Pipes para generador→analizadores, Queues para analizadores→verificador
- **Primitivas de Sincronización**: 
  - **Lock**: Protege escritura del archivo blockchain.json
  - **Event**: Coordina inicio sincronizado de todos los procesos
  - **Barrier**: Sincroniza los 3 procesadores antes de enviar resultados
  - **Queue**: Comunicación segura entre procesadores y verificador
- **Análisis Estadístico**: Ventana móvil de 30 segundos con numpy
- **Integridad**: Hashes SHA-256 y encadenamiento verificable
- **Tolerancia a fallos**: Manejo de excepciones y cierre limpio de recursos

## Ejemplo de Ejecución

```bash
$ python tp1.py
=== Sistema Concurrente de Análisis Biométrico ===
Primitivas de sincronización utilizadas:
- Lock: Para proteger escritura del archivo blockchain.json
- Event: Para coordinar inicio sincronizado de todos los procesos
- Barrier: Para sincronizar envío de resultados entre procesadores
- Queue: Para comunicación segura procesadores → verificador

Iniciando todos los procesos...
Proceso principal: Preparando generación de datos...
Procesador frecuencia: Esperando señal de inicio...
Procesador presion: Esperando señal de inicio...
Procesador oxigeno: Esperando señal de inicio...
Verificador: Esperando señal de inicio...
Proceso principal: Señalando inicio a todos los procesos...
Procesador frecuencia: Iniciado!
Procesador presion: Iniciado!
Procesador oxigeno: Iniciado!
Verificador: Iniciado!
Iniciando generación de datos biométricos...
Muestra 1/60 enviada: 2024-08-11T12:00:00
Bloque 1: Hash=a1b2c3d4e5f6... Alerta=False
Muestra 2/60 enviada: 2024-08-11T12:00:01
Bloque 2: Hash=f6e5d4c3b2a1... Alerta=True
...
Generación de datos completada
Procesador frecuencia: Terminado
Procesador presion: Terminado
Procesador oxigeno: Terminado
Verificador: Terminado
Cadena de bloques guardada en blockchain.json
Todos los procesos han terminado correctamente

$ python verificar_cadena.py
=== Verificador de Integridad de Cadena de Bloques ===
Cadena de bloques cargada: 60 bloques
Verificando integridad de la cadena de bloques...
La cadena de bloques es íntegra - No hay bloques corruptos
Reporte generado en 'reporte.txt'
```

## Alumno

Josías Vilches

Legajo: 63050

Computación II

## Licencia

Este proyecto es parte de un trabajo práctico académico para la materia Computación II.
