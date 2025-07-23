import tkinter as tk
import os
import json
from krave.helper import utils

PARAMS_FILE = os.path.join(os.path.dirname(__file__), 'last_exp_params.json')

class ExperimentOptions():
    '''Object to select all the conditions for the experiment'''

    @staticmethod
    def get_rig_options():
        try:
            hardware = utils.get_config('krave.hardware', 'hardware.json')
            return sorted(list(hardware.keys()))
        except Exception as e:
            print(f"Could not load rig options from hardware.json: {e}")
            return ["rig1", "rig2", "rig3", "rig4", "rig5", "rig6", "rig7"]

    RIG_OPTIONS = get_rig_options.__func__()
    TRAINING_OPTIONS = ["shaping", "regular"]
    TRAINER_OPTIONS = ["Rebekah", "Lianne"]

    def __init__(self):
        self.root = None
        # Set hardcoded defaults
        self.rig_var = "rig1"
        self.training_var = "regular"
        self.trainer_var = "Rebekah"
        self.default_mouse_name = "test"
        self.record_var = False
        self.forward_file_var = True
        # Try to load last used params
        self.load_last_params()

    def load_last_params(self):
        if os.path.exists(PARAMS_FILE):
            try:
                with open(PARAMS_FILE, 'r') as f:
                    params = json.load(f)
                self.rig_var = params.get('rig_var', self.rig_var)
                self.training_var = params.get('training_var', self.training_var)
                self.trainer_var = params.get('trainer_var', self.trainer_var)
                self.default_mouse_name = params.get('mouse_name', self.default_mouse_name)
                self.record_var = params.get('record_var', self.record_var)
                self.forward_file_var = params.get('forward_file_var', self.forward_file_var)
            except Exception as e:
                print(f"Could not load last experiment parameters: {e}")

    def save_last_params(self):
        params = {
            'rig_var': self.rig_var_var.get(),
            'training_var': self.training_var_var.get(),
            'trainer_var': self.trainer_var_var.get(),
            'mouse_name': getattr(self, 'text_input_var', self.default_mouse_name),
            'record_var': self.record_var.get() if hasattr(self, 'record_var') and hasattr(self.record_var, 'get') else self.record_var,
            'forward_file_var': self.forward_file_var.get() if hasattr(self, 'forward_file_var') and hasattr(self.forward_file_var, 'get') else self.forward_file_var
        }
        try:
            with open(PARAMS_FILE, 'w') as f:
                json.dump(params, f)
        except Exception as e:
            print(f"Could not save experiment parameters: {e}")
    
    def _init_tkinter(self):
        '''Initialize tkinter with the name and size'''
        self.root = tk.Tk()
        self.root.title("Experiment options")
        self.root.geometry("540x300")  # Wider and taller to fit all widgets

    def create_dropdowns(self):
        '''Create rig, training, and trainer dropdowns in a single row, each with a label above and more width.'''
        frame = tk.Frame(self.root)
        frame.pack(side='top', fill='x', padx=20, pady=10)

        # Rig
        rig_col = tk.Frame(frame, width=160)
        rig_col.pack(side='left', expand=True, fill='x', padx=8)
        tk.Label(rig_col, text="Rig:").pack(anchor='w', pady=(0, 2))
        self.rig_var_var = tk.StringVar(value=self.rig_var)
        rig_menu = tk.OptionMenu(rig_col, self.rig_var_var, *self.RIG_OPTIONS)
        rig_menu.config(width=12)
        rig_menu.pack(fill='x')

        # Training
        training_col = tk.Frame(frame, width=160)
        training_col.pack(side='left', expand=True, fill='x', padx=8)
        tk.Label(training_col, text="Training:").pack(anchor='w', pady=(0, 2))
        self.training_var_var = tk.StringVar(value=self.training_var)
        training_menu = tk.OptionMenu(training_col, self.training_var_var, *self.TRAINING_OPTIONS)
        training_menu.config(width=12)
        training_menu.pack(fill='x')

        # Trainer
        trainer_col = tk.Frame(frame, width=160)
        trainer_col.pack(side='left', expand=True, fill='x', padx=8)
        tk.Label(trainer_col, text="Trainer:").pack(anchor='w', pady=(0, 2))
        self.trainer_var_var = tk.StringVar(value=self.trainer_var)
        trainer_menu = tk.OptionMenu(trainer_col, self.trainer_var_var, *self.TRAINER_OPTIONS)
        trainer_menu.config(width=12)
        trainer_menu.pack(fill='x')
    
    def create_frame_for_check_boxes(self):
        '''Create a frame to place the mouse name entry and checkboxes'''
        self.frame = tk.Frame(self.root)
        self.frame.pack(side='top', fill='x', padx=20, pady=5)

    def create_text_entry(self):
        '''Create box to enter the mouse name, full width and clearly visible'''
        entry_frame = tk.Frame(self.frame)
        entry_frame.pack(fill='x', pady=(10, 8))
        tk.Label(entry_frame, text="Mouse Name:").pack(anchor='w', padx=(0, 2), pady=(0, 2))
        self.text_input = tk.Entry(entry_frame, width=30, font=("Arial", 12))
        self.text_input.insert(0, self.default_mouse_name)
        self.text_input.pack(fill='x', padx=2, pady=(0, 2))

    def create_text_and_checkbox_for_record(self):
        '''Create record and forward file checkboxes in a single row'''
        check_frame = tk.Frame(self.frame)
        check_frame.pack(fill='x', pady=(0, 10))
        # Record
        tk.Label(check_frame, text="Record:").pack(side='left', anchor='w', padx=(0, 2))
        self.record_var = tk.BooleanVar(value = self.record_var)
        record_checkbox = tk.Checkbutton(check_frame, variable=self.record_var)
        record_checkbox.pack(side='left', padx=(0, 15))
        # Forward file
        tk.Label(check_frame, text="Forward file:").pack(side='left', anchor='w', padx=(0, 2))
        self.forward_file_var = tk.BooleanVar(value = self.forward_file_var)
        forward_file_checkbox = tk.Checkbutton(check_frame, variable=self.forward_file_var)
        forward_file_checkbox.pack(side='left')

    def create_text_and_checkbox_for_forward_file(self):
        pass  # No longer needed, handled in create_text_and_checkbox_for_record

    def create_accept_button(self):
        '''Create a larger accept button with extra space above'''
        button_frame = tk.Frame(self.root)
        button_frame.pack(side='bottom', fill='x', pady=(20, 20), padx=20)
        accept_button = tk.Button(button_frame, text="Accept", command=self.accept, width=16, height=2, font=("Arial", 12, "bold"))
        accept_button.pack(side='right', padx=(0, 20), pady=(0, 10))

    def start_tkinter_main_loop(self):
        '''Starts tkinter mainloop to show the screen'''
        self.root.mainloop()

    def accept(self):
        '''Function called when pressing in accept button. Closes window'''
        self.text_input_var = self.text_input.get()
        # Validation: ensure all fields are filled
        if not self.rig_var_var.get() or not self.training_var_var.get() or not self.trainer_var_var.get() or not self.text_input_var.strip():
            tk.messagebox.showerror("Input Error", "Please select a rig, training, trainer, and enter a mouse name.")
            return
        # Save the current dropdown selections
        self.rig_var = self.rig_var_var.get()
        self.training_var = self.training_var_var.get()
        self.trainer_var = self.trainer_var_var.get()
        self.save_last_params()
        self.root.destroy()

    def run(self):
        '''When run it initiates the program'''
        self._init_tkinter()
        self.create_dropdowns()
        self.create_frame_for_check_boxes()
        self.create_text_entry()
        self.create_text_and_checkbox_for_record()
        self.create_text_and_checkbox_for_forward_file()
        self.create_accept_button()
        self.start_tkinter_main_loop()

if __name__ == "__main__":
    ExperimentOptions().run()

#TODO use constants to adress configuration names