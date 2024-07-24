import pandas as pd
import matplotlib.pyplot as plt
import pygame
from PIL import Image
import os

class Graph:
    def __init__(self, x, y, name_data_document, color):
        self._x = x
        self._y = y
        self._name_data_document = name_data_document
        self._name_x = "Loading"
        self._name_y = "Loading"
        self._image_width = 0
        self._image_height = 0
        self._name_label = "Loading"
        self._color = color
        self._graph = 0
        self._file_name = "Loading"


        self.refresh()
    
    @property
    def name_data_document(self):
        return self._name_data_document
    @name_data_document.setter
    def name_data_document(self, name):
        self._name_data_document = name
    @property
    def image_width(self):
        return self._image_width
    @property
    def image_height(self):
        return self._image_height

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, value):
        self._x = value
     
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, value):
        self._y = value

    def refresh(self):
        print("------REFRESHED------")

        #GET PATH OF DIRECTORY
        direcroty_path = os.getcwd()
        img_path = os.path.join(direcroty_path, "TestGraph.png")
        print(img_path)

        #READ DATA
        data = pd.read_csv(self._name_data_document, delimiter = ",")
        #x = data[self._name_x].astype("int").tolist()
        #y = data[self._name_y].astype("int").tolist()

        #GET FILE NAME AND REMOVE EXTENSION (EX: .csv)
        self._file_name = os.path.splitext(os.path.basename(self._name_data_document))[0]
        headers = data.columns.tolist()  

        if plt.gca().lines:
            print("Hay líneas dibujadas en el gráfico.")
            plt.clf()
        else:
            print("No hay líneas dibujadas en el gráfico.")

        plt.figure(figsize=(10,6))
        for header in headers[1:len(headers)]:
            #Get lines:
            #plt.plot(data[headers[0]], data[header], label = header)
            #Get points: 
            plt.plot(data[headers[0]], data[header], label = header, linestyle="", marker="o") 

        #plt.plot(x, y, label=self._name_label, color=self._color)
        plt.xlabel(headers[0])
        plt.ylabel("Values")
        plt.title(self._file_name)

        '''plt.xlabel(headers[0])
        plt.ylabel(headers[1])''' #solo si tenemos 1 header

        plt.legend()
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
        imagen_redimensionada.save('TestGraph.png')

        #Otro:
        self._graph = pygame.image.load(img_path)
        #self._graph = pygame.image.load("/home/ricardo/graphImg/graph_analyzed_data_resized.png")

        self._img_width, self._img_height = self._graph.get_size()
    
    def draw(self, win):
        win.blit(self._graph, (self._x, self._y))
    

