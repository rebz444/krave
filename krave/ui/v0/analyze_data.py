import pygame
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
from button_class import Button
from krave.ui.debugging.graph_class import Graph
from button_refresh_class import RefreshButton
from krave.ui.constants import *
import tkinter as tk
from tkinter import filedialog
from button_select_data_class import SelectData
from threading import Thread
import os
import time
import csv
from PIL import Image

def analyze_data(file_path):
    new_headers = ["trial", "bg_repeat", "wait_time", "miss_trial"]
    new_rows = []
    #READ DATA
    data = pd.read_csv(file_path, delimiter = ",")
    #x = data[self._name_x].astype("int").tolist()
    #y = data[self._name_y].astype("int").tolist()

    #GET FILE NAME AND REMOVE EXTENSION (EX: .csv)
    headers = data.columns.tolist()  
    print(headers) #prints headers
    #print(data) #prints all data
    #print(data[headers[1]]) #prints the column without the header
    #print(len(data))
    
    #print(data.iloc[0][0])  #print de elemento de la fila específica

    index = 0
    actual_trial = 0
    number_background = 0
    initial_time = 0
    final_time = 0
    wait_time = 0
    miss_trial = False
    consumption = False
    while(index < (len(data) - 1)): #HAY QUE COMPROBAR EL ULTIMO ELEMENTO!!!!!        
        #print("YE ARE IN: ", index)
        actual_row = data.iloc[index]
        next_row = data.iloc[index + 1]

        actual_trial = actual_row[3]
        next_trial = next_row[3]
        #Count background
        if actual_trial == next_trial:
            if (actual_row[-1] == "background"):
                number_background += 1
        else:
            if (actual_row[-1] == "background"):
                number_background += 1
            
            if (consumption == False):
                miss_trial = True
            print(actual_trial, number_background, wait_time, miss_trial)
            new_rows.append([actual_trial, number_background, wait_time, miss_trial])
            number_background = 0
            initial_time = 0
            final_time = 0
            wait_time = 0
            miss_trial = False
            actual_trial += 1            

        #Count wait time
        if actual_row[-1] == "wait":
            initial_time = actual_row[0]
        if actual_row[-1] == "consumption":
            final_time = actual_row[0]
            wait_time = final_time - initial_time
            consumption = True
        index += 1
    
    #We need to check the last output of the file
    #Creo que no se necesita porque el background nunca puede ser el ultimo -
    #-output del sistema
    index += 1
    actual_row = data.iloc[-1]
    if (actual_row[-1] == "background"):
        number_background += 1
    print(actual_trial, number_background, wait_time, miss_trial)
    new_rows.append([actual_trial, number_background, wait_time, miss_trial])

    #Now we add everything to the new file

    new_file_name = "analized_data.csv"
    with open(new_file_name, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(new_headers)
        writer.writerows( new_rows[1:len(new_rows)]) #We dont want the -1



root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("TXT files", ".txt"), ("CSV files", "*.csv")])
root.destroy()

if not file_path:
    print("No se seleccionó ningún archivo.")

def plot_data(file_path, file_path2):

    direcroty_path = os.getcwd()
    img_path = os.path.join(direcroty_path, "graph_analyzed_data.png")

    data = pd.read_csv(file_path, delimiter = ",")
    headers = data.columns.tolist()

    file_name = os.path.splitext(os.path.basename(file_path2))[0]

    '''plt.subplots(figsize=(12, 6))
    plt.subplots_adjust(right=0.85)'''


    max_wait_time = 0

    for index, row in data.iterrows():
        if row[-1] == False:
            plt.plot(row["trial"], row["wait_time"], linestyle="", marker="o", color = "black")
        else:
            plt.axvspan(index - 0.5, index + 0.5, color = "red", alpha = 0.25)
        
        max_wait_time = max(max_wait_time, row["wait_time"])
    
    false_data = data[data['miss_trial'] == False]
    plt.plot(false_data['trial'], false_data['wait_time'], '-', color='gray', alpha=0.5)

    h1 = max_wait_time + (max_wait_time / 100 * 10)
    h2 = max_wait_time + (max_wait_time / 100 * 15)
    h3 = max_wait_time + (max_wait_time / 100 * 20)
    
    plt.plot([0, len(data) - 1],[ h1,h1], color = "black")
    plt.plot([0, len(data) - 1],[ h3,h3], color = "black")

    plt.xlabel("trial #")
    plt.ylabel("t (s)")
    plt.title(file_name)

    for index, row in data.iterrows():
        plt.text(row["trial"], h2, str(row["bg_repeat"]), fontsize=12, color='lightseagreen', ha='center', va='center', alpha=0.5)
    
    #TO INDICATE THE LEGENDS OF THE GRAPH WE CREATE A POINT WITH THE SAME COLOR
    #AND WE ASIGN A LABEL
    plt.plot([],[], color = "black", label = "wait time")
    plt.plot([],[], color = "lightseagreen", label = "bg repeat", )
    #plt.subplots_adjust(right=0.75) #Margen al exterior del grafico (se comprime el grafico :|)
    #plt.legend(handletextpad=1, markerscale=15, loc='lower left', bbox_to_anchor=(1, 1))



    try:
        plt.savefig(img_path)
    except Exception as e:
        print(f"Error al guardar la imagen: {e}")

    #REDIMENSIONAR IMAGEN - PUEDE FALLAR
    imagen = Image.open(img_path)
    nuevo_tamano = (450, 350)  # Ejemplo: ancho de 400px, alto de 300px

    # Redimensionar la imagen
    imagen_redimensionada = imagen.resize(nuevo_tamano)

    # Guardar la imagen redimensionada
    imagen_redimensionada.save('graph_analyzed_data_resized.png')

    

analyze_data(file_path)
input("Press ENTER to continue ")
plot_data("/home/ricardo/graphImg/analized_data.csv", file_path)