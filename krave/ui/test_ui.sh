#!/bin/python3

import time
import csv
import os

print("RUNNING...")

# Archivos de entrada y salida
path_input_file = '/home/ricardo/krave/krave/ui/test_data/events_2024-06-11_11-06-27_RZ041.txt'
path_output_file = '/home/ricardo/krave/krave/ui/test_data/test.csv'

# Abrir el archivo de entrada y el archivo de salida
with open(path_input_file, 'r') as infile, open(path_output_file, 'w', newline='') as outfile:
    # Leer todas las líneas del archivo de entrada
    reader = infile.readlines()
    
    # Copiar cada línea del archivo de entrada al archivo de salida cada 0.1 segundos    cont = 0
    cont = 0
    aux = 0
    for line in reader:
        if cont == 0:
            cont += 1
            aux = line
            continue
        elif cont == 1:
            outfile.write(aux)
            outfile.flush()
            os.fsync(outfile.fileno())  
            outfile.write(line)  
            outfile.flush()
            os.fsync(outfile.fileno())  
            cont += 1
            #break

        else: 
            outfile.write(line)
            outfile.flush()
            os.fsync(outfile.fileno())    # Escribir la línea directamente
        time.sleep(0.05)
print("----END----")