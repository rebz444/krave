from button_class import Button
import tkinter as tk
from tkinter import filedialog

class SelectData(Button):
    def activate(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("TXT files", ".txt")])
        root.destroy()
        self.result = file_path
        return file_path #podria dar problemas porque utilizamos el self y el return