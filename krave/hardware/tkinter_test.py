import tkinter as tk

from krave import utils

from PIL import Image, ImageTk

visual_cue_name = utils.get_config('krave.experiment', '/config/exp1.json')["visual_cue_name"]

my_img = ImageTk.PhotoImage(Image.open(visual_cue_name))
my_label = tk.Label(img=visual_cue_name)

# root = tk.Tk()
# root.configure(bg="black")
# root.attributes("-fullscreen", True)
# window_size = (root.winfo_width(), root.winfo_height())
#
#
# def show_cue():
#     img = Image.open('/Users/rebekahzhang/PycharmProjects/krave/krave/hardware/grating 0.79.png')
#     img = img.resize(window_size)
#     img = ImageTk.PhotoImage(img)
#     cue = tk.Label(root, img=img)
#     cue.pack()
#     cue.update()
#
#
# my_button = tk.Button(root, text='click me', command=show_cue)
# my_button.pack()
#
# root.mainloop()
