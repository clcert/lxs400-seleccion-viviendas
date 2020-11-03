import requests
import csv
import io
import json
import clcert_chachagen
import numpy as np

## 1° Obtener datos (manzanas censales) desde INE y construir listas para su posterior uso

data_ine_url = "https://opendata.arcgis.com/datasets/54e0c40680054efaabeb9d53b09e1e7a_0.csv?outSR=%7B%22latestWkid%22" \
               "%3A3857%2C%22wkid%22%3A102100%7D"
response = requests.get(data_ine_url).content.decode('utf-8')
reader = csv.DictReader(io.StringIO(response))
total_viviendas = []
datos_filtrados = []
for row in reader:
    total_viviendas.append(row['TOTAL_VIVIENDAS'])
    datos_filtrados.append({'REGION': row['REGION'],
                            'PROVINCIA': row['PROVINCIA'],
                            'COMUNA': row['COMUNA'],
                            'NOMBRE_DISTRITO': row['NOMBRE_DISTRITO'],
                            'MANZENT': row['MANZENT']})

viviendas_acum_value = 0
viviendas_acumuladas = []
for viviendas in total_viviendas:
    viviendas_acum_value += int(viviendas)
    viviendas_acumuladas.append(viviendas_acum_value)

## 2° Obtener semilla aleatoria desde Random UChile

pulse_url = "https://random.uchile.cl/beacon/2.0/pulse/last"
seed = json.loads(requests.get(pulse_url).content)["pulse"]["outputValue"]

## 3° Crear objeto PRNG con la semilla obtenida en el paso anterior

chacha_prng = clcert_chachagen.ChaChaGen(seed)

## 4° Seleccionar aleatoriamente las 30.000 manzanas (ponderadas por total de viviendas)

fids_seleccionados = []
fids_seleccionados_agrupados = {}
for i in range(30000):
    rnd = chacha_prng.randint(0, 5510076)  # TOTAL VIVIENDAS = 5.510.076
    x = np.searchsorted(viviendas_acumuladas, rnd)
    if x in fids_seleccionados_agrupados:
        updated_times = fids_seleccionados_agrupados[x] + 1
        if updated_times <= int(total_viviendas[x]):
            fids_seleccionados.append(x)
            fids_seleccionados_agrupados[x] = updated_times
        else:
            i -= 1
            continue
    else:
        fids_seleccionados_agrupados[x] = 1

## 5° Generar archivos de salida con las manzanas seleccionadas

### Archivo detallado
out_1_filename = "resultados_manzanas_detalle.csv"
out_columns = ['FID', 'MANZENT', 'TIMES_SELECTED', 'TOTAL_VIVIENDAS',
               'REGION', 'PROVINCIA', 'COMUNA', 'NOMBRE_DISTRITO']
with open(out_1_filename, 'w') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=out_columns)
    writer.writeheader()
    for data in fids_seleccionados_agrupados:
        writer.writerow({'FID': data + 1,
                         'MANZENT': datos_filtrados[data]['MANZENT'],
                         'TIMES_SELECTED': fids_seleccionados_agrupados[data],
                         'TOTAL_VIVIENDAS': total_viviendas[data],
                         'REGION': datos_filtrados[data]['REGION'],
                         'PROVINCIA': datos_filtrados[data]['PROVINCIA'],
                         'COMUNA': datos_filtrados[data]['COMUNA'],
                         'NOMBRE_DISTRITO': datos_filtrados[data]['NOMBRE_DISTRITO']})

### Archivo solamente con fids seleccionados
out_2_filename = "resultados_fids.csv"
out_columns = ['FID']
with open(out_2_filename, 'w') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=out_columns)
    writer.writeheader()
    for fid in fids_seleccionados:
        writer.writerow({'FID': fid + 1})
