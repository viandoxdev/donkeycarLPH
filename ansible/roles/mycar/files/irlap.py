from evdev import InputDevice, ecodes
from time import time
import threading
from datetime import datetime, timedelta
import sys
import logging

class IrLapTimer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.device = InputDevice('/dev/input/event0')
        self.current_start_lap_date = None
        self.last_lap_start_date = None
        self.last_lap_duration = None
        self.last_lap_end_date = None
        self.laps_total = 0
        self.daemon = True
        return

    def run(self):
        last_time_was = 0
        laps_delay_validation = 2 # seconds
        for event in self.device.read_loop():
            logging.info(f"event {event.type} {event.value}")
            sys.stdout.flush()
            # get time in seconds
            time_seconds = int(time())
            if event.type == ecodes.EV_MSC and event.value == 131380: # receive a scancode of 0x20134
                # avoid rapid firing
                if time_seconds > (last_time_was + laps_delay_validation):
                    # save the last time when the event was received 
                    last_time_was = time_seconds
                    self.laps_total += 1
                    self.last_start_lap_date = self.current_start_lap_date
                    self.last_lap_end_date = datetime.utcnow()
                    self.current_start_lap_date = datetime.utcnow()
                    if self.last_start_lap_date:
                        self.last_lap_duration = (self.last_lap_end_date - self.last_lap_start_date) / timedelta(milliseconds = 1)
                    logging.info(f"lap {self.last_lap_duration}")

class IrLapTimerPart:
    def __init__(self):
        self.timer = IrLapTimer()
        self.timer.start()
    def update(self):
        return
    def run_threaded(self, reset_all = False):
        if reset_all:
            self.timer.current_start_lap_date= None
            self.timer.last_lap_start_date= None
            self.timer.last_lap_duration = None
            self.timer.last_lap_end_date = None
            self.timer.laps_total = 0
        current_lap_duration = None
        if self.timer.current_start_lap_date:
            current_lap_duration = (datetime.utcnow() - self.timer.current_start_lap_date) / timedelta(milliseconds = 1)
        return self.timer.current_start_lap_date, current_lap_duration, self.timer.last_lap_start_date, self.timer.last_lap_duration, self.timer.last_lap_end_date, self.timer.laps_total
    def run(self, reset_all = False):
        return self.run_threaded(reset_all)

