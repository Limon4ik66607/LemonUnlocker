import os
import sys
import shutil
import subprocess
import time
import winreg
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class AdminElevator:
    @staticmethod
    def is_admin():
        try:
            return subprocess.run("net session", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True).returncode == 0
        except:
            return False

    @staticmethod
    def requires_admin(path):
        try:
            test_file = os.path.join(path, ".test_write")
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return False
        except:
            return True

    @staticmethod
    def elevate():
        try:
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            subprocess.run(f'powershell Start-Process "{sys.executable}" -ArgumentList "{params}" -Verb RunAs', shell=True)
            sys.exit(0)
        except Exception as e:
            pass

class UnlockerManager:
    @staticmethod
    def get_base_path():
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def get_ea_desktop_path():
        try:
            keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Electronic Arts\EA Desktop", "ClientPath"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Electronic Arts\EA Desktop", "ClientPath")
            ]
            for hkey, subkey, val_name in keys:
                try:
                    key = winreg.OpenKey(hkey, subkey)
                    val, _ = winreg.QueryValueEx(key, val_name)
                    winreg.CloseKey(key)
                    if val and os.path.exists(val):
                        return os.path.dirname(val)
                except:
                    continue
        except:
            pass
    @staticmethod
    def check_status():
        ea_path = UnlockerManager.get_ea_desktop_path()
        if not ea_path:
            return False
        
        dst_dll = os.path.join(ea_path, "version.dll")
        return os.path.exists(dst_dll)

    @staticmethod
    def install_ea_unlocker(logger):
        ea_path = UnlockerManager.get_ea_desktop_path()
        if not ea_path:
            return False, "EA Desktop not found."
        
        if AdminElevator.requires_admin(ea_path) and not AdminElevator.is_admin():
            return False, "Administrator privileges required. Restart app as Admin."

        try:
            subprocess.run('taskkill /f /im "EADesktop.exe"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('taskkill /f /im "Origin.exe"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('taskkill /f /im "EABackgroundService.exe"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except:
            pass

        base_dir = UnlockerManager.get_base_path()
        
        src_dll = os.path.join(base_dir, "unlocker", "ea_desktop", "version.dll")
        if not os.path.exists(src_dll):
            src_dll = os.path.join(base_dir, "unlocker", "version.dll")
            
        if not os.path.exists(src_dll):
            return False, f"Source version.dll not found at {src_dll}"

        dst_dll = os.path.join(ea_path, "version.dll")
        
        try:
            shutil.copy2(src_dll, dst_dll)
            logger.log(f"Copied version.dll to {dst_dll}")
            
            parent = os.path.dirname(ea_path)
            staged = os.path.join(parent, "StagedEADesktop", "EA Desktop")
            if os.path.exists(staged):
                shutil.copy2(src_dll, os.path.join(staged, "version.dll"))
                logger.log(f"Copied version.dll to {staged}")
            
            appdata = os.path.join(os.environ["APPDATA"], "anadius", "EA DLC Unlocker v2")
            os.makedirs(appdata, exist_ok=True)
            
            config_src = os.path.join(base_dir, "unlocker", "config.ini")
            if os.path.exists(config_src):
                shutil.copy2(config_src, os.path.join(appdata, "config.ini"))
                logger.log("Copied config.ini")
            
            return True, "EA Unlocker installed successfully!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_sims4_config(logger):
        appdata = os.path.join(os.environ["APPDATA"], "anadius", "EA DLC Unlocker v2")
        os.makedirs(appdata, exist_ok=True)
        
        base_dir = UnlockerManager.get_base_path()
             
        src_conf = os.path.join(base_dir, "unlocker", "g_The Sims 4.ini")
        if not os.path.exists(src_conf):
             return False, "Source g_The Sims 4.ini not found"
             
        dst_conf = os.path.join(appdata, "g_The Sims 4.ini")
        try:
            shutil.copy2(src_conf, dst_conf)
            logger.log(f"Updated config: {dst_conf}")
            return True, "Sims 4 Config updated successfully!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def uninstall_ea_unlocker(logger):
        try:
            subprocess.run('taskkill /f /im "EADesktop.exe"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('taskkill /f /im "Origin.exe"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run('taskkill /f /im "EABackgroundService.exe"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except:
            pass
            
        ea_path = UnlockerManager.get_ea_desktop_path()
        if not ea_path:
            return False, "EA Desktop path not found."
            
        dst_dll = os.path.join(ea_path, "version.dll")
        if not os.path.exists(dst_dll):
            return True, "Unlocker was not installed (version.dll not found)."
            
        try:
            os.remove(dst_dll)
            logger.log(f"Removed {dst_dll}")
            
            parent = os.path.dirname(ea_path)
            staged = os.path.join(parent, "StagedEADesktop", "EA Desktop", "version.dll")
            if os.path.exists(staged):
                os.remove(staged)
                logger.log(f"Removed {staged}")
                
            return True, "EA Unlocker uninstalled successfully."
        except Exception as e:
            return False, f"Failed to uninstall: {str(e)}"

class UnlockerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DLC Unlocker Manager")
        self.setFixedSize(400, 250)
        self.parent_ui = parent
        self.setup_ui()
        self.setStyleSheet("QDialog{background-color:#1e1e1e;}QLabel{color:white;}QPushButton{background-color:#ffd700;color:black;border:none;padding:10px;font-weight:bold;border-radius:4px;}QPushButton:hover{background-color:#ffed4a;}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        header = QLabel("Lemon Unlocker Manager")
        header.setStyleSheet("font-size:16px;font-weight:bold;color:#ffd700;margin-bottom:10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        btn_install = QPushButton("1. Install EA Unlocker (Required Once)")
        btn_install.clicked.connect(self.install_unlocker)
        layout.addWidget(btn_install)
        
        btn_config = QPushButton("2. Update Sims 4 Config (Required for DLC)")
        btn_config.clicked.connect(self.update_config)
        layout.addWidget(btn_config)
        
        info = QLabel("Use Option 1 if you haven't installed Unlocker before.\nUse Option 2 to unlock newly downloaded DLCs.")
        info.setStyleSheet("color:#aaa;font-size:11px;text-align:center;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
    def install_unlocker(self):
        if not AdminElevator.is_admin():
            reply = QMessageBox.question(self, "Admin Rights", "Installing Unlocker requires Administrator rights.\nRestart as Administrator?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                AdminElevator.elevate()
            return

        success, msg = UnlockerManager.install_ea_unlocker(self.parent_ui.logger)
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Error", msg)

    def update_config(self):
        success, msg = UnlockerManager.update_sims4_config(self.parent_ui.logger)
        if success:
            QMessageBox.information(self, "Success", msg)
        else:
            QMessageBox.critical(self, "Error", msg)