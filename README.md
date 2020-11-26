![](https://www.clcert.cl//img/logo.svg)

# Los 500 - Selección Aleatoria de Manzanas Censales e Índices de Viviendas

El primer paso para la selección de ciudadanas y ciudadanos de manera aleatoria que participarán en el proyecto "Los 500" es la selección aleatoria de viviendas, las cuales se elegirán a partir de una selección aleatoria de manzanas censales repartidas en todo Chile.

## Algoritmo de Selección

### Paso 1: Selección de Manzanas Censales (`seleccion_manzanas.py`)

1. Se extrae desde el sitio web del INE, los datos de las manzanas censales totales correspondientes al censo 2017.
2. Se extrae desde el Faro de Aleatoriedad el pulso correspondiente a la fecha previamente establecida para la ceremonia de selección de manzanas. Este pulso se utilizará como semilla aleatoria para alimentar a un PRNG (generador pseudo-aleatorio).
3. Se pondera cada manzana censal con respecto al total de viviendas que posee dicha manzana. Se eligen 30.000 manzanas tomando en cuenta la ponderación realizada en cada manzana. Pueden ser seleccionadas manzanas repetidas, en dicho caso se debe guardar las veces que fue seleccionada cada manzana.

### Paso 2: Selección de índices de viviendas en cada Manzana (`seleccion_indices_viviendas.py`) 

1. Se extrae desde el Faro de Aleatoriedad el pulso correspondiente a la fecha previamente establecida para la ceremonia de selección de viviendas. Este pulso se combinará (usando algoritmo HMAC) con un valor aleatorio secreto previamente definido para derivar la semilla aleatoria que se utilizará para alimentar a un PRNG (generador pseudo-aleatorio).

2. Por cada manzana censal seleccionada en el Paso 1 se escogerán de manera aleatoria tantos índices como veces fue seleccioanda dicha manzana en el rango [1, N], siendo N = total de viviendas en dicha manzana.

## Ejecución de los scripts

### 1. Instalar requisitos

```
$ pip install -r requirements.txt
```

### 2. Ejecutar selección de manzanas

```
$ python seleccion_manzanas.py -f [FECHA_PULSO] -v [NUM_VIVIENDAS]
```
Argumentos:
- `-f [FECHA_PULSO]`: fecha (hora UTC) del pulso aleatorio que se utilizará, en formato Epoch Unix con milisegundos. Visitar https://www.epochconverter.com/ para convertir una fecha en dicho formato.
- `-v [NUM_VIVIENDAS]`: número de viviendas a seleccionar de manera aleatoria.

Se generan dos archivos:
1. `resultados_manzanas_detalle.csv`: detalle de todas las distintas manzanas escogidas (identificador único, veces que fue seleccionada y ubicación geográfica hasta el nivel de distrito).
2. `resultados_fids.csv`: lista de los 30.000 identificadores de las manzanas seleccionadas.

### 3. Ejecutar selección de índices de viviendas

```
$ python seleccion_indices_viviendas.py -s [SECRETO] -f [FECHA_PULSO] -n [NUMERO_ARCHIVOS]
```
Argumentos:
- `-s [SECRETO]`: valor aleatorio secreto en formato hexadecimal.
- `-f [FECHA_PULSO]`: fecha del pulso aleatorio que se utilizará, en formato Epoch Unix con milisegundos. Visitar https://www.epochconverter.com/ para convertir una fecha en dicho formato.
- `-n [NUMERO_ARCHIVOS]`: número de archivos a generar con los resultados de los índices de viviendas seleccionadas.

Se generan los siguientes archivos (relacionados con el argumento `-n`):
1. `resultados_indices_viviendas_<X>.csv`: lista de índices de viviendas escogidas por cada manzana censal seleccionada. Se generar `-n` archivos distintos, diferenciándose en el número `<X>` de cada uno.
