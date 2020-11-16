import csv
import clcert_chachagen
import json
import requests
import io
import argparse
import hmac
import hashlib
import datetime


def esc(code):
    return f'\033[{code}m'


def format_date(s):
    date = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.000Z')
    return date.strftime('%d/%m/%Y %H:%M:%S UTC')


parser = argparse.ArgumentParser(description='Los 400 - Selección aleatoria de Índices de Viviendas.')
parser.add_argument('-s', dest='secret', action="store", default="", type=str,
                    help="Valor aleatorio (en hexadecimal) secreto que será combinado con el pulso aleatorio público. (Por defecto sín secreto)")
parser.add_argument('-f', dest='date', action="store", default="", type=str,
                    help="Fecha (formato Epoch con milisegundos) del pulso aleatorio público que será utilizado. (Por defecto último pulso generado)")
args = parser.parse_args()

print('[Los 400] Selección Aleatoria de Índices de Viviendas\n')

print('🏠 Seleccionando índices de viviendas 🏠')

## 1° Obtener semilla aleatoria desde Random UChile

print('(1/4) Obteniendo pulso aleatorio desde Random UChile... ', end='', flush=True)

if args.date == "":
    pulse_url = "https://random.uchile.cl/beacon/2.0/pulse/last"
else:
    pulse_url = "https://random.uchile.cl/beacon/2.0/pulse/time/" + args.date

print(esc('32') + 'ok' u'\u2713' + esc(0))

## 2° Construir semilla aleatorio combinando secreto y pulso (HMAC), y crear PRNG con dicha semilla aleatoria

print('(2/4) Construyendo semilla aleatoria y PRNG combinando pulso con secreto... ', end='', flush=True)

pulse = json.loads(requests.get(pulse_url).content)["pulse"]
pulse_date = format_date(pulse["timeStamp"])
pulse_index = str(pulse["chainIndex"]) + '-' + str(pulse["pulseIndex"])
pulse_uri = str(pulse["uri"])
pulse_value = pulse["outputValue"]
seed = hmac.HMAC(bytes.fromhex(args.secret), bytes.fromhex(pulse_value), hashlib.sha3_512).hexdigest()
chacha_prng = clcert_chachagen.ChaChaGen(seed)

print(esc('32') + 'ok' u'\u2713' + esc(0))

## 3° Revisar cuantas veces fue seleccionada cada manzana y escoger índices de viviendas a escoger

print('(3/4) Seleccionando aleatoriamente los índices de las viviendas en cada manzana... ', end='', flush=True)

input_filename = "resultados_manzanas_detalle.csv"
viviendas_seleccionadas = []
with open(input_filename, 'rt') as input_file:
    reader = csv.DictReader(io.StringIO(input_file.read()))
    for row in reader:
        total = row['TOTAL_VIVIENDAS']
        times = row['TIMES_SELECTED']
        selected_indexes = chacha_prng.sample(range(1, int(total) + 1), int(times))
        viviendas_seleccionadas.append({'MANZENT': row['MANZENT'],
                                        'INDICES_VIVIENDAS': selected_indexes})

print(esc('32') + 'ok' u'\u2713' + esc(0))

## 4° Generar archivo de salida con los índices de las viviendas seleccionadas

print('(4/4) Generando archivo con los resultados... ', end='', flush=True)

output_filename = "resultados_indices_viviendas.csv"
out_columns = ['MANZENT', 'INDICE_VIVIENDA']
with open(output_filename, 'w') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=out_columns)
    writer.writeheader()
    counter = 0
    for vivienda in viviendas_seleccionadas:
        for index in sorted(vivienda['INDICES_VIVIENDAS']):
            counter += 1
            writer.writerow({'MANZENT': vivienda['MANZENT'], 'INDICE_VIVIENDA': index})
print(esc('32') + 'ok' u'\u2713' + esc(0))

print('🏠 ¡Selección realizada con éxito! 🏠')

print('\nResumen de la Selección')
print('‣ Fecha pulso aleatorio: ' + pulse_date + ' (' + pulse_uri + ')')
print('‣ Número de viviendas seleccionadas: ' + str(counter))

print('\n🎲 Random UChile 🎲')
print('Entra a https://random.uchile.cl/los400 para mayor información')
