import tkinter as tk
from tkinter import Menu

class experiment_options():
    def __init__(self):
        self.root = None
        self.rig_var = None
        self.training_var = None
        self.trainer_var = None
    
    def _init_tkinter(self):
        self.root = tk.Tk()
        self.root.title("Experiment options")
        self.root.geometry("300x185")
    
    def create_menu_bar(self):
        self.menubar = Menu(self.root)
    
    def create_rig_menu(self):
        self.rig_menu = Menu(self.menubar, tearoff = 0)
        self.rig_menu.add_command(label="Rig 1", command = lambda: self.f_rig("rig1"))
        self.rig_menu.add_command(label="Rig 2", command = lambda: self.f_rig("rig2"))
        self.rig_menu.add_command(label="Rig 3", command = lambda: self.f_rig("rig3"))
        self.rig_menu.add_command(label="Rig 4", command = lambda: self.f_rig("rig4"))
        self.rig_menu.add_command(label="Rig 5", command = lambda: self.f_rig("rig5"))
        self.rig_menu.add_command(label="Rig 6", command = lambda: self.f_rig("rig6"))
        self.rig_menu.add_command(label="Rig 7", command = lambda: self.f_rig("rig7"))
        self.menubar.add_cascade(label="Rig", menu = self.rig_menu)

    def create_training_menu(self):
        self.training_menu = Menu(self.menubar, tearoff = 0)
        self.training_menu.add_command(label="Shaping", command = lambda: self.f_training("shaping"))
        self.training_menu.add_command(label="Regular", command = lambda: self.f_training("regular"))
        self.menubar.add_cascade(label="Training", menu = self.training_menu)

    def create_trainer_menu(self):
        self.trainer_menu = Menu(self.menubar, tearoff = 0)
        self.trainer_menu.add_command(label="Rebekah", command = lambda: self.f_trainer("Rebekah"))
        self.trainer_menu.add_command(label="Lianne", command = lambda: self.f_trainer("Lianne"))
        self.menubar.add_cascade(label="Trainer", menu = self.trainer_menu)

    def add_menu_bar_to_window(self):
        self.root.config(menu = self.menubar)

    def create_frame_for_check_boxes(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(side='top', anchor='w', padx = 5, pady=20)

    def create_text_and_checkbox_for_record(self):
        label1 = tk.Label(self.frame, text="Record:")
        label1.grid(row=0, column=0, sticky='w', padx=(0, 10), pady = (0, 10))

        self.record_var = tk.BooleanVar(value = True)
        record_checkbox = tk.Checkbutton(self.frame, variable=self.record_var)
        record_checkbox.grid(row=0, column=1, sticky='w', pady = (0, 10))

    def create_text_and_checkbox_for_forward_file(self):
        self.label2 = tk.Label(self.frame, text="Forward file:")
        self.label2.grid(row=1, column=0, sticky='w', padx=(0, 10), pady = (0, 10))

        self.forward_file_var = tk.BooleanVar(value = True)
        forward_file_checkbox = tk.Checkbutton(self.frame, variable=self.forward_file_var)
        forward_file_checkbox.grid(row=1, column=1, sticky='w', pady = (0, 10))

    def create_accept_button(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(side='bottom', anchor='e', pady=(0,20), padx=20, fill='x')

        accept_button = tk.Button(button_frame, text="Accept", command=self.accept)
        accept_button.pack(side='right')

    def start_tkinter_main_loop(self):
        self.root.mainloop()

    def f_rig(self, rig_number_input):
        self.rig_var = rig_number_input
        print(self.rig_var)

    def f_training(self, training_input):
        self.training_var = training_input
        print(self.training_var)

    def f_trainer(self, trainer_input):
        self.trainer_var = trainer_input
        print(self.trainer_var)

    def accept(self):
        self.root.destroy()

    def run(self):
        self._init_tkinter()
        self.create_menu_bar()
        self.create_rig_menu()
        self.create_training_menu()
        self.create_trainer_menu()
        self.add_menu_bar_to_window()
        self.create_frame_for_check_boxes()
        self.create_text_and_checkbox_for_record()
        self.create_text_and_checkbox_for_forward_file()
        self.create_accept_button()
        self.start_tkinter_main_loop()

if __name__ == "__main__":
    experiment_options().run()
    