import os

# Use environment variable if set, otherwise default to /home/pi/krave
BASE = os.environ.get('KRAVE_BASE_PATH', '/home/pi/krave')

class Colors:
    BLACK = (0, 0, 0)       # 1
    GREEN = (0, 128, 0)     # 2
    ORANGE = (255,165,0)    # 3
    WHITE = (255, 255, 255) # 4
    D_BLUE = (0, 0, 139)    # 5
    PINK = (255,192,203)    # 6
    RED = (255,0,0)         # 7
    YELLOW = (255,255,0)    # 8
    L_BLUE = (65, 105, 225) # 9

class PATHS:
    TEMP_ANALYZED_DATA = f'{BASE}/krave/ui/analized_data/real_time_analized_data.csv'
    TEMP_IMG = f'{BASE}/krave/ui/images/graph_analyzed_data.png'
    TEMP_IMG_RESIZED = f'{BASE}/krave/ui/images/graph_analyzed_data_resized.png'
    RUN_TASK = f'{BASE}/run_task.sh'
    COMMUNICATION_FROM_EXP = f'{BASE}/krave/ui/communications/communication_from_exp.txt'
    COMMUNICATION_FROM_UI = f'{BASE}/krave/ui/communications/communication_from_ui.txt'
    START_SIGNAL = f'{BASE}/krave/ui/communications/start_signal.txt'
    STOP_SIGNAL = f'{BASE}/krave/ui/communications/stop_signal.txt'

class DATA_HEADERS:
    TRIAL = "trial"
    BG_REPEAT = "bg_repeat"
    WAIT_TIME = "wait_time"
    MISS_TRIAL = "miss_trial"
    REWARD_SIZE = "reward_size"

class DATA_WORDS:
    BACKGROUND = "background"
    WAIT = "wait"
    CONSUMPTION = "consumption"

DEFAULT_FPS = 15
DEFAULT_UPDATE_TIME_SECONDS = 5  # Increased from 2 to 5 seconds

#TODO use https://docs.python.org/3/library/importlib.resources.html to find paths to different resources files