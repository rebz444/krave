import tkinter as tk
import time
import logging

from krave import utils

from PIL import Image, ImageTk


class Visual:
    def __init__(self, experiment_config):
        self.hardware_config = utils.get_config('krave.hardware', 'hardware.json')[experiment_config['hardware_setup']]
        self.cue_path = utils.get_path('krave.hardware', experiment_config['visual_cue_name'])
        self.cue_time = experiment_config['visual_cue_length']
        self.window = None
        self.window_size = None
        self.cue = None
        self.cue_displaying = False

    def initialize(self):
        self.window = tk.Tk()
        self.window.configure(bg = "black")
        self.window.attributes("-fullscreen", True)
        self.window.update()
        self.window_size = (self.window.winfo_width(), self.window.winfo_height())
        return time.time()

    def cue_on(self):
        if not self.window:
            logging.warning("Please initialize visual display first!")
            return
        img = PIL.Image.open(self.cue_path)
        img = img.resize(self.window_size)
        img = ImageTk.PhotoImage(img)
        self.cue = tk.Label(self.window, image=img)
        self.cue.pack()
        self.cue_displaying = True
        # self.window.after(self.cue_time, self.cue.destroy)
        self.window.update()
        return time.time()

    def cue_off(self):
        if self.cue_on:
            self.window.after(self.cue_time, self.cue.destroy)
            self.cue_displaying = False
        self.window.update()
        return time.time()

    def clean_up(self):
        self.window.destroy
        return time.time()

    # def test(self):
    #     self.window = tk.Tk()
    #     self.window.attributes("-fullscreen", True)
    #     self.window_size = (self.window.winfo_width(), self.window.winfo_height())
    #     self.window.update()
    #     img = Image.open(self.cue_path)
    #     img = img.resize(self.window_size)
    #     img = ImageTk.PhotoImage(img)
    #     label = tk.Label(self.window, image=img)
    #     label.pack()
    #     self.window.after(self.cue_time, label.destroy)
    #     self.window.update()
    #     self.window.destroy()
