from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import time
from .tracker import flush_database, track
import sqlite3
from constants import FILE
import atexit


class TrackerSignals(QObject):
    finished = Signal(tuple)
    stop = Signal()


class TrackerWorker(QRunnable):
    def __init__(self) -> None:
        super().__init__()
        self.signals = TrackerSignals()
        self.signals.stop.connect(self.stop)
    
    @Slot()
    def run(self) -> None:
        database = sqlite3.connect(FILE)
        database.execute("PRAGMA journal_mode=WAL;")
        cursor = database.cursor()
        last_db_flush = time.perf_counter()
        atexit.register(lambda: flush_database(cursor))
        while True:
            time.sleep(1)
            if getattr(self, 'quit', False):
                return
            name = track(cursor)
            print(name)
            self.signals.finished.emit(name)

            if time.perf_counter() - last_db_flush > 60:
                flush_database(cursor)

    def stop(self):
        self.quit = True
