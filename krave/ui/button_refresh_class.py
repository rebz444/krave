from button_class import Button
import pandas as pd
import matplotlib.pyplot as plt
import pygame
from krave.ui.debugging.graph_class import Graph

class RefreshButton(Button):
    def activate(self, object):
        object.refresh()

    