import tkinter as tk
import os
import time
import logging

from krave import utils

from PIL import Image, ImageTk


class Visual:
    def __init__(self, exp_name, hardware_config_name):
        self.exp_config = utils.get_config('krave.experiment', f'config/{exp_name}.json')
        self.hardware_config = utils.get_config('krave.hardware', '../hardware/hardware.json')[hardware_config_name]
        self.cue_name = self.exp_config['visual_cue_name']
        self.cue_path = utils.get_path('krave.hardware', self.cue_name)
        self.cue_length = self.exp_config['visual_cue_length']

        self.window = None
        self.window_size = None
        self.cue = None
        self.cue_displaying = False
        self.show_cue = False

    def test_test(self):
        print(self.cue_path)

    def initialize(self):
        self.window = tk.Tk()
        self.window.configure(bg="black")
        self.window.attributes("-fullscreen", True)
        self.window_size = (self.window.winfo_width(), self.window.winfo_height())
        self.window.mainloop()
        # self.window.update()
        # self.window_size = (self.window.winfo_width(), self.window.winfo_height())
        # return time.time()

    def test_cue(self):
        self.window = tk.Tk()
        img = Image.open(self.cue_path)
        # img = img.resize(self.window_size)
        img = ImageTk.PhotoImage(img)
        self.cue = tk.Label(self.window, image=img)
        self.cue.pack()
        self.window.after(self.cue_length, self.cue.destroy)
        self.window.mainloop()


    def main_loop(self):
        window = tk.Tk()
        window.configure(bg="black")
        window.attributes("-fullscreen", True)
        window_size = (window.winfo_width(), window.winfo_height())
        img = Image.open(self.cue_path)
        img = img.resize(window_size)
        img = ImageTk.PhotoImage(img)
        window.update()
        self.cue = tk.Label(window, image=img)

        def get_cue():
            self.cue.pack()
            window.update()

        window.after(3000, get_cue)

        window.after(6000, self.cue.destroy)

        window.mainloop()

    # def cue_on(self):
    #     if not self.window:
    #         logging.warning("Please initialize visual display first!")
    #         return
    #     img = Image.open(self.cue_path)
    #     img = img.resize(self.window_size)
    #     img = ImageTk.PhotoImage(img)
    #     self.cue = tk.Label(self.window, image=img)
    #     self.cue.pack()
    #     self.cue_displaying = True
    #     self.window.update()
    #     return time.time()
    #
    # def cue_off(self):
    #     if self.cue_displaying:
    #         self.window.after(self.cue_time, self.cue.destroy)
    #         self.cue_displaying = False
    #     self.window.update()
    #     return time.time()
    #
    # def clean_up(self):
    #     self.window.destroy
    #     return time.time()
    #
    # def test_one_run(self):
    #     window = tk.Tk()
    #     window.configure(bg="black")
    #     window.attributes("-fullscreen", True)
    #     # window_size = (window.winfo_width(), window.winfo_height())
    #     # img = Image.open(self.cue_path)
    #     # img = img.resize(window_size)
    #     # img = ImageTk.PhotoImage(img)
    #     # label = tk.Label(window, image=img)
    #     # label.pack()
    #     # window.after(self.cue_time, label.destroy())
    #     # window.update()
