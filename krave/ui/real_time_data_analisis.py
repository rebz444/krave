import pygame
import matplotlib.pyplot as plt
import pandas as pd
from button_class import Button
from graph_class import Graph
from button_refresh_class import RefreshButton
from colors_list import *
import tkinter as tk
from tkinter import filedialog
from button_select_data_class import SelectData
from threading import Thread
import os
import time
import csv
from PIL import Image
import warnings

#Ignore warnings from matplotlib (ser.iloc[pos] is deprecated)
warnings.simplefilter(action="ignore", category=FutureWarning)

#FUNCTIONS
def analyze_data(data, index, initial_index, last_trial, total_trials):
    #In this function we check if we started a new trial (with the actual row)
    #if we started one then we check if it's a miss trial, the wait time and the backgrounds

    actual_row = data.iloc[index]
    actual_trial = actual_row[3]

    consumption = False
    wait_time = 0
    miss_trial = False

    if (actual_trial != last_trial):
        number_background = 0
        initial_time = 0
        final_time = 0

        final_index = index - 1

        data_interval = data[initial_index:final_index + 1]
        for index, row in data_interval.iterrows():
            if (row[-1] == "background"):
                number_background += 1
            
            elif (row[-1] == "wait"):
                initial_time = row[0]
            
            elif (row[-1] == "consumption"):
                final_time = row[0]
                wait_time = final_time - initial_time
                consumption = True
        
        if (consumption == False):
                miss_trial = True
        return([last_trial, number_background, wait_time, miss_trial])

    else:

        return (False)

    
    

def plot_data(file_path, file_path2, img_path):
    #This functions reads the file created with the analized data and plots it
    #Maybe more work on legend

    #load data
    data = pd.read_csv(file_path, delimiter = ",")

    #Get the name of the file with now extencion (ex: example.csv --> example)
    file_name = os.path.splitext(os.path.basename(file_path2))[0]

    max_wait_time = 0 #this helps us generate the top numbers so it is not superposed with the data

    #We plot the wait times. If it is a miss trial (row[-1] == True) then we dont plot the value but we
    #do a red square indicating is a miss
    for index, row in data.iterrows():
        if row[-1] == False:
            plt.plot(row["trial"], row["wait_time"], linestyle="", marker="o", color = "black")
        else:
            plt.axvspan(index - 0.5, index + 0.5, color = "red", alpha = 0.25)
        
        max_wait_time = max(max_wait_time, row["wait_time"])
    
    #we get all the data that is not a miss trial and plot it with lines (it also joins the space of miss trials, maybe review)
    false_data = data[data['miss_trial'] == False] 
    plt.plot(false_data['trial'], false_data['wait_time'], '-', color='gray', alpha=0.5)

    #we get the different heights to create the top numbres (bg repeat)
    h1 = max_wait_time + (max_wait_time / 100 * 10)
    h2 = max_wait_time + (max_wait_time / 100 * 15)
    h3 = max_wait_time + (max_wait_time / 100 * 20)
    
    #plot the two black lines of separration
    plt.plot([0, len(data) - 1],[ h1,h1], color = "black")
    plt.plot([0, len(data) - 1],[ h3,h3], color = "black")

    #Name of axixs and title(name of the file we are getting the data from originally, no analized)
    plt.xlabel("trial #")
    plt.ylabel("t (s)")
    plt.title(file_name)

    #Plot the numbers (bg repeat)
    for index, row in data.iterrows():
        plt.text(row["trial"], h2, str(row["bg_repeat"]), fontsize=12, color='lightseagreen', ha='center', va='center', alpha=0.5)
    
    #TO INDICATE THE LEGENDS OF THE GRAPH WE CREATE A POINT WITH THE SAME COLOR
    #AND WE ASIGN A LABEL (currenly disablabled, not working the position)
    plt.plot([],[], color = "black", label = "wait time")
    plt.plot([],[], color = "lightseagreen", label = "bg repeat", )
    #plt.subplots_adjust(right=0.75) #Margen al exterior del grafico (se comprime el grafico :|)
    #plt.legend(handletextpad=1, markerscale=15, loc='lower left', bbox_to_anchor=(1, 1))

    try:
        plt.savefig(img_path)
    except Exception as e:
        print(f"Error al guardar la imagen: {e}")

    #Resize image - PUEDE FALLAR
    imagen = Image.open(img_path)
    nuevo_tamano = (450, 350) #width and height
    imagen_redimensionada = imagen.resize(nuevo_tamano)

    # Save image with new name
    imagen_redimensionada.save('graph_analyzed_data_resized.png')

    

