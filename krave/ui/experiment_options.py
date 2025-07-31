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
        # New override parameters with default values (None means use config default)
        self.max_reward_override = None
        self.max_time_override = None
        self.max_missed_trial_override = None
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
                # Load override parameters
                self.max_reward_override = params.get('max_reward_override', self.max_reward_override)
                # Convert saved seconds back to minutes for display
                saved_time_seconds = params.get('max_time_override', self.max_time_override)
                self.max_time_override = saved_time_seconds
                self.max_missed_trial_override = params.get('max_missed_trial_override', self.max_missed_trial_override)
            except Exception as e:
                print(f"Could not load last experiment parameters: {e}")

    def save_last_params(self):
        params = {
            'rig_var': self.rig_var_var.get(),
            'training_var': self.training_var_var.get(),
            'trainer_var': self.trainer_var_var.get(),
            'mouse_name': getattr(self, 'text_input_var', self.default_mouse_name),
            'record_var': self.record_var.get() if hasattr(self, 'record_var') and hasattr(self.record_var, 'get') else self.record_var,
            'forward_file_var': self.forward_file_var.get() if hasattr(self, 'forward_file_var') and hasattr(self.forward_file_var, 'get') else self.forward_file_var,
            # Save override parameters
            'max_reward_override': self.max_reward_override_var.get() if hasattr(self, 'max_reward_override_var') else self.max_reward_override,
            'max_time_override': self.max_time_override,  # Save the seconds value
            'max_missed_trial_override': self.max_missed_trial_override_var.get() if hasattr(self, 'max_missed_trial_override_var') else self.max_missed_trial_override
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
        self.root.geometry("540x450")  # Made taller to accommodate new fields

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

    def create_override_parameters(self):
        '''Create input fields for max rewards, max trials, and max time overrides'''
        override_frame = tk.Frame(self.root)
        override_frame.pack(side='top', fill='x', padx=20, pady=10)
        
        # Title for override section
        tk.Label(override_frame, text="Session End Overrides (leave empty to use config defaults):", 
                font=("Arial", 10, "bold")).pack(anchor='w', pady=(0, 5))
        
        # Create three columns for the override parameters
        param_frame = tk.Frame(override_frame)
        param_frame.pack(fill='x')
        
        # Max Reward Override
        reward_col = tk.Frame(param_frame, width=160)
        reward_col.pack(side='left', expand=True, fill='x', padx=8)
        tk.Label(reward_col, text="Max Reward (μL):").pack(anchor='w', pady=(0, 2))
        self.max_reward_override_var = tk.StringVar(value=str(self.max_reward_override) if self.max_reward_override is not None else "")
        reward_entry = tk.Entry(reward_col, textvariable=self.max_reward_override_var, width=12)
        reward_entry.pack(fill='x')
        
        # Max Time Override
        time_col = tk.Frame(param_frame, width=160)
        time_col.pack(side='left', expand=True, fill='x', padx=8)
        tk.Label(time_col, text="Max Time (min):").pack(anchor='w', pady=(0, 2))
        self.max_time_override_var = tk.StringVar(value=str(self.max_time_override // 60) if self.max_time_override is not None else "")
        time_entry = tk.Entry(time_col, textvariable=self.max_time_override_var, width=12)
        time_entry.pack(fill='x')
        
        # Max Missed Trial Override
        missed_trial_col = tk.Frame(param_frame, width=160)
        missed_trial_col.pack(side='left', expand=True, fill='x', padx=8)
        tk.Label(missed_trial_col, text="Max Missed Trials:").pack(anchor='w', pady=(0, 2))
        self.max_missed_trial_override_var = tk.StringVar(value=str(self.max_missed_trial_override) if self.max_missed_trial_override is not None else "")
        missed_trial_entry = tk.Entry(missed_trial_col, textvariable=self.max_missed_trial_override_var, width=12)
        missed_trial_entry.pack(fill='x')

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

    def _parse_override_value(self, value_str):
        '''Parse override value, returning None if empty or invalid'''
        if not value_str.strip():
            return None
        try:
            return float(value_str) if '.' in value_str else int(value_str)
        except ValueError:
            return None

    def accept(self):
        '''Function called when pressing in accept button. Closes window'''
        self.text_input_var = self.text_input.get()
        # Validation: ensure all fields are filled
        if not self.rig_var_var.get() or not self.training_var_var.get() or not self.trainer_var_var.get() or not self.text_input_var.strip():
            tk.messagebox.showerror("Input Error", "Please select a rig, training, trainer, and enter a mouse name.")
            return
        
        # Parse override values
        self.max_reward_override = self._parse_override_value(self.max_reward_override_var.get())
        # Convert minutes to seconds for max_time_override
        time_minutes = self._parse_override_value(self.max_time_override_var.get())
        self.max_time_override = time_minutes * 60 if time_minutes is not None else None
        self.max_missed_trial_override = self._parse_override_value(self.max_missed_trial_override_var.get())
        
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
        self.create_override_parameters()
        self.create_accept_button()
        self.start_tkinter_main_loop()

if __name__ == "__main__":
    ExperimentOptions().run()

#TODO use constants to adress configuration names