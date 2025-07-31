import pygame
import matplotlib.pyplot as plt
import pandas as pd
from krave.ui.constants import Colors, PATHS, DEFAULT_FPS, DEFAULT_UPDATE_TIME_SECONDS, DATA_HEADERS, DATA_WORDS
from krave.ui.button_start_class import StartButton
from krave.ui.button_stop_class import StopButton
from krave.ui.experiment_options import ExperimentOptions
import os
import time
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=RuntimeWarning)
warnings.simplefilter(action="ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*pygame.*")
import csv
from PIL import Image 
import sys
import subprocess

class UI():
    """Object to run a UI for a mouse experiment."""
    def __init__(self, source_data_path = None, fps = DEFAULT_FPS, update_time_seconds = DEFAULT_UPDATE_TIME_SECONDS) -> None:
        self._source_data_path = source_data_path
        self._pygame_window = None
        self._pygame_clock = None
        self._FPS = fps
        self._update_time_seconds = update_time_seconds
        self._index = None
        self._last_trial = None
        self._initial_index = None
        self._first_change = None
        self._last_mod_time = None
        self._num_rows = None
        self.exp_process_started = False
        self.session_start_time = None
        # Store display texts
        self.session_time_text = "0.0 min"
        self.mean_text = "Mean wait time: N/A"
        self.total_rewards_text = "Total rewards: N/A"

    def _init_pygame(self):
        if not self._pygame_window:    
            os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
            pygame.init()
            WIDTH, HEIGHT = 500, 400
            self._pygame_window = pygame.display.set_mode((WIDTH, HEIGHT))
            self._pygame_clock = pygame.time.Clock()
            pygame.display.set_caption("Krave")
            self._pygame_window.fill(Colors.WHITE)
    
    def _quit_pygame(self):
        pygame.quit()
    
    def _init_analyzed_data_file(self):
        """Create real_time_analized_data.csv file and place headers (to store analized data)"""
        new_headers = [DATA_HEADERS.TRIAL, DATA_HEADERS.BG_REPEAT, DATA_HEADERS.WAIT_TIME, DATA_HEADERS.MISS_TRIAL, DATA_HEADERS.REWARD_SIZE]
        with open(PATHS.TEMP_ANALYZED_DATA, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(new_headers)
    
    def _init_ui_loop_parameters(self):
        """Initialize variables for check_for_data_update function in the main loop"""
        print(f"[DEBUG] _init_ui_loop_parameters called - resetting _index from {getattr(self, '_index', 'undefined')} to 0")
        self._index = 0
        self._last_trial = -1
        self._initial_index = 1
        self._first_change = False
        self._last_mod_time = None
        self._total_trials = 42
    
    def _check_pygame_quit_event(self):
        """Check for events in pygame to quit the main loop and end program"""
        for event in pygame.event.get():
            if pygame.mouse.get_pressed()[0]:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if self.buttonStop.pressed(mouse_x, mouse_y) and self.buttonStart.activated:
                    with open(PATHS.STOP_SIGNAL, 'w') as f:
                        f.write('STOP')
                    return self.buttonStop.activate()
                
                if self.buttonStart.pressed(mouse_x, mouse_y) and self.buttonStart.activated == False:
                    self.buttonStart.activate()
                    self.session_start_time = time.time()
                    try:
                        with open(PATHS.START_SIGNAL, 'w') as f:
                            f.write('start')
                    except Exception as e:
                        print(f"Failed to write start signal: {e}")
                        
            if event.type == pygame.QUIT:
                with open(PATHS.STOP_SIGNAL, 'w') as f:
                    f.write('STOP')
                return False
        return True

    def plot_data(self, end = False):
        """This functions reads the file created with the analized data and plots it
        Creates two subplots: bg repeat line plot on top, wait time plot on bottom"""

        try:
            data = pd.read_csv(PATHS.TEMP_ANALYZED_DATA, delimiter = ",", low_memory=False)
        except Exception as e:
            print(f"Error reading analyzed data file: {e}")
            return

        plt.clf()
        
        if hasattr(self, 'menu_selector'):
            mouse_name = getattr(self.menu_selector, 'text_input_var', getattr(self.menu_selector, 'default_mouse_name', None))
        
        # Create two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), height_ratios=[1, 2])
        
        # Prepare data for plotting
        trials = []
        bg_repeats = []
        wait_times = []
        reward_sizes = []
        miss_trials = []
        
        for index, row in data.iterrows():
            trial_num = int(row[DATA_HEADERS.TRIAL])
            trials.append(trial_num)
            bg_repeats.append(row[DATA_HEADERS.BG_REPEAT])
            wait_times.append(row[DATA_HEADERS.WAIT_TIME])
            reward_size = float(row[DATA_HEADERS.REWARD_SIZE]) if not pd.isnull(row[DATA_HEADERS.REWARD_SIZE]) else 0
            reward_sizes.append(reward_size)
            miss_trials.append(row[-2])  # MISS_TRIAL is second to last
        
        # Top subplot: BG Repeat line plot
        ax1.plot(trials, bg_repeats, color='lightseagreen', linewidth=2, marker='o', markersize=4)
        ax1.set_ylabel('BG Repeat')
        ax1.grid(True, alpha=0.3)
        
        # Bottom subplot: Wait Time plot
        max_wait_time = 0
        for i, trial_num in enumerate(trials):
            if not miss_trials[i]:  # Not a miss trial
                color = "blue" if reward_sizes[i] > 0 else "black"
                ax2.plot(trial_num, wait_times[i], linestyle="", marker="o", color=color, markersize=3)
                max_wait_time = max(max_wait_time, wait_times[i])
            else:  # Miss trial
                ax2.axvspan(trial_num - 0.5, trial_num + 0.5, color="red", alpha=0.25)
        
        ax2.set_xlabel("Trial #")
        ax2.set_ylabel("Wait Time (s)")
        ax2.grid(True, alpha=0.3)
        
        # Set main title with mouse name
        fig.suptitle(mouse_name, fontsize=14, fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()

        try:
            plt.savefig(PATHS.TEMP_IMG)
            plt.close('all')  # Clear matplotlib cache to prevent memory leaks
        except Exception as e:
            print(f"Error when saving image: {e}")

        #Resize image
        imagen = Image.open(PATHS.TEMP_IMG)
        nuevo_tamano = (450, 350) #width and height
        imagen_redimensionada = imagen.resize(nuevo_tamano)

        # Save image with the new name
        imagen_redimensionada.save(PATHS.TEMP_IMG_RESIZED)
        
        if end:
            FINAL_IMG = os.path.join(os.path.dirname(self._source_data_path), "graph.png")
            imagen_redimensionada.save(FINAL_IMG)
    
    def draw(self):
        """Draws the main UI window, including plot, session time, mean wait time, and total rewards."""
        self._pygame_window.fill(Colors.WHITE)
        
        if self.buttonStart.activated:
            self._draw_running_interface()
        elif hasattr(self, 'menu_selector'):
            self._draw_setup_interface()
        else:
            self._draw_stop_only_interface()
            
        pygame.display.update()

    def _draw_running_interface(self):
        """Draw the interface when experiment is running."""
        self._draw_main_plot()
        self._draw_session_stats()
        self._draw_session_time()
        self.buttonStop.draw("STOP", self._pygame_window)

    def _draw_setup_interface(self):
        """Draw the interface when in setup mode."""
        self._draw_experiment_parameters()
        self.buttonStart.draw("START", self._pygame_window)

    def _draw_stop_only_interface(self):
        """Draw interface with only stop button."""
        self.buttonStop.draw("STOP", self._pygame_window)

    def _draw_main_plot(self):
        """Draw the main plot image."""
        plot_x, plot_y = 25, 0
        img = pygame.image.load(PATHS.TEMP_IMG_RESIZED)
        self._pygame_window.blit(img, (plot_x, plot_y))

    def _draw_session_stats(self):
        """Draw mean wait time and total rewards statistics."""
        stats_font = pygame.font.SysFont('Arial', 16, bold=True)
        mean_surface = stats_font.render(self.mean_text, True, Colors.D_BLUE)
        rewards_surface = stats_font.render(self.total_rewards_text, True, Colors.D_BLUE)
        
        # Position stats at bottom center
        self._pygame_window.blit(mean_surface, (120, 355))
        self._pygame_window.blit(rewards_surface, (120, 375))

    def _draw_session_time(self):
        """Draw session time and current trial number at bottom left."""
        time_font = pygame.font.SysFont('Arial', 12)
        time_surface = time_font.render(self.session_time_text, True, Colors.D_BLUE)
        self._pygame_window.blit(time_surface, (10, 355))
        
        # Draw current trial number underneath
        trial_text = f"Trial: {self._last_trial if self._last_trial is not None else 0}"
        trial_surface = time_font.render(trial_text, True, Colors.D_BLUE)
        self._pygame_window.blit(trial_surface, (10, 370))

    def _draw_experiment_parameters(self):
        """Draw experiment setup parameters."""
        param_font = pygame.font.SysFont('Arial', 18)
        params = self._get_experiment_parameters()
        
        for i, param in enumerate(params):
            text_surface = param_font.render(param, True, Colors.BLACK)
            self._pygame_window.blit(text_surface, (30, 30 + i * 28))

    def _get_experiment_parameters(self):
        """Get formatted experiment parameters for display."""
        params = [
            f"Rig: {self.menu_selector.rig_var}",
            f"Training: {self.menu_selector.training_var}",
            f"Trainer: {self.menu_selector.trainer_var}",
            f"Mouse: {getattr(self.menu_selector, 'text_input_var', getattr(self.menu_selector, 'default_mouse_name', ''))}",
            f"Record: {self._get_record_value()}",
            f"Forward file: {self._get_forward_file_value()}"
        ]
        
        # Add override parameters if they are set
        if self.menu_selector.max_reward_override is not None:
            params.append(f"Max Reward: {self.menu_selector.max_reward_override} μL")
        if self.menu_selector.max_time_override is not None:
            params.append(f"Max Time: {self.menu_selector.max_time_override // 60} min")
        if self.menu_selector.max_missed_trial_override is not None:
            params.append(f"Max Missed Trials: {self.menu_selector.max_missed_trial_override}")
        
        return params

    def _get_record_value(self):
        """Get the record value safely."""
        record_var = self.menu_selector.record_var
        return record_var.get() if hasattr(record_var, 'get') else record_var

    def _get_forward_file_value(self):
        """Get the forward file value safely."""
        forward_file_var = self.menu_selector.forward_file_var
        return forward_file_var.get() if hasattr(forward_file_var, 'get') else forward_file_var
    
    def read_data_file_csv(self):
        if not self._source_data_path:
            print("No data file path set, skipping read_data_file_csv.")
            return None
        
        try:
            # Single read to avoid race conditions
            data = pd.read_csv(self._source_data_path, delimiter = ",", low_memory=False)
            old_num_rows = self._num_rows
            self._num_rows = len(data)  # Use DataFrame length instead of separate file read
            if old_num_rows is not None and old_num_rows != self._num_rows:
                print(f"[DEBUG] File size updated: {old_num_rows} → {self._num_rows} rows")
            return data
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def write_TEMP_ANALYZED_DATA_csv(self, output_analyzed_data):
        with open(PATHS.TEMP_ANALYZED_DATA, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(output_analyzed_data)

    def check_for_data_update(self):
        """Check for updates in the self._source_data_path file and if there is an update it analizes the new rows of the file,
        copies the new analized data to the TEMP_ANALIZED_DATA file and plots with this file. Skip first modification (headers) 
        and trial -1 is not ploted or saved in the TEMP_ANALIZED_DATA file"""

        if not self._source_data_path:
            # No data file selected or experiment not started yet
            return

        if detect_change(self._source_data_path, self._last_mod_time):
            if self._first_change:
                self._last_mod_time = os.path.getmtime(self._source_data_path)
                data = self.read_data_file_csv()
                
                # Check for file reindexing (index went backwards)
                if self._num_rows < self._index:
                    print(f"[DEBUG] File reindexed! Previous index: {self._index}, Current file size: {self._num_rows}")
                    print(f"[DEBUG] Resetting to handle file restart...")
                    # Reset tracking variables
                    self._index = 0
                    self._last_trial = -1
                    self._initial_index = 1
                    # Clear invalid analyzed data
                    if os.path.exists(PATHS.TEMP_ANALYZED_DATA):
                        os.remove(PATHS.TEMP_ANALYZED_DATA)
                    if os.path.exists(PATHS.TEMP_IMG_RESIZED):
                        os.remove(PATHS.TEMP_IMG_RESIZED)
                    # Continue monitoring instead of returning
                    print(f"[DEBUG] Reset complete, continuing to monitor...")
                
                diff = (self._num_rows - 2) - self._index #New rows added since last check
                print(f"[DEBUG] Processing {diff} new rows, current index: {self._index}, file size: {self._num_rows}")
                
                new_index = self._index
                for i in range(diff):
                    new_index = self._index + 1 + i
                    output_analyzed_data = analyze_data(data, new_index, self._initial_index, self._last_trial)
                    if output_analyzed_data:
                        self._initial_index = new_index
                        if self._last_trial != -1:
                            self.write_TEMP_ANALYZED_DATA_csv(output_analyzed_data)
                            self.plot_data()
                        self._last_trial += 1
                print(f"[DEBUG] Updating _index from {self._index} to {new_index}")
                self._index = new_index
            else:
                self._first_change = True
                self._last_mod_time = os.path.getmtime(self._source_data_path)
                if hasattr(self, 'menu_selector'):
                    mouse_name = getattr(self.menu_selector, 'text_input_var', getattr(self.menu_selector, 'default_mouse_name', None))
                
                # Create initial two-subplot structure
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), height_ratios=[1, 2])
                
                # Top subplot: BG Repeat
                ax1.set_ylabel('BG Repeat')
                ax1.grid(True, alpha=0.3)
                
                # Bottom subplot: Wait Time
                ax2.set_xlabel("Trial #")
                ax2.set_ylabel("Wait Time (s)")
                ax2.grid(True, alpha=0.3)
                ax2.set_xlim(left=0)
                
                # Set main title with mouse name
                fig.suptitle(mouse_name, fontsize=14, fontweight='bold')
                
                plt.tight_layout()
                plt.savefig(PATHS.TEMP_IMG)
                img = Image.open(PATHS.TEMP_IMG)
                img = img.resize((450, 350))
                img.save(PATHS.TEMP_IMG_RESIZED)
                self._index += 1

            # --- Update display texts here ---
            # Session time (minutes)
            if self.session_start_time is not None:
                elapsed_seconds = time.time() - self.session_start_time
                elapsed_minutes = elapsed_seconds / 60
                self.session_time_text = f"{elapsed_minutes:.1f} min"
            else:
                self.session_time_text = "0.0 min"
            # Mean wait time and total rewards
            try:
                data = pd.read_csv(PATHS.TEMP_ANALYZED_DATA, delimiter=",", low_memory=False)
                wait_times = data[DATA_HEADERS.WAIT_TIME]
                wait_times = pd.to_numeric(wait_times, errors='coerce')
                valid_waits = wait_times[wait_times > 0].dropna()
                if len(valid_waits) > 0:
                    mean_wait = valid_waits.mean()
                    self.mean_text = f"Mean wait time: {mean_wait:.2f} s"
                else:
                    self.mean_text = "Mean wait time: N/A"
                if DATA_HEADERS.REWARD_SIZE in data.columns:
                    reward_sizes = pd.to_numeric(data[DATA_HEADERS.REWARD_SIZE], errors='coerce').fillna(0)
                    total_rewards = reward_sizes.sum()
                    self.total_rewards_text = f"Total rewards: {int(total_rewards)}"
                else:
                    self.total_rewards_text = "Total rewards: N/A"
            except Exception as e:
                print(f"[DEBUG] Error updating display texts: {e}")
                self.mean_text = "Mean wait time: N/A"
                self.total_rewards_text = "Total rewards: N/A"

    def check_krave_running(self):
        '''We check if task.py finishes the taks to end the UI and remove communication files. 
        Task.py writes in a file that is finishes and we look for that in each iteration. '''
        
        stop = False
        if os.path.exists(PATHS.STOP_SIGNAL):
            with open(PATHS.STOP_SIGNAL, "r") as file:
                stop = file.read().strip()
            if stop == "True" or stop == "STOP":
                with open(PATHS.STOP_SIGNAL, "r") as file:
                    content = file.read()
                print('----STOP FROM UI----')
                os.remove(PATHS.STOP_SIGNAL)
                return False
        return True
        

    def create_menu_selector(self):
        '''Create the menu to select the initial conditions of the experiment
        Tkinter only works if pygame is not in use (before or after)'''
        self.menu_selector = ExperimentOptions()

    def run_menu_selector(self):
        '''Run the menu'''
        self.menu_selector.run()

    def check_data_menu_selector(self):
        '''Check if the data provided by the user is correct (all selected). If not, get exception and quit'''
        if self.menu_selector.rig_var == None or self.menu_selector.training_var == None or self.menu_selector.trainer_var == None or self.menu_selector.text_input_var == "":
                    print("Error: You need to select all the options for the experiment")
                    sys.exit(1)
    
    def write_data_menu_selector(self):
        '''Write the data of the conditions of the experiment from the menu_selector in communications2 file. 
        run_task.sh will read this data'''

        with open(PATHS.COMMUNICATION_FROM_UI, 'w') as file:
            writer = csv.writer(file)
            writer.writerow([self.menu_selector.rig_var])
            writer.writerow([self.menu_selector.training_var])
            writer.writerow([self.menu_selector.trainer_var])
            writer.writerow([str(self.menu_selector.record_var.get())])
            writer.writerow([str(self.menu_selector.forward_file_var.get())])
            writer.writerow([self.menu_selector.text_input_var])
            # Write override parameters
            writer.writerow([str(self.menu_selector.max_reward_override) if self.menu_selector.max_reward_override is not None else ""])
            writer.writerow([str(self.menu_selector.max_time_override) if self.menu_selector.max_time_override is not None else ""])
            writer.writerow([str(self.menu_selector.max_missed_trial_override) if self.menu_selector.max_missed_trial_override is not None else ""])
        '''run_task.sh will read this data'''
    
    def final_data_plot(self):
        '''We do a final analyze and plot of all the data with the last trial'''
        data = self.read_data_file_csv()
        if data is None:
            print("No data to plot in final_data_plot.")
            return
        self._index = self._num_rows - 2
        output_analyzed_data = analyze_data(data, self._index, self._initial_index, self._last_trial, end = True)
        if output_analyzed_data:
            if self._last_trial != -1:
                self.write_TEMP_ANALYZED_DATA_csv(output_analyzed_data)
        self.plot_data(end = True)

    def remove_communication_files(self):
        '''We remove the communication files to avoid overwrite data and errors'''

        if os.path.exists(PATHS.COMMUNICATION_FROM_EXP):
            os.remove(PATHS.COMMUNICATION_FROM_EXP)
        if os.path.exists(PATHS.COMMUNICATION_FROM_UI):
            os.remove(PATHS.COMMUNICATION_FROM_UI)
        if os.path.exists(PATHS.START_SIGNAL):
            os.remove(PATHS.START_SIGNAL)
        try:
            os.remove(PATHS.STOP_SIGNAL)
        except FileNotFoundError:
            pass
        if hasattr(self, 'exp_process') and self.exp_process is not None:
            self.exp_process.terminate()
            self.exp_process.wait()
    
    def end_UI(self):
        '''We end run_task.sh process if it is running, the final data plot and remove the communication files'''

        if self.buttonStart.activated:
            if self.buttonStart.RUN_TASK.poll() is None:
                print("Ending process...")
                self.buttonStart.RUN_TASK.terminate()
                self.buttonStart.RUN_TASK.wait()
                print("Process ended")
        
        self.final_data_plot()
        self.remove_communication_files()

    def run(self):
        """Run main UI thread."""

        self.remove_communication_files()  # Clean up old files before anything else
        self.create_menu_selector()
        self.run_menu_selector()
        self.check_data_menu_selector()
        self.write_data_menu_selector()

        # Only launch experiment process if not already started
        if not self.exp_process_started:
            self.exp_process = subprocess.Popen(["python3", "run_task.sh"])
            self.exp_process_started = True

        # After launching the experiment process
        timeout = 10  # seconds
        start = time.time()
        while not os.path.exists(PATHS.COMMUNICATION_FROM_EXP):
            if time.time() - start > timeout:
                raise Exception("Experiment did not write events file path in time.")
            time.sleep(0.2)
        with open(PATHS.COMMUNICATION_FROM_EXP, "r") as file:
            # If multiple lines, get the last non-empty line
            lines = [line.strip() for line in file if line.strip()]
            if not lines:
                raise Exception("No events file path found in communication_from_exp.txt")
            self._source_data_path = lines[-1]

        self.buttonStart = StartButton(200, 345, 100, 50, Colors.L_BLUE)
        self.buttonStop = StopButton(350, 345, 100, 50, Colors.RED)
        
        self._init_pygame()
        self._init_analyzed_data_file()
        self._init_ui_loop_parameters()
        
        try:
            run = True
            start_time = time.time()
            while run:
                # Run UI update every {update_time_seconds} seconds.
                if self.buttonStart.activated:
                    current_time = time.time()
                    diff_time = current_time - start_time
                    if diff_time >= self._update_time_seconds:
                        start_time = time.time()
                        self.check_for_data_update()

                self._pygame_clock.tick(self._FPS)
                self.draw()
                run = self._check_pygame_quit_event()
                
                if run:
                    run = self.check_krave_running()
        except KeyboardInterrupt:
            print("UI interrupted by user.")
        finally:
            # Always clean up communication files, even on error or interrupt
            self.remove_communication_files()
            self._quit_pygame()

#FUNCTIONS
def analyze_data(data, index, initial_index, last_trial, end = False):
    """check in the self._source_data_path in the index row if we start a new trial. 
    if we started one then we check if it's a miss trial, the wait time, the backgrounds, and the reward size"""

    actual_row = data.iloc[index]
    actual_trial = actual_row[3]

    consumption = False
    wait_time = 0
    miss_trial = False
    reward_size = 0

    if (actual_trial != last_trial or end):
        number_background = 0
        initial_time = 0
        final_time = 0

        final_index = index - 1

        data_interval = data[initial_index:final_index + 1] #  Interval of data on 1 trial
        for idx, row in data_interval.iterrows(): #  Iterate for each row checking the data of the trial
            if (row[-1] == DATA_WORDS.BACKGROUND):
                number_background += 1
            elif (row[-1] == DATA_WORDS.WAIT):
                initial_time = row[0]
            elif (row[-1] == DATA_WORDS.CONSUMPTION):
                final_time = row[0]
                wait_time = final_time - initial_time
                consumption = True
                reward_size = row[6]  # 6th column (index 5) is reward_size, but your sample shows 7th (index 6)
        if (consumption == False):
            miss_trial = True
        return([last_trial, number_background, wait_time, miss_trial, reward_size])

def detect_change(source_data_path, time_last_mod):
    """This functions detetcts if there has been a modification in the file with the date"""
    if source_data_path is None:
        return False
    time_mod = os.path.getmtime(source_data_path)
    if (time_mod != time_last_mod):
        return True
    return False

if __name__ == '__main__':
    '''Runs only if direclty executed, no execution if imported (then you need to call main())'''
    UI().run()
