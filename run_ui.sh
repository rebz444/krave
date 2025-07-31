#!/bin/bash
cd /home/pi/krave
source /home/pi/krave-env/bin/activate
PYGAME_HIDE_SUPPORT_PROMPT=1 python3 -m krave.ui.ui 