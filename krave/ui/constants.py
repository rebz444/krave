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
    TEMP_ANALYZED_DATA = '/home/pi/real_time_analized_data.csv'
    TEMP_IMG = '/home/pi/graph_analyzed_data.png'
    TEMP_IMG_RESIZED = '/home/pi/graph_analyzed_data_resized.png' 

class DATA_HEADERS:
    TRIAL = "trial"
    BG_REPEAT = "bg_repeat"
    WAIT_TIME = "wait_time"
    MISS_TRIAL = "miss_trial"

DEFAULT_FPS = 15
DEFAULT_UPDATE_TIME_SECONDS = 5