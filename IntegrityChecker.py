import os
import hashlib
import json
from PyQt6.QtCore import QObject, pyqtSignal, QThread

class IntegrityManager(QObject):
    status_signal = pyqtSignal(str, int)
    
    def __init__(self, game_path):
        super().__init__()
        self.game_path = game_path
        self.integrity_db = {}

    def load_database(self):
        try:
            with open("integrity.json", "r") as f:
                self.integrity_db = json.load(f)
        except:
            self.integrity_db = {}

    def get_file_hash(self, file_path):
        if not os.path.exists(file_path):
            return None
        
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def check_dlc(self, dlc_id, dlc_name):
        target_path = os.path.join(self.game_path, dlc_id)
        
        if not os.path.exists(target_path):
            self.status_signal.emit(dlc_id, 1)
            return 1
            
        files = os.listdir(target_path)
        if not files:
            self.status_signal.emit(dlc_id, 1)
            return 1
            
        if dlc_id in self.integrity_db:
             expected_files = self.integrity_db[dlc_id]["files"]
             for fname, expected_hash in expected_files.items():
                 fpath = os.path.join(target_path, fname)
                 if not os.path.exists(fpath):
                     self.status_signal.emit(dlc_id, 2)
                     return 2
                 
                 real_hash = self.get_file_hash(fpath)
                 if real_hash != expected_hash:
                     self.status_signal.emit(dlc_id, 2)
                     return 2
        
        self.status_signal.emit(dlc_id, 0)
        return 0

class IntegrityWorker(QThread):
    def __init__(self, manager, dlc_list):
        super().__init__()
        self.manager = manager
        self.dlc_list = dlc_list
        self._is_running = True

    def run(self):
        for dlc_id, dlc_name in self.dlc_list:
            if not self._is_running:
                break
            self.manager.status_signal.emit(dlc_id, 4) 
            self.manager.check_dlc(dlc_id, dlc_name)
            
    def stop(self):
        self._is_running = False