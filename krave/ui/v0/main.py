import pygame
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
from button_class import Button
from button_refresh_class import RefreshButton
from krave.ui.constants import Colors
import tkinter as tk
from tkinter import filedialog
from button_select_data_class import SelectData
from threading import Thread
import os
import time

#INITIALIZE PROYECT
"""if not file_path:
    print("No se seleccionó ningún archivo. Saliendo del programa.")
    exit()""" #PONER EN LA ACTIVACIÓN DEL OBJETO CON LAS COORDENADAS

pygame.init()
WIDTH, HEIGHT = 500, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HSL project")

#FUNCTIONS

def draw():
    win.fill(Colors.WHITE)
    #win.blit(graph, (WIDTH / 2 - (img_width / 2), 0))
    grafico.draw(win)
    buttonRefresh.draw("REFRESH", win)
    buttonSelectData.draw("SELECT FILE", win)
    pygame.display.update()

#creamos un threat para poder abrir una nueva ventana
def get_path(button):
    return buttonSelectData.activate()


def normalice_color(color_rgb):
    r, g, b = color_rgb
    return (r / 255, g / 255, b / 255)

def detect_change(file_path, time_last_mod):
    time_mod = os.path.getmtime(file_path)
    if (time_mod != time_last_mod):
        return True
    else:
        return False

#OBJECTS
buttonRefresh = RefreshButton(100,342,100,50, Colors.BLACK)
buttonSelectData = SelectData(260,342,150,50, Colors.BLACK)

#FIRST SELECTION OF DATA
file_path = buttonSelectData.activate()
if not file_path:
    print("No se seleccionó ningún archivo.")

last_mod_time = os.path.getatime(file_path)

#MAIN LOOP
win.fill(Colors.WHITE)
run = True

FPS = 15
proceso = False #Para comprovar si ha acabado el hilo y que no se ponga a imprimir todo el rato que no hay archivo
clock = pygame.time.Clock()

while run:
    
    if detect_change(file_path, last_mod_time) == True:
        last_mod_time = os.path.getmtime(file_path)
        grafico.refresh()
    clock.tick(FPS)
    

    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if pygame.mouse.get_pressed()[0]:
            m_x, m_y = pygame.mouse.get_pos()
            print(m_x, m_y)
            if buttonRefresh.pressed(m_x, m_y) == True:
                buttonRefresh.activate(grafico)
            
            if buttonSelectData.pressed(m_x, m_y) == True:
                thread = Thread(target=get_path, args=(buttonSelectData,))
                new_file_path = thread.start()
                proceso = True
    
    if 'thread' in locals() and not thread.is_alive() and proceso:
        new_file_path = buttonSelectData.result 
        #grafico.name_data_document = file_path
        proceso = False
        if not new_file_path:
            print("No se seleccionó ningún archivo.")
        else:
            file_path = new_file_path
            grafico.name_data_document = file_path
            grafico.refresh()
            #m_x, m_y = 0, 0 #podría causar problemas en un futuro
pygame.quit()
