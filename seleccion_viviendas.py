import csv
import clcert_chachagen
import json
import requests
import io

## 1° Obtener semilla aleatoria desde Random UChile

pulse_url = "https://random.uchile.cl/beacon/2.0/pulse/last"
seed = json.loads(requests.get(pulse_url).content)["pulse"]["outputValue"]

## 2° Crear objeto PRNG con la semilla obtenida en el paso anterior

chacha_prng = clcert_chachagen.ChaChaGen(seed)

## 3° Revisar cuantas veces fue seleccionada cada manzana y escoger índices de viviendas a escoger

input_filename = "resultados_manzanas_detalle.csv"
viviendas_seleccionadas = []
with open(input_filename, 'rt') as input_file:
    reader = csv.DictReader(io.StringIO(input_file.read()))
    for row in reader:
        times = row['TIMES_SELECTED']
        total = row['TOTAL_VIVIENDAS']
        selected_indexes = chacha_prng.sample(range(int(total)), int(times))
        viviendas_seleccionadas.append({'MANZENT': row['MANZENT'],
                                        'INDEX_VIVIENDAS': list(map(lambda x: x+1, selected_indexes))})

## 4° Generar archivo de salida con los índices de las viviendas seleccionadas

output_filename = "resultados_indices_viviendas.csv"
out_columns = ['MANZENT', 'INDEX_VIVIENDAS']
with open(output_filename, 'w') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=out_columns)
    writer.writeheader()
    for vivienda in viviendas_seleccionadas:
        writer.writerow({'MANZENT': vivienda['MANZENT'], 'INDEX_VIVIENDAS': vivienda['INDEX_VIVIENDAS']})
