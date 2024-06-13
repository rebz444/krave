import time
import numpy as np

import RPi.GPIO as GPIO


class IRBeam:
    def __init__(self):
        self.lick_pin = 21
        self.lick_status = 0
        self.lick_record = np.ones([2])
        self.lick_count = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lick_pin, GPIO.IN)

    def lick_status_check(self):
        """register change only when current status is different than all two previous status"""
        # self.lick_record = np.roll(self.lick_record, 1)
        # self.lick_record[0] = GPIO.input(self.lick_pin)
        # change_bool = np.all(self.lick_record != self.lick_status)
        # change = 0 if not change_bool else 1 if self.lick_status == 0 else -1
        change = GPIO.input(self.lick_pin) - self.lick_status
        self.lick_status += change

        return change

    def test(self, time_limit=30):
        start_time = time.time()
        try:
            while start_time + time_limit > time.time():
                lick_change = self.lick_status_check()
                if lick_change == 1:
                    self.lick_count += 1
                    print(f"lick {self.lick_count} started")
                elif lick_change == -1:
                    print(f"lick {self.lick_count} ended")
        finally:
            GPIO.cleanup()


if __name__ == '__main__':
    IRBeam().test()
