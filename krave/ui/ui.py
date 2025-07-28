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
        Maybe more work on legend"""

        try:
            data = pd.read_csv(PATHS.TEMP_ANALYZED_DATA, delimiter = ",")
        except Exception as e:
            print(f"Error reading analyzed data file: {e}")
            return

        plt.clf()
        
        if hasattr(self, 'menu_selector'):
            mouse_name = getattr(self.menu_selector, 'text_input_var', getattr(self.menu_selector, 'default_mouse_name', None))
        max_wait_time = 0
        for index, row in data.iterrows():
            trial_num = int(row[DATA_HEADERS.TRIAL])
            reward_size = float(row[DATA_HEADERS.REWARD_SIZE]) if not pd.isnull(row[DATA_HEADERS.REWARD_SIZE]) else 0
            if row[-2] == False:  # MISS_TRIAL is second to last now
                color = "blue" if reward_size > 0 else "black"
                plt.plot(trial_num, row[DATA_HEADERS.WAIT_TIME], linestyle="", marker="o", color=color)
            else:
                plt.axvspan(trial_num - 0.5, trial_num + 0.5, color = "red", alpha = 0.25)
            
            max_wait_time = max(max_wait_time, row[DATA_HEADERS.WAIT_TIME])

        #we get the different heights to create the top numbres (bg repeat)
        h1 = max_wait_time + (max_wait_time / 100 * 10)
        h2 = max_wait_time + (max_wait_time / 100 * 15)
        h3 = max_wait_time + (max_wait_time / 100 * 20)
        
        #plot the two black lines of separration
        plt.plot([0, len(data) - 1],[ h1,h1], color = "black")
        plt.plot([0, len(data) - 1],[ h3,h3], color = "black")

        #Name of axixs and title (now mouse name)
        plt.xlabel("trial #")
        plt.ylabel("t (s)")
        plt.title(mouse_name)

        #Plot the numbers (bg repeat)
        for index, row in data.iterrows():
            trial_num = int(row[DATA_HEADERS.TRIAL])
            plt.text(trial_num, h2, str(row[DATA_HEADERS.BG_REPEAT]), fontsize=12, color='lightseagreen', ha='center', va='center', alpha=0.5)
        
        plt.plot([],[], color = "black", label = "wait time (no reward)")
        plt.plot([],[], color = "blue", label = "wait time (reward)")
        plt.plot([],[], color = "lightseagreen", label = "bg repeat", )
        #plt.subplots_adjust(right=0.75) #Edge in the outside of the graph (problem -- graph compressed)
        #plt.legend(handletextpad=1, markerscale=15, loc='lower left', bbox_to_anchor=(1, 1))

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
            # --- Draw the main plot image ---
            plot_x, plot_y = 25, 0
            img = pygame.image.load(PATHS.TEMP_IMG_RESIZED)
            self._pygame_window.blit(img, (plot_x, plot_y))

            # --- Layout constants ---
            window_rect = self._pygame_window.get_rect()
            margin = 10
            gap_between_text = 6

            # --- Prepare surfaces for bottom center stats ---
            stats_font = pygame.font.SysFont('Arial', 16, bold=True)
            mean_surface = stats_font.render(self.mean_text, True, Colors.D_BLUE)
            rewards_surface = stats_font.render(self.total_rewards_text, True, Colors.D_BLUE)

            # --- Calculate positions for bottom center ---
            mean_width, mean_height = mean_surface.get_size()
            rewards_width, rewards_height = rewards_surface.get_size()
            center_x = window_rect.width // 2
            rewards_y = window_rect.height - rewards_height - margin
            mean_y = rewards_y - mean_height - gap_between_text
            offset = 40  # Move left by 40 pixels
            mean_x = center_x - mean_width // 2 - offset
            rewards_x = center_x - rewards_width // 2 - offset

            # --- Draw mean wait time and total rewards (stacked, centered) ---
            self._pygame_window.blit(mean_surface, (mean_x, mean_y))
            self._pygame_window.blit(rewards_surface, (rewards_x, rewards_y))

            # --- Draw session time at bottom left, above total rewards ---
            time_font = pygame.font.SysFont('Arial', 12)
            time_surface = time_font.render(self.session_time_text, True, Colors.D_BLUE)
            time_height = time_surface.get_height()
            time_y = rewards_y - time_height - 4  # 4px gap above rewards
            self._pygame_window.blit(time_surface, (margin, time_y))

            # --- Draw the stop button ---
            self.buttonStop.draw("STOP", self._pygame_window)

        # Draw experiment setup parameters and buttons if not running
        elif hasattr(self, 'menu_selector'):
            param_font = pygame.font.SysFont('Arial', 18)
            params = [
                f"Rig: {self.menu_selector.rig_var}",
                f"Training: {self.menu_selector.training_var}",
                f"Trainer: {self.menu_selector.trainer_var}",
                f"Mouse: {getattr(self.menu_selector, 'text_input_var', getattr(self.menu_selector, 'default_mouse_name', ''))}",
                f"Record: {self.menu_selector.record_var.get() if hasattr(self.menu_selector.record_var, 'get') else self.menu_selector.record_var}",
                f"Forward file: {self.menu_selector.forward_file_var.get() if hasattr(self.menu_selector.forward_file_var, 'get') else self.menu_selector.forward_file_var}"
            ]
            for i, param in enumerate(params):
                text_surface = param_font.render(param, True, Colors.BLACK)
                self._pygame_window.blit(text_surface, (30, 30 + i * 28))
            self.buttonStart.draw("START", self._pygame_window)
        else:
            self.buttonStop.draw("STOP", self._pygame_window)

        pygame.display.update()
    
    def read_data_file_csv(self):
        if not self._source_data_path:
            print("No data file path set, skipping read_data_file_csv.")
            return None
        reader = csv.reader(open(self._source_data_path))
        self._num_rows = len(list(reader))
        data = pd.read_csv(self._source_data_path, delimiter = ",")
        return data
    
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
                diff = (self._num_rows - 2) - self._index #New rows added since last check
                print(f"[DEBUG] Processing {diff} new rows, current index: {self._index}")
                
                new_index = 0
                for i in range(diff):
                    new_index = self._index + 1 + i
                    output_analyzed_data = analyze_data(data, new_index, self._initial_index, self._last_trial)
                    if output_analyzed_data:
                        self._initial_index = new_index
                        if self._last_trial != -1:
                            self.write_TEMP_ANALYZED_DATA_csv(output_analyzed_data)
                            self.plot_data()
                        self._last_trial += 1
                self._index = new_index
            else:
                self._first_change = True
                self._last_mod_time = os.path.getmtime(self._source_data_path)
                if hasattr(self, 'menu_selector'):
                    mouse_name = getattr(self.menu_selector, 'text_input_var', getattr(self.menu_selector, 'default_mouse_name', None))
                plt.xlabel("trial #")
                plt.ylabel("t (s)")
                plt.title(mouse_name)
                plt.plot([], [], color="black", label="wait time")
                plt.plot([], [], color="lightseagreen", label="bg repeat")
                plt.xlim(left=0)
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
                data = pd.read_csv(PATHS.TEMP_ANALYZED_DATA, delimiter=",")
                wait_times = data[DATA_HEADERS.WAIT_TIME]
                wait_times = pd.to_numeric(wait_times, errors='coerce')
                valid_waits = wait_times[wait_times > 0].dropna()
                if len(valid_waits) > 0:
                    mean_wait = valid_waits.mean()
                    self.mean_text = f"Mean wait time: {mean_wait:.0f} s"
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
