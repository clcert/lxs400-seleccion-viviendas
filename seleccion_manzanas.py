import requests
import csv
import io
import json
import clcert_chachagen
import numpy as np
import argparse
import progressbar
import sys
import datetime


def esc(code):
    return f'\033[{code}m'


def format_date(s):
    date = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.000Z')
    return date.strftime('%d/%m/%Y %H:%M:%S UTC')


widgets = [
    '(', progressbar.SimpleProgress(format='%(value_s)s/%(max_value_s)s'), ') ',
    progressbar.Bar(left='[', right='] '), progressbar.Percentage(),
]

parser = argparse.ArgumentParser(description='Los 500 - Selección aleatoria de Manzanas Censales.')
parser.add_argument('-v', dest='viviendas', action="store", required=True, type=int,
                    help="Número de viviendas a seleccionar. (Obligatorio)")
parser.add_argument('-f', dest='date', action="store", default="", type=str,
                    help="Fecha (formato Epoch con milisegundos) del pulso que será utilizado como semilla aleatoria. (Por defecto último pulso generado)")
args = parser.parse_args()

print('[Los 500] Selección Aleatoria de Manzanas Censales\n')
print('🏠 Seleccionando ', args.viviendas, ' manzanas censales 🏠')

## 1° Obtener datos (manzanas censales) desde INE y construir listas para su posterior uso

print('(1/5) Descargando base de datos desde sitio del INE... ', end='', flush=True)

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

print(esc('32') + 'ok' u'\u2713' + esc(0))

## 2° Obtener semilla aleatoria desde Random UChile

print('(2/5) Obteniendo pulso aleatorio desde Random UChile... ', end='', flush=True)

if args.date == "":
    pulse_url = "https://random.uchile.cl/beacon/2.0/pulse/last"
else:
    pulse_url = "https://random.uchile.cl/beacon/2.0/pulse/time/" + args.date
pulse = json.loads(requests.get(pulse_url).content)["pulse"]
pulse_date = format_date(pulse["timeStamp"])
pulse_index = str(pulse["chainIndex"]) + '-' + str(pulse["pulseIndex"])
pulse_uri = str(pulse["uri"])
seed = pulse["outputValue"]

print(esc('32') + 'ok' u'\u2713' + esc(0))

## 3° Crear objeto PRNG con la semilla obtenida en el paso anterior

print('(3/5) Construyendo PRNG con la semilla obtenida... ', end='', flush=True)

chacha_prng = clcert_chachagen.ChaChaGen(seed)

print(esc('32') + 'ok' u'\u2713' + esc(0))

## 4° Seleccionar aleatoriamente las 30.000 manzanas (ponderadas por total de viviendas)

fids_seleccionados = []
fids_seleccionados_agrupados = {}
for i in progressbar.progressbar(range(args.viviendas), widgets=widgets,
                                 prefix='(4/5) Seleccionando las manzanas al azar... ', suffix='\r'):
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
        fids_seleccionados.append(x)
        fids_seleccionados_agrupados[x] = 1

sys.stdout.write("\033[F")
sys.stdout.write("\033[K")
print('(4/5) Seleccionando las manzanas al azar... ' + esc('32') + 'ok' u'\u2713' + esc(0))

## 5° Generar archivos de salida con las manzanas seleccionadas

print('(5/5) Generando archivos con los resultados... ', end='', flush=True)

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

print(esc('32') + 'ok' u'\u2713' + esc(0))

print('🏠 ¡Selección realizada con éxito! 🏠')

print('\nResumen de la Selección')
print('‣ Fecha pulso aleatorio: ' + pulse_date + ' (' + pulse_uri + ')')
print('‣ Número de manzanas distintas: ' + str(len(fids_seleccionados_agrupados)))

print('\n🎲 Random UChile 🎲')
print('Entra a https://random.uchile.cl/los500 para mayor información')