def detect_change(file_path, time_last_mod):
    #This functions detetcts if there has been a modification in the file with the date

    time_mod = os.path.getmtime(file_path)
    if (time_mod != time_last_mod):
        return True
    else:
        return False


#INITIALIZATION

#Get the file where the data is being written
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("TXT files", ".txt")])
root.destroy()

if not file_path:
    print("No se seleccionó ningún archivo.")

#Get last odification date
last_mod_time = os.path.getmtime(file_path)

#Indicate the name of the new file where the analized data will be written
#Writte the heades of the new file
new_headers = ["trial", "bg_repeat", "wait_time", "miss_trial"]
new_file_name = "real_time_analized_data.csv"
with open(new_file_name, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(new_headers)

#Initialice variables
index = 0
total_trials = 42
new_rows = []
last_trial = -1
initial_index = 1
first_change = False
num_rows = 2

direcroty_path = os.getcwd() #get the current directory
img_path = os.path.join(direcroty_path, "graph_analyzed_data.png") #we create the new path. CHANGE FOR NEW IMAGE NAME

print("RUNNING...")

#MAIN LOOP
#For this initial testing we need to indicate the number of index and the number of trials
#But for the final one we will wait for one function to say that we ended writting the file
#Now it does not graph the last trial bcs it can't detect it finished. Needed implementation
#to plot the last trial when the doc is finished writting

while(last_trial <= 42 and index <= 3488):
    #print(index, last_trial)
    time.sleep(5) #ADJUST TO SET THE REFRESH RATE OF THE GRAPH!!!

    if detect_change(file_path, last_mod_time) == True:
        if first_change != False:
            #print("----CHANGE DETECTED----")

            #Get new mod date
            last_mod_time = os.path.getmtime(file_path)

            #Load data, num of rows and diference from the index we are in and the num of rows
            reader = csv.reader(open(file_path))
            num_rows = len(list(reader))
            data = pd.read_csv(file_path, delimiter = ",")

            diff = (num_rows - 2) - index #New rows added since last check
            #print("NUMBER OF ROWS:", num_rows, "DIFF:", diff)

            #Iterate throught all the new rows
            for i in range(diff):
                new_index = index + 1 + i
                #print("NEW INDEX: ", new_index)
                sortida = analyze_data(data, new_index, initial_index, last_trial, total_trials)

                if sortida != False:
                    #print("OUTPUT: ", sortida)
                    new_rows.append(sortida)
                    initial_index = new_index

                    #We dont want to plot the trial -1 (isnt a real trial) 
                    if last_trial != -1:

                        #We add the new analized data to the file to plot
                        with open(new_file_name, "a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(sortida)
                        
                        #We plot the data from the analized file
                        direcroty_path = os.getcwd() #get the current directory
                        new_file_path = os.path.join(direcroty_path, "real_time_analized_data.csv")
                        plot_data(new_file_path, file_path, img_path)
                    last_trial += 1
            
            index = new_index

        else:
            first_change = True
            last_mod_time = os.path.getmtime(file_path)

        index += 1

#Final plot because why not :)
plot_data(new_file_path, file_path, img_path)

print("END - graph saved at ",img_path)