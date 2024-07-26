import pygame
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
#from krave.ui.constants import Colors, PATHS, DEFAULT_FPS, DEFAULT_UPDATE_TIME_SECONDS, DATA_HEADERS
from constants import Colors, PATHS, DEFAULT_FPS, DEFAULT_UPDATE_TIME_SECONDS, DATA_HEADERS
import tkinter as tk
from tkinter import filedialog
from threading import Thread
import os
import time
import warnings
#Ignore warnings from matplotlib (ser.iloc[pos] is deprecated)
warnings.simplefilter(action="ignore", category=FutureWarning)
import csv
from PIL import Image


class UI():
    """Object to run a UI for a mouse experiment."""
    def __init__(self, source_data_path = None, fps = DEFAULT_FPS, update_time_seconds = DEFAULT_UPDATE_TIME_SECONDS) -> None:
        self._source_data_path = source_data_path
        self._pygame_window = None
        self._pygame_clock = None
        self._FPS = fps
        self._update_time_seconds = update_time_seconds

        # UI Loop parameters
        self._index = None
        self._last_trial = None
        self._initial_index = None
        self._first_change = None
        self._last_mod_time = None

    def _prompt_for_data_file(self):
        """Ask user to provide path to the data file. Always before initializing pygame"""
        root = tk.Tk()
        root.withdraw()
        self._source_data_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("TXT files", ".txt")])
        root.destroy()

        if not self._source_data_path:
            raise("No file was selected.")
        return self._source_data_path

    def _init_pygame(self):
        """initialize pygame (we check if we have already created it)"""
        if not self._pygame_window:    
            pygame.init()
            WIDTH, HEIGHT = 500, 400
            self._pygame_window = pygame.display.set_mode((WIDTH, HEIGHT))
            self._pygame_clock = pygame.time.Clock()
            pygame.display.set_caption("HSL project")
            self._pygame_window.fill(Colors.WHITE)
    
    def _quit_pygame(self):
        """end pygame and krave"""
        pygame.quit()
    
    def _init_analyzed_data_file(self):
        """create real_time_analized_data.csv file and place headers (to store analized data)"""
        new_headers = [DATA_HEADERS.TRIAL, DATA_HEADERS.BG_REPEAT, DATA_HEADERS.WAIT_TIME, DATA_HEADERS.MISS_TRIAL]
        with open(PATHS.TEMP_ANALYZED_DATA, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(new_headers)
    
    def _init_ui_loop_parameters(self):
        """initialize variables for check_for_data_update function in the main loop"""
        self._index = 0
        self._last_trial = -1
        self._initial_index = 1
        self._first_change = False
        self._last_mod_time = os.path.getmtime(self._source_data_path)
        # TODO(r.hueto@icloud.com): Remove total_trials when connected with main krave loop.
        self._total_trials = 42
    
    def _check_pygame_quit_event(self):
        """check for events in pygame to quit the main loop and end program"""
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
        return True

    def plot_data(self):
        """This functions reads the file created with the analized data and plots it
        Maybe more work on legend"""

        #load data
        data = pd.read_csv(PATHS.TEMP_ANALYZED_DATA, delimiter = ",")

        #Get the name of the file with now extencion (ex: example.csv --> example)
        file_name = os.path.splitext(os.path.basename(self._source_data_path))[0]

        max_wait_time = 0 #this helps us generate the top numbers so it is not superposed with the data

        #We plot the wait times. If it is a miss trial (row[-1] == True) then we dont plot the value but we
        #do a red square indicating is a miss
        for index, row in data.iterrows():
            if row[-1] == False:
                plt.plot(row[DATA_HEADERS.TRIAL], row[DATA_HEADERS.WAIT_TIME], linestyle="", marker="o", color = "black")
            else:
                plt.axvspan(index - 0.5, index + 0.5, color = "red", alpha = 0.25)
            
            max_wait_time = max(max_wait_time, row[DATA_HEADERS.WAIT_TIME])
        
        #we get all the data that is not a miss trial and plot it with lines (it also joins the space of miss trials, maybe review)
        false_data = data[data[DATA_HEADERS.MISS_TRIAL] == False] 
        plt.plot(false_data[DATA_HEADERS.TRIAL], false_data[DATA_HEADERS.WAIT_TIME], '-', color='gray', alpha=0.5)

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
            plt.text(row[DATA_HEADERS.TRIAL], h2, str(row[DATA_HEADERS.BG_REPEAT]), fontsize=12, color='lightseagreen', ha='center', va='center', alpha=0.5)
        
        #TO INDICATE THE LEGENDS OF THE GRAPH WE CREATE A POINT WITH THE SAME COLOR
        #AND WE ASIGN A LABEL (currenly disablabled, not working the position)
        plt.plot([],[], color = "black", label = "wait time")
        plt.plot([],[], color = "lightseagreen", label = "bg repeat", )
        #plt.subplots_adjust(right=0.75) #Margen al exterior del grafico (se comprime el grafico :|)
        #plt.legend(handletextpad=1, markerscale=15, loc='lower left', bbox_to_anchor=(1, 1))

        try:
            plt.savefig(PATHS.TEMP_IMG)
        except Exception as e:
            print(f"Error al guardar la imagen: {e}")

        #Resize image - PUEDE FALLAR
        imagen = Image.open(PATHS.TEMP_IMG)
        nuevo_tamano = (450, 350) #width and height
        imagen_redimensionada = imagen.resize(nuevo_tamano)

        # Save image with new name
        imagen_redimensionada.save(PATHS.TEMP_IMG_RESIZED)
    
    def draw(self):
        """loads graph image and draws elements in the pygame window"""
        self._pygame_window.fill(Colors.WHITE)
        img = pygame.image.load(PATHS.TEMP_IMG_RESIZED)
        self._pygame_window.blit(img, (25,0))
        pygame.display.update()
    
    def check_for_data_update(self):
        """check for updates in the self._source_data_path file and if there is an update it analizes the new rows of the file,
        copies the new analized data to the TEMP_ANALIZED_DATA file and plots with this file. Skip first modification (headers) 
        and trial -1 is not ploted or saved in the TEMP_ANALIZED_DATA file"""

        print(self._index, self._last_trial)

        if detect_change(self._source_data_path, self._last_mod_time):
            if self._first_change != False:
                print("----CHANGE DETECTED----")
                #Get new mod date
                self._last_mod_time = os.path.getmtime(self._source_data_path)

                #Load data, num of rows and diference from the index we are in and the num of rows
                reader = csv.reader(open(self._source_data_path))
                num_rows = len(list(reader))
                data = pd.read_csv(self._source_data_path, delimiter = ",")

                diff = (num_rows - 2) - self._index #New rows added since last check
                #print("NUMBER OF ROWS:", num_rows, "DIFF:", diff)

                sortida = None

                #Iterate throught all the new rows
                for i in range(diff):
                    new_index = self._index + 1 + i
                    #print("NEW INDEX: ", new_index)
                    sortida = analyze_data(data, new_index, self._initial_index, self._last_trial)

                    if sortida:
                        #print("OUTPUT: ", sortida)
                        self._initial_index = new_index

                        #We dont want to plot the trial -1 (isnt a real trial) 
                        if self._last_trial != -1:

                            #We add the new analized data to the file to plot
                            with open(PATHS.TEMP_ANALYZED_DATA, "a", newline="") as file:
                                writer = csv.writer(file)
                                writer.writerow(sortida)
                            
                            #We plot the data from the analized file
                            self.plot_data()
                        self._last_trial += 1
                
                self._index = new_index

            else:
                self._first_change = True
                self._last_mod_time = os.path.getmtime(self._source_data_path)

            self._index += 1

    def run(self):
        """Run main UI thread."""
        if not self._source_data_path:
            self._source_data_path = self._prompt_for_data_file()
        self._init_pygame()
        self._init_analyzed_data_file()
        self._init_ui_loop_parameters()
        
        run = True
        start_time = time.time()
        while run:
            # Run UI update every {update_time_seconds} seconds.
            current_time = time.time()
            diff_time = current_time - start_time
            if diff_time >= self._update_time_seconds:
                start_time = time.time()
                self.check_for_data_update()

            self._pygame_clock.tick(self._FPS)
            self.draw()
            run = self._check_pygame_quit_event()

        self._quit_pygame()

#FUNCTIONS
def analyze_data(data, index, initial_index, last_trial):
    '''check in the self._source_data_path in the index row if we start a new trial. 
    if we started one then we check if it's a miss trial, the wait time and the backgrounds  '''

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

def detect_change(source_data_path, time_last_mod):
    """This functions detetcts if there has been a modification in the file with the date"""
    time_mod = os.path.getmtime(source_data_path)
    if (time_mod != time_last_mod):
        return True
    return False

if __name__ == '__main__':
    '''runs only if direclty executed, no execution if imported (then you need to call main())'''
    UI().run()