import sys
import os
import shutil
import time
import requests
import json
import zipfile
import tempfile
import webbrowser
import traceback
import datetime
import platform
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, 
                             QProgressBar, QStackedWidget, QFileDialog, QMessageBox, 
                             QComboBox, QLineEdit, QGroupBox, QCheckBox, QTextEdit, QGridLayout)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal, QPropertyAnimation, QUrl, QObject, QPoint
from PyQt6.QtGui import QIcon, QColor, QDesktopServices, QCursor
from PyQt6 import sip

from dlc_database import DLCDatabase
from UnlockerLogic import UnlockerManager, AdminElevator
from IntegrityChecker import IntegrityManager, IntegrityWorker

APP_VERSION = "1.1.2"
GITHUB_REPO = "Limon4ik66607/LemonUnlocker" 


COLOR_BG_DARK = "#0f172a"
COLOR_BG_LIGHT = "#1e293b"
COLOR_BG_CARD = "#334155"
COLOR_ACCENT = "#FACC15"
COLOR_ACCENT_HOVER = "#EAB308"
COLOR_TEXT_WHITE = "#FFFFFF"
COLOR_TEXT_GRAY = "#94a3b8"
COLOR_DANGER = "#EF4444"
COLOR_SUCCESS = "#22C55E"

STYLE_SHEET = f"""
    QMainWindow {{
        background-color: {COLOR_BG_DARK};
        color: {COLOR_TEXT_WHITE};
    }}
    QWidget {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
        color: {COLOR_TEXT_WHITE};
    }}
    /* Scrollbar */
    QScrollBar:vertical {{
        border: none;
        background: {COLOR_BG_DARK};
        width: 8px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLOR_BG_LIGHT};
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {COLOR_BG_LIGHT};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        color: {COLOR_TEXT_WHITE};
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color:
    }}
    QPushButton:pressed {{
        background-color:
    }}
    
    /* Primary Action Button */
    QPushButton.primary {{
        background-color: {COLOR_ACCENT};
        color:
        font-weight: bold;
    }}
    QPushButton.primary:hover {{
        background-color: {COLOR_ACCENT_HOVER};
    }}
    
    /* Inputs */
    QLineEdit {{
        background-color: {COLOR_BG_LIGHT};
        border: 1px solid
        border-radius: 6px;
        padding: 8px;
        color: {COLOR_TEXT_WHITE};
    }}
    QLineEdit:focus {{
        border: 1px solid {COLOR_ACCENT};
    }}
    
    /* Cards */
    QFrame.card {{
        background-color: {COLOR_BG_LIGHT};
        border-radius: 12px;
        border: 1px solid
    }}
    
    /* Sidebar */
    QFrame
        background-color:
        border-right: 1px solid
    }}
    QPushButton.nav-btn {{
        text-align: left;
        padding: 12px 20px;
        border-radius: 0px;
        background-color: transparent;
        color: {COLOR_TEXT_GRAY};
        font-size: 15px;
        border-left: 3px solid transparent;
    }}
    QPushButton.nav-btn:hover {{
        background-color:
        color: {COLOR_TEXT_WHITE};
    }}
    QPushButton.nav-btn.active {{
        background-color:
        color: {COLOR_ACCENT};
        border-left: 3px solid {COLOR_ACCENT};
        font-weight: bold;
    }}
    
    /* Title Bar */
    QFrame
        background-color: transparent;
    }}
    QPushButton.win-btn {{
        background-color: transparent;
        border-radius: 0;
        font-weight: bold;
        font-size: 12px;
    }}
    QPushButton.win-btn:hover {{
        background-color:
    }}
    QPushButton.win-btn
        background-color: {COLOR_DANGER};
    }}
"""

SCROLLBAR_STYLESHEET = f"""
    QScrollBar:vertical {{
        border: none;
        background: {COLOR_BG_DARK};
        width: 8px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLOR_BG_LIGHT};
        min-height: 20px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""


import math

class FileUtils:
    @staticmethod
    def get_folder_size(start_path):
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except:
            pass
        return total_size

    @staticmethod
    def format_size(size_bytes):
        if size_bytes == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.log(size_bytes, 1024)) if size_bytes > 0 else 0
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

class ImprovedLogger:
    def __init__(self, text_widget=None):
        self.widget = text_widget
        self.logs = []
    
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] [{level}] {message}"
        self.logs.append(full_msg)
        print(full_msg)
        if self.widget:
            color = "#22C55E" if level == "SUCCESS" else "#EF4444" if level == "ERROR" else "#FACC15" if level == "WARNING" else "#FFFFFF"
            self.widget.append(f'<span style="color:#94a3b8">[{timestamp}]</span> <span style="color:{color}">{message}</span>')
            self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum())

    def export_logs(self):
        try:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            filename = f"LemonUnlocker_Logs_{int(time.time())}.txt"
            path = os.path.join(desktop, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.logs))
            return True, path
        except Exception as e:
            return False, str(e)

class CrashHandler:
    @staticmethod
    def install():
        sys.excepthook = CrashHandler.handle_exception

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        filename = os.path.join(log_dir, f"crash_log_{timestamp}.txt")
        
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Lemon Unlocker v{APP_VERSION} Crash Log - {timestamp}\n")
                f.write(f"OS: {platform.system()} {platform.release()}\n")
                f.write("-" * 50 + "\n")
                f.write(error_msg)
        except Exception as e:
            print(f"Failed to write crash log: {e}")
            
        try:
            app = QApplication.instance()
            if app:
                msg_en = (
                    f"An unhandled exception occurred.\n"
                    f"Log saved to: {os.path.abspath(filename)}\n\n"
                    f"Please send this file to the developer on Telegram: @L3mon4elo4"
                )
                
                title = "Critical Error"
                lang = "en"
                
                try:
                    if "Localization" in globals():
                        lang = globals()["Localization"].current_lang
                except:
                    pass

                if lang == "ru":
                    title = "Критическая ошибка"
                    msg = msg_ru
                else:
                    msg = msg_en
                    
                QMessageBox.critical(None, title, msg)
        except:

            pass
            
        sys.exit(1)

class GameDetector:
    @staticmethod
    def find_game():
        possible_paths = [
            r"C:\Program Files\EA Games\The Sims 4",
            r"C:\Program Files (x86)\Origin Games\The Sims 4",
            r"C:\Program Files (x86)\Steam\steamapps\common\The Sims 4",
            r"D:\Games\The Sims 4",
            r"E:\Games\The Sims 4",
            r"F:\Games\The Sims 4"
        ]
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Maxis\The Sims 4")
            val, _ = winreg.QueryValueEx(key, "Install Dir")
            if os.path.exists(val):
                return val
        except:
            pass
            
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "Game", "Bin", "TS4_x64.exe")):
                return path
        return None
LANG_EN = {
    "dashboard": "Home",
    "library": "Library",
    "catalog": "Catalog",
    "unlocker": "Unlocker",
    "settings": "Settings",
    "status_installed": "Unlocker Installed",
    "status_not_installed": "Unlocker Not Installed",
    "game_path": "Game Path:",
    "change_path": "Change",
    "total_dlcs": "Total DLCs Owned",
    "total_size": "Total Size of installed DLCs:",
    "my_library": "My Library",
    "get_dlcs": "Get DLCs",
    "search_placeholder": "Search DLC...",
    "download": "Download",
    "uninstall": "Uninstall",
    "install_unlocker": "1. Install EA Unlocker",
    "update_config": "2. Update Sims 4 Config",
    "uninstall_unlocker": "3. Uninstall Unlocker",
    "unlocker_info": "Use Option 1 once. Use Option 2 after new DLC downloads.",
    "app_settings": "Application Settings",
    "theme": "Theme",
    "language": "Language",
    "about": "About",
    "created_by": "Created by Lemon4elo",
    "support": "Support (Coming Soon)",
    "telegram_channel": "Telegram Channel",
    "telegram_chat": "Telegram Chat",
    "restart_required": "Restart required to apply language changes fully.",
    "success": "Success",
    "error": "Error",
    "quick_start": "Quick Start",
    "step_path": "Select Game Path",
    "step_install_unlocker": "Install Unlocker",
    "step_update_config": "Update Config",
    "step_install_dlc": "Install DLCs",
    "step_enjoy": "Enjoy the game!",
    "select_all": "Select All",
    "deselect_all": "Deselect All",
    "download_all": "Download All",
    "cat_all": "All",
    "cat_ep": "Expansions",
    "cat_gp": "Game Packs",
    "cat_sp": "Stuff Packs",
    "cat_kits": "Kits",
    "waiting": "Waiting...",
    "verify_files": "Verify Files"
}

LANG_RU = {
    "dashboard": "Главная",
    "library": "Библиотека",
    "catalog": "Каталог",
    "unlocker": "Анлокер",
    "settings": "Настройки",
    "status_installed": "Анлокер установлен",
    "status_not_installed": "Анлокер не установлен",
    "game_path": "Путь к игре:",
    "change_path": "Изменить",
    "total_dlcs": "Всего DLC установлено:",
    "total_size": "Общий размер установленных DLC:",
    "my_library": "Моя библиотека",
    "get_dlcs": "Скачать DLC",
    "search_placeholder": "Поиск DLC...",
    "download": "Скачать",
    "uninstall": "Удалить",
    "install_unlocker": "1. Установить Анлокер",
    "update_config": "2. Обновить конфиг Sims 4",
    "uninstall_unlocker": "3. Удалить Анлокер",
    "unlocker_info": "Опция 1 - один раз. Опция 2 - после скачивания новых DLC.",
    "app_settings": "Настройки приложения",
    "theme": "Тема",
    "language": "Язык",
    "about": "О программе",
    "created_by": "Создатель: Lemon4elo",
    "support": "Поддержать (Скоро)",
    "telegram_channel": "Telegram Канал",
    "telegram_chat": "Telegram Чат",
    "restart_required": "Перезапустите для смены языка.",
    "success": "Успешно",
    "error": "Ошибка",
    "quick_start": "Быстрый Старт",
    "verify_files": "Проверить файлы",
    "step_path": "Указать путь к игре",
    "step_install_unlocker": "Установить Анлокер",
    "step_update_config": "Обновить конфиги",
    "step_install_dlc": "Установить DLC",
    "step_enjoy": "Наслаждаться игрой!",
    "select_all": "Выбрать все",
    "deselect_all": "Снять выбор",
    "download_all": "Скачать все",
    "cat_all": "Все",
    "cat_ep": "Дополнения",
    "cat_gp": "Наборы",
    "cat_sp": "Каталоги",
    "cat_kits": "Комплекты",
    "waiting": "В очереди..."
}

class Localization:
    current_lang = "ru"
    _strings = LANG_RU

    @classmethod
    def set_language(cls, lang_code):
        cls.current_lang = lang_code
        if lang_code == "ru":
            cls._strings = LANG_RU
        else:
            cls._strings = LANG_EN

    @classmethod
    def get(cls, key):
        return cls._strings.get(key, key)

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load()
        
    def load(self):
        loaded_config = {}
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
            except:
                pass
        
        Localization.set_language(loaded_config.get("language", "ru"))
        return loaded_config
        
    def save(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
            
    def get(self, key, default=None):
        return self.config.get(key, default)
        
    def set(self, key, value):
        self.config[key] = value
        self.save()

class SmartDownloader:
    def __init__(self, logger):
        self.logger = logger
        self._progress_callback = None
        
    def set_progress_callback(self, callback):
        self._progress_callback = callback
        
    def download(self, url, out_path, dlc_name, resume=False):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = {"User-Agent": "LemonUnlocker/2.0"}
                downloaded = 0
                
                if (resume or attempt > 0) and os.path.exists(out_path):
                    downloaded = os.path.getsize(out_path)
                    headers["Range"] = f"bytes={downloaded}-"
                
                with requests.get(url, stream=True, headers=headers, timeout=(30, 60)) as r:
                    if r.status_code == 416:
                        return True, "OK"
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    
                    mode = 'ab' if downloaded > 0 else 'wb'
                    total_size += downloaded
                    
                    with open(out_path, mode) as f:
                        for chunk in r.iter_content(chunk_size=65536):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if self._progress_callback and total_size > 0:
                                self._progress_callback((downloaded / total_size) * 100, downloaded, total_size)
                return True, "OK"
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ChunkedEncodingError) as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return False, f"Connection failed after {max_retries} attempts: {str(e)}"
            except Exception as e:
                return False, str(e)

class Extractor:
    def __init__(self, logger):
        self.logger = logger
        
    def extract_zip(self, zip_path, out_dir):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(out_dir)
            return True, "Extracted"
        except Exception as e:
            return False, str(e)
    
    def extract_7z(self, zip_path, out_dir):
        """Extract using 7-Zip (required for multi-volume archives)"""
        import subprocess
        
        sz_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "7-Zip", "7z.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "7-Zip", "7z.exe"),
            os.path.join(os.environ.get("ProgramW6432", ""), "7-Zip", "7z.exe"),
        ]
        
        if getattr(sys, 'frozen', False):
            app_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        sz_paths.insert(0, os.path.join(app_dir, "7z", "7za.exe"))
        sz_paths.insert(1, os.path.join(app_dir, "7za.exe"))
        sz_paths.insert(2, os.path.join(app_dir, "7z.exe"))
        
        sz_exe = None
        for p in sz_paths:
            if os.path.exists(p):
                sz_exe = p
                break
        
        if not sz_exe:
            return False, "7-Zip not found. Please install 7-Zip to extract large DLCs.\nDownload: https://7-zip.org"
        
        try:
            result = subprocess.run(
                [sz_exe, "x", zip_path, f"-o{out_dir}", "-y", "-aoa"],
                capture_output=True, text=True, timeout=600
            )
            if result.returncode == 0:
                return True, "Extracted"
            else:
                return False, f"7-Zip error (code {result.returncode}): {result.stderr or result.stdout}"
        except Exception as e:
            return False, f"7-Zip execution failed: {str(e)}"

class DownloadWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(float)
    completed = pyqtSignal(bool)
    error_msg = pyqtSignal(str)

    def __init__(self, dlc_id, info, game_path, downloader, extractor):
        super().__init__()
        self.dlc_id = dlc_id
        self.info = info
        self.game_path = game_path
        self.downloader = downloader
        self.extractor = extractor

    def run(self):
        try:
            urls = self.info.get("urls")
            single_url = self.info.get("url")
            
            if urls and len(urls) > 1:
                temp_dir = os.path.join(tempfile.gettempdir(), f"lemon_{self.dlc_id}")
                os.makedirs(temp_dir, exist_ok=True)
                
                downloaded_files = []
                zip_file = None
                total_parts = len(urls)
                
                for i, url in enumerate(urls):
                    filename = url.split("/")[-1]
                    temp_path = os.path.join(temp_dir, filename)
                    downloaded_files.append(temp_path)
                    if filename.endswith(".zip"):
                        zip_file = temp_path
                    
                    part_idx = i
                    parts_total = total_parts
                    def make_cb(pi, pt):
                        def cb(p, d, t):
                            overall = ((pi * 100) + p) / pt
                            self.progress.emit(overall)
                        return cb
                    
                    self.downloader.set_progress_callback(make_cb(part_idx, parts_total))
                    success, msg = self.downloader.download(url, temp_path, self.dlc_id, resume=True)
                    if not success:
                        error_detail = f"[{self.dlc_id}] Download failed (part {i+1}/{total_parts}): {msg}"
                        self._log_error(error_detail)
                        self.error_msg.emit(error_detail)
                        shutil.rmtree(temp_dir, ignore_errors=True)
                        self.completed.emit(False)
                        self.finished.emit()
                        return
                
                zip_file = next((f for f in downloaded_files if f.endswith(".zip")), None)
                
                if not zip_file:
                    success = False
                    msg = "Main .zip file not found"
                else:
                    extract_dir = os.path.join(temp_dir, "_extracted")
                    os.makedirs(extract_dir, exist_ok=True)
                    success, msg = self.extractor.extract_7z(zip_file, extract_dir)
                    
                    if success:
                        archive_exts = ('.zip', '.rar', '.7z', '.tar', '.gz')
                        nested_archives = []
                        for item in os.listdir(extract_dir):
                            item_path = os.path.join(extract_dir, item)
                            if os.path.isfile(item_path):
                                _, ext = os.path.splitext(item)
                                if ext.lower() in archive_exts or (not ext and os.path.getsize(item_path) > 100_000_000):
                                    nested_archives.append(item_path)
                        
                        if nested_archives:
                            for nested in nested_archives:
                                success, msg = self.extractor.extract_7z(nested, self.game_path)
                                if not success:
                                    break
                        else:
                            for item in os.listdir(extract_dir):
                                src = os.path.join(extract_dir, item)
                                dst = os.path.join(self.game_path, item)
                                if os.path.isdir(src):
                                    if os.path.exists(dst):
                                        shutil.rmtree(dst)
                                    shutil.move(src, dst)
                                else:
                                    shutil.move(src, dst)
                
                if success:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                else:
                    error_detail = f"[{self.dlc_id}] Extraction failed: {msg}\nTemp files kept at: {temp_dir}"
                    self._log_error(error_detail)
                    self.error_msg.emit(error_detail)
            else:
                url = single_url or (urls[0] if urls else None)
                temp_path = os.path.join(tempfile.gettempdir(), f"{self.dlc_id}.zip")
                
                self.downloader.set_progress_callback(self.report_progress)
                success, msg = self.downloader.download(url, temp_path, self.dlc_id, resume=True)
                
                if not success:
                    error_detail = f"[{self.dlc_id}] Download failed: {msg}"
                    self._log_error(error_detail)
                    self.error_msg.emit(error_detail)
                    self.completed.emit(False)
                    self.finished.emit()
                    return
                
                success, msg = self.extractor.extract_zip(temp_path, self.game_path)
                
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
            self.completed.emit(success)
        except Exception as e:
            error_detail = f"[{self.dlc_id}] Download error: {str(e)}"
            self._log_error(error_detail)
            self.error_msg.emit(error_detail)
            self.completed.emit(False)
        finally:
            self.finished.emit()

    def _log_error(self, message):
        try:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.join(base_dir, "logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(log_dir, f"download_error_{timestamp}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Lemon Unlocker v{APP_VERSION} Download Error - {timestamp}\n")
                f.write(f"DLC: {self.dlc_id} ({self.info.get('name', 'Unknown')})\n")
                f.write("-" * 50 + "\n")
                f.write(message + "\n")
        except:
            pass

    def report_progress(self, p, d, t):
        self.progress.emit(p)


class TitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(32)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        
        title = QLabel(f"🍋 Lemon Unlocker")
        title.setStyleSheet(f"font-weight: bold; color: {COLOR_ACCENT}; font-size: 13px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("min-btn")
        self.min_btn.setFixedSize(45, 32)
        self.min_btn.setCursor(Qt.CursorShape.ArrowCursor)
        self.min_btn.clicked.connect(parent.showMinimized)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close-btn")
        self.close_btn.setFixedSize(45, 32)
        self.close_btn.setCursor(Qt.CursorShape.ArrowCursor)
        self.close_btn.clicked.connect(parent.close)
        
        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)
        
        self.start = QPoint(0, 0)
        self.pressing = False

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            end = self.mapToGlobal(event.pos())
            movement = end - self.start
            self.window().setGeometry(self.window().x() + movement.x(),
                                    self.window().y() + movement.y(),
                                    self.window().width(),
                                    self.window().height())
            self.start = end

    def mouseReleaseEvent(self, event):
        self.pressing = False

class Sidebar(QFrame):
    def __init__(self, parent_controller):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(240)
        self.controller = parent_controller
        self.setStyleSheet(f"background-color: {COLOR_BG_DARK}; border-right: 1px solid #1e293b;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 30, 10, 30)
        layout.setSpacing(8)
        
        logo = QLabel("LEMON\nUNLOCKER")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"font-weight: 900; font-size: 20px; color: {COLOR_TEXT_WHITE}; margin-bottom: 30px; letter-spacing: 1px;")
        layout.addWidget(logo)
        
        self.buttons = {}
        self.add_nav_btn(Localization.get("dashboard"), "🏠", 0)
        self.add_nav_btn(Localization.get("library"), "📚", 1)
        self.add_nav_btn(Localization.get("catalog"), "🛒", 2)
        self.add_nav_btn(Localization.get("unlocker"), "🔓", 3)
        self.add_nav_btn(Localization.get("settings"), "⚙️", 4)
        
        layout.addStretch()
        
        ver = QLabel(f"v{APP_VERSION}")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 11px; opacity: 0.7;")
        layout.addWidget(ver)

    def add_nav_btn(self, text, icon, index):
        btn = QPushButton(f"  {text}")
        btn.setIcon(QIcon())
        btn.setText(f"{icon}   {text}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(45)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_GRAY};
                text-align: left;
                padding-left: 20px;
                border-radius: 8px;
                border: none;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color:
                color: {COLOR_TEXT_WHITE};
            }}
        """)
        
        btn.clicked.connect(lambda: self.controller.switch_page(index))
        self.layout().addWidget(btn)
        self.buttons[index] = btn

    def set_active(self, index):
        for idx, btn in self.buttons.items():
            if idx == index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_BG_LIGHT};
                        color: {COLOR_ACCENT};
                        text-align: left;
                        padding-left: 20px;
                        border-radius: 8px;
                        border-left: 3px solid {COLOR_ACCENT};
                        font-weight: 700;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLOR_TEXT_GRAY};
                        text-align: left;
                        padding-left: 20px;
                        border-radius: 8px;
                        border: none;
                        border-left: 3px solid transparent;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color:
                        color: {COLOR_TEXT_WHITE};
                    }}
                """)

class DashboardPage(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: transparent; border: none;")
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("DashboardContent")
        self.scroll.setWidget(self.scroll_content)
        
        layout = QVBoxLayout(self.scroll_content)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        main_layout.addWidget(self.scroll)
        

        header = QLabel(Localization.get("dashboard"))
        header.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {COLOR_TEXT_WHITE}; letter-spacing: 1px;")
        layout.addWidget(header)
        
        guide_card = QFrame()
        guide_card.setObjectName("GuideCard")
        guide_card.setStyleSheet(f"""
            QFrame
                background-color: transparent;
            }}
        """)
        guide_layout = QVBoxLayout(guide_card)
        guide_layout.setContentsMargins(0, 0, 0, 0)
        guide_layout.setSpacing(15)
        
        title_lbl = QLabel(Localization.get("quick_start") if Localization.get("quick_start") else "Quick Start")
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_WHITE}; font-size: 18px; font-weight: 800; letter-spacing: 1px; margin-left: 5px;")
        guide_layout.addWidget(title_lbl)
        
        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(15)
        
        steps_data = [
            ("1", "📁", Localization.get("step_path") if Localization.get("step_path") else "Select Path"),
            ("2", "🔓", Localization.get("step_install_unlocker") if Localization.get("step_install_unlocker") else "Install Unlocker"),
            ("3", "📝", Localization.get("step_update_config") if Localization.get("step_update_config") else "Update Config"),
            ("4", "🛒", Localization.get("step_install_dlc") if Localization.get("step_install_dlc") else "Get DLCs"),
            ("5", "🎉", Localization.get("step_enjoy") if Localization.get("step_enjoy") else "Enjoy!")
        ]
        
        for num, icon, text in steps_data:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLOR_BG_LIGHT};
                    border-radius: 16px;
                    border: 1px solid
                }}
                QFrame:hover {{
                    border: 1px solid {COLOR_ACCENT};
                    background-color:
                    margin-top: -5px; /* Lift effect */
                }}
            """)
            card.setFixedHeight(140)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)
            card_layout.setSpacing(10)
            
            h_row = QHBoxLayout()
            
            num_lbl = QLabel(num)
            num_lbl.setFixedSize(24, 24)
            num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num_lbl.setStyleSheet(f"""
                background-color: {COLOR_ACCENT}; 
                color: {COLOR_BG_DARK};
                border-radius: 12px;
                font-weight: 900;
                font-size: 13px;
            """)
            
            step_icon = QLabel(icon)
            step_icon.setStyleSheet("font-size: 32px; background: transparent; border: none;")
            step_icon.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            h_row.addWidget(num_lbl)
            h_row.addStretch()
            h_row.addWidget(step_icon)
            
            card_layout.addLayout(h_row)
            
            text_lbl = QLabel(text)
            text_lbl.setStyleSheet(f"color: {COLOR_TEXT_WHITE}; font-size: 13px; font-weight: 700; background: transparent; border: none;")
            text_lbl.setWordWrap(True)
            text_lbl.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
            
            card_layout.addWidget(text_lbl)
            steps_layout.addWidget(card)
            
        guide_layout.addLayout(steps_layout)
        layout.addWidget(guide_card)
        
        path_card = QFrame()
        path_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_LIGHT};
                border-radius: 16px;
                border: 1px solid {COLOR_BG_LIGHT};
            }}
            QFrame:hover {{
                border: 1px solid
            }}
        """)
        path_layout = QHBoxLayout(path_card)
        path_layout.setContentsMargins(20, 20, 20, 20)
        
        path_icon = QLabel("📁")
        path_icon.setStyleSheet("font-size: 24px; color: #94a3b8;")
        
        path_info = QVBoxLayout()
        lbl_path_title = QLabel(Localization.get("game_path"))
        lbl_path_title.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 12px; font-weight: 600;")
        self.lbl_path_val = QLabel("Not Set")
        self.lbl_path_val.setStyleSheet(f"color: {COLOR_TEXT_WHITE}; font-size: 15px; font-weight: 500;")
        self.lbl_path_val.setWordWrap(True)
        path_info.addWidget(lbl_path_title)
        path_info.addWidget(self.lbl_path_val)
        
        btn_layout = QHBoxLayout()
        btn_change = QPushButton(Localization.get("change_path"))
        btn_change.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_change.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_DARK}; 
                border: 1px solid
                padding: 8px 16px; 
                border-radius: 8px;
                font-weight: 600;
                color: {COLOR_TEXT_WHITE};
            }}
            QPushButton:hover {{
                background-color:
                border: 1px solid
            }}
        """)
        btn_change.clicked.connect(self.change_path)
        
        btn_auto = QPushButton("Auto")
        btn_auto.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_auto.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_DARK}; 
                border: 1px solid
                padding: 8px 16px; 
                border-radius: 8px;
                font-weight: 600;
                color: {COLOR_ACCENT};
                margin-left: 8px;
            }}
            QPushButton:hover {{
                background-color:
                border: 1px solid {COLOR_ACCENT};
            }}
        """)
        btn_auto.clicked.connect(self.auto_detect)
        
        btn_layout.addWidget(btn_change)
        btn_layout.addWidget(btn_auto)
        
        path_layout.addWidget(path_icon)
        path_layout.addSpacing(15)
        path_layout.addLayout(path_info, stretch=1)
        path_layout.addLayout(btn_layout)
        
        layout.addWidget(path_card)
        
        stats_row = QHBoxLayout()
        stats_row.setSpacing(20)
        
        self.stats_card = self.create_stat_card(Localization.get("total_dlcs"), "0 / 0", "#FACC15")
        self.size_card = self.create_stat_card(Localization.get("total_size"), "0 B", "#3B82F6")
        
        stats_row.addWidget(self.stats_card)
        stats_row.addWidget(self.size_card)
        
        layout.addLayout(stats_row)

        self.news_card = QFrame()
        self.news_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_LIGHT};
                border-radius: 16px;
                border: 1px solid
            }}
            QFrame:hover {{
                border: 1px solid {COLOR_ACCENT};
                background-color:
            }}
        """)
        news_layout = QVBoxLayout(self.news_card)
        news_layout.setContentsMargins(25, 25, 25, 25)
        news_layout.setSpacing(15)
        
        news_header = QHBoxLayout()
        
        lbl_news_title = QLabel(Localization.get("latest_news") if Localization.get("latest_news") else "Latest News") 
        lbl_news_title.setText("Latest Updates")
        lbl_news_title.setStyleSheet(f"color: {COLOR_TEXT_WHITE}; font-size: 18px; font-weight: 800; background: transparent; letter-spacing: 0.5px;")
        
        news_header.addWidget(lbl_news_title)
        news_header.addStretch()
        
        news_layout.addLayout(news_header)
        
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #334155; border: none;")
        news_layout.addWidget(sep)
        
        self.lbl_news_content = QLabel("Loading updates...")
        self.lbl_news_content.setWordWrap(True)
        self.lbl_news_content.setOpenExternalLinks(True)
        self.lbl_news_content.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_TEXT_GRAY}; 
                font-size: 14px; 
                background: transparent; 
                line-height: 1.4;
            }}
        """)
        
        news_layout.addWidget(self.lbl_news_content)
        
        layout.addWidget(self.news_card)
        layout.addStretch()
        
        self.config = ConfigManager()
        saved_path = self.config.get("game_path")
        
        QTimer.singleShot(1000, self.load_news)

        if saved_path:
            self.check_stats()

    def load_news(self):
        try:
            version, body, date = Updater.get_latest_news()
            if version:
                header_html = f"""
                <div style='margin-bottom: 10px;'>
                    <span style='background-color: {COLOR_ACCENT}; color: #000; font-weight: bold; padding: 4px 8px; border-radius: 4px;'>v{version}</span>
                    <span style='color: #64748b; margin-left: 10px; font-style: italic;'>{date}</span>
                </div>
                <br>
                """
                
                body = body.replace("**", "")
                lines = body.split('\n')
                formatted_lines = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("- "):
                        formatted_lines.append(f"<div style='margin-left: 10px;'>• {line[2:]}</div>")
                    elif line:
                        formatted_lines.append(f"<div>{line}</div>")
                
                body_html = "".join(formatted_lines)
                
                full_html = header_html + body_html
                self.lbl_news_content.setText(full_html)
            else:
                self.lbl_news_content.setText("No updates available.")
        except Exception as e:
             self.lbl_news_content.setText("Could not load updates.")

    def create_stat_card(self, title, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_LIGHT};
                border-radius: 12px;
                border: 1px solid
            }}
            QFrame:hover {{
                border: 1px solid {color};
                background-color: {color}10; /* Very slight tint */
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 20, 25, 20)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 13px; font-weight: 700; letter-spacing: 0.5px; background: transparent; border: none;")
        
        val_lbl = QLabel(value)
        val_lbl.setObjectName("ValueLabel")
        val_lbl.setStyleSheet(f"color: {COLOR_TEXT_WHITE}; font-size: 28px; font-weight: 800; background: transparent; border: none; margin-top: 5px;")
        
        val_lbl.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 900; background: transparent; border: none;")

        layout.addWidget(title_lbl)
        layout.addWidget(val_lbl)
        
        frame.val_lbl = val_lbl 
        return frame

    def change_path(self):
        folder = QFileDialog.getExistingDirectory(self, Localization.get("game_path"))
        if folder:
            self.config.set("game_path", folder)
            self.config.save()
            self.check_stats()

    def auto_detect(self):
        path = GameDetector.find_game()
        if path:
            self.config.set("game_path", path)
            self.config.save()
            self.check_stats()
        else:
            QMessageBox.warning(self, Localization.get("error"), "Could not automatically find The Sims 4.")

    def check_stats(self):
        config = ConfigManager()
        path = config.get("game_path")
        
        if path and os.path.exists(path):
            self.lbl_path_val.setText(path)
            installed = 0
            total_size = 0
            try:
                for item in os.listdir(path):
                    if item.upper().startswith(("EP", "GP", "SP")):
                        full_path = os.path.join(path, item)
                        if os.path.exists(os.path.join(full_path, "__Installer")) or any(os.scandir(full_path)): 
                            installed += 1
                            total_size += FileUtils.get_folder_size(full_path)
            except:
                pass
            
            db = DLCDatabase()
            total = len(db.all())
            self.stats_card.val_lbl.setText(f"{installed} / {total}")
            self.size_card.val_lbl.setText(FileUtils.format_size(total_size))
            
            if hasattr(self.parent_window, 'library_page'):
                self.parent_window.library_page.populate()
            if hasattr(self.parent_window, 'catalog_page'):
                self.parent_window.catalog_page.populate()
                
        else:
            self.lbl_path_val.setText("Not Set")
            self.stats_card.val_lbl.setText("0 / 0")
            self.size_card.val_lbl.setText("0 B")

class DLCListPage(QWidget):
    def __init__(self, parent_window, mode="installed"):
        super().__init__()
        self.parent_window = parent_window
        self.mode = mode
        self.db = DLCDatabase()
        self.selected_items = set()
        self.active_downloads = {}
        self.pending_downloads = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        header_row = QHBoxLayout()
        title_text = Localization.get("my_library") if mode == "installed" else Localization.get("get_dlcs")
        title = QLabel(title_text)
        title.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {COLOR_TEXT_WHITE}; letter-spacing: 1px;")
        header_row.addWidget(title)
        header_row.addStretch()
        
        self.btn_select_all = QPushButton(Localization.get("select_all"))
        self.btn_select_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_all.setCheckable(True)
        self.btn_select_all.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLOR_TEXT_GRAY};
                color: {COLOR_TEXT_GRAY};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:checked {{
                background-color: {COLOR_ACCENT}20;
                border: 1px solid {COLOR_ACCENT};
                color: {COLOR_ACCENT};
            }}
            QPushButton:hover {{
                border-color: {COLOR_TEXT_WHITE};
                color: {COLOR_TEXT_WHITE};
            }}
        """)
        self.btn_select_all.clicked.connect(self.toggle_select_all)
        header_row.addWidget(self.btn_select_all)
        header_row.addSpacing(10)

        if mode == "installed":
             self.btn_verify = QPushButton(Localization.get("verify_files"))
             self.btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
             self.btn_verify.setStyleSheet(f"background-color: {COLOR_BG_CARD}; color: {COLOR_TEXT_GRAY}; border-radius: 8px; padding: 6px 12px; font-weight: 600;")
             self.btn_verify.clicked.connect(self.verify_files)
             header_row.addWidget(self.btn_verify)
             header_row.addSpacing(10)
        
        config = ConfigManager()
        self.integrity_manager = IntegrityManager(config.get("game_path"))
        self.integrity_manager.status_signal.connect(self.on_verify_status)
        self.verification_worker = None

        self.filter_combo = QLineEdit()
        self.filter_combo.setPlaceholderText(Localization.get("search_placeholder"))
        self.filter_combo.textChanged.connect(self.filter_list)
        self.filter_combo.setFixedWidth(250)
        self.filter_combo.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_BG_LIGHT};
                border: 1px solid
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLOR_TEXT_WHITE};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_ACCENT};
            }}
        """)
        header_row.addWidget(self.filter_combo)
        
        layout.addLayout(header_row)
        
        cat_layout = QHBoxLayout()
        cat_layout.setSpacing(10)
        
        self.cat_buttons = {}
        categories = [
            ("ALL", Localization.get("cat_all")),
            ("EP", Localization.get("cat_ep")),
            ("GP", Localization.get("cat_gp")),
            ("SP", Localization.get("cat_sp")),
            ("KIT", Localization.get("cat_kits"))
        ]
        
        self.current_category = "ALL"
        
        for cat_id, cat_name in categories:
            btn = QPushButton(cat_name)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda checked, c=cat_id: self.filter_category(c))
            cat_layout.addWidget(btn)
            self.cat_buttons[cat_id] = btn
            
        cat_layout.addStretch()
        layout.addLayout(cat_layout)

        self.update_cat_styles()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.verticalScrollBar().setStyleSheet(SCROLLBAR_STYLESHEET)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)
        
        self.action_bar = QFrame()
        self.action_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_LIGHT};
                border-radius: 12px;
                border: 1px solid {COLOR_ACCENT};
            }}
        """)
        self.action_bar.setFixedHeight(60)
        self.action_bar.hide()
        
        action_layout = QHBoxLayout(self.action_bar)
        action_layout.setContentsMargins(20, 10, 20, 10)
        
        self.lbl_selected_count = QLabel("0 selected")
        self.lbl_selected_count.setStyleSheet(f"color: {COLOR_TEXT_WHITE}; font-weight: bold; font-size: 14px;")
        
        btn_action = QPushButton()
        btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.mode == "catalog":
            btn_action.setText(Localization.get("download_all"))
            btn_action.setStyleSheet(f"background-color: {COLOR_SUCCESS}; color: white; border-radius: 6px; padding: 6px 16px; font-weight: bold;")
            btn_action.clicked.connect(self.batch_download)
        else:
            btn_action.setText("Uninstall Selected") 
            btn_action.setStyleSheet(f"background-color: {COLOR_DANGER}; color: white; border-radius: 6px; padding: 6px 16px; font-weight: bold;")
            btn_action.clicked.connect(self.batch_uninstall)
            
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"background-color: transparent; color: {COLOR_TEXT_GRAY}; border: 1px solid {COLOR_TEXT_GRAY}; border-radius: 6px; padding: 6px 12px;")
        btn_cancel.clicked.connect(self.clear_selection)
        
        action_layout.addWidget(self.lbl_selected_count)
        action_layout.addStretch()
        action_layout.addWidget(btn_cancel)
        action_layout.addWidget(btn_action)
        
        layout.addWidget(self.action_bar)

        QTimer.singleShot(100, self.populate)
        
    def filter_category(self, cat_id):
        self.current_category = cat_id
        self.update_cat_styles()
        self.apply_filters()

    def update_cat_styles(self):
        for cat, btn in self.cat_buttons.items():
            if cat == self.current_category:
                btn.setChecked(True)
                btn.setStyleSheet(f"""
                    background-color: {COLOR_ACCENT}; 
                    color: {COLOR_BG_DARK}; 
                    border-radius: 16px; 
                    padding: 0 15px; 
                    font-weight: bold;
                    border: none;
                """)
            else:
                btn.setChecked(False)
                btn.setStyleSheet(f"""
                    background-color: {COLOR_BG_LIGHT}; 
                    color: {COLOR_TEXT_GRAY}; 
                    border-radius: 16px; 
                    padding: 0 15px; 
                    font-weight: bold;
                    border: 1px solid
                """)

    def apply_filters(self):
        text = self.filter_combo.text().lower()
        
        for i in range(self.scroll_layout.count()):
            w = self.scroll_layout.itemAt(i).widget()
            if w and hasattr(w, "dlc_id"):
                dlc_id = w.dlc_id.upper()
                name_match = False
                
                if text in dlc_id.lower():
                    name_match = True
                else:
                    labels = w.findChildren(QLabel)
                    for l in labels:
                        if text in l.text().lower():
                            name_match = True
                            break
                            
                cat_match = False
                if self.current_category == "ALL":
                    cat_match = True
                elif self.current_category == "EP" and dlc_id.startswith("EP"):
                    cat_match = True
                elif self.current_category == "GP" and dlc_id.startswith("GP"):
                    cat_match = True
                elif self.current_category == "SP":
                    try:
                        num = int(dlc_id[2:])
                        if dlc_id.startswith("SP") and num < 20: 
                             cat_match = True
                    except:
                        pass
                elif self.current_category == "KIT":
                    if dlc_id.startswith("FP"):
                        cat_match = True
                    elif dlc_id.startswith("SP"):
                        try:
                            num = int(dlc_id[2:])
                            if num >= 20: 
                                cat_match = True
                        except:
                            pass
                
                if name_match and cat_match:
                    w.show()
                else:
                    w.hide()
        
    def toggle_select_all(self):
        target_select = self.btn_select_all.isChecked()
        
        if target_select:
            self.btn_select_all.setText(Localization.get("deselect_all"))
        else:
            self.btn_select_all.setText(Localization.get("select_all"))
            
        for i in range(self.scroll_layout.count()):
            w = self.scroll_layout.itemAt(i).widget()
            if w and w.isVisible() and hasattr(w, "dlc_id"):
                if target_select:
                    if w.dlc_id not in self.selected_items:
                        self.toggle_selection(w.dlc_id, w)
                else:
                    if w.dlc_id in self.selected_items:
                        self.toggle_selection(w.dlc_id, w)

    def populate(self):
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.clear_selection()
                
        config = ConfigManager()
        game_path = config.get("game_path")
        
        if not game_path or not os.path.exists(game_path):
            lbl = QLabel("Game path not set in Dashboard.")
            lbl.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 16px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(lbl)
            return

        db = DLCDatabase()
        dlcs = db.all()
        
        sorted_dlcs = sorted(dlcs.items(), key=lambda x: x[0])
        
        for dlc_id, info in sorted_dlcs:
            is_installed = False
            target_path = os.path.join(game_path, dlc_id)
            
            if os.path.exists(target_path):
                 if any(os.scandir(target_path)):
                    is_installed = True
            
            if self.mode == "installed" and is_installed:
                size = FileUtils.get_folder_size(target_path)
                card = self.create_dlc_card(dlc_id, info, is_installed=True, size=size)
                self.scroll_layout.addWidget(card)
            elif self.mode == "catalog" and not is_installed:
                size = info.get("size", 0)
                card = self.create_dlc_card(dlc_id, info, is_installed=False, size=size)
                
                if dlc_id in self.active_downloads:
                    btn = card.action_button
                    btn.setEnabled(False)
                    btn.setText("Downloading...")
                    thread, worker = self.active_downloads[dlc_id]
                    worker.progress.connect(lambda p, b=btn: b.setText(f"{int(p)}%") if not sip.isdeleted(b) else None)
                    worker.completed.connect(lambda s, b=btn: self.on_download_complete(s, b) if not sip.isdeleted(b) else None)
                elif dlc_id in [d[0] for d in self.pending_downloads]:
                    btn = card.action_button
                    btn.setEnabled(False)
                    btn.setText(Localization.get("waiting") if Localization.get("waiting") else "Waiting...")
                
                self.scroll_layout.addWidget(card)
        
        self.apply_filters()

    def create_dlc_card(self, dlc_id, info, is_installed, size=0):
        frame = QFrame()
        frame.setObjectName("DLCCard")
        frame.dlc_id = dlc_id
        
        bg_color = COLOR_BG_LIGHT
        border_color = "#334155"
        
        frame.setStyleSheet(f"""
            QFrame
                background-color: {bg_color};
                border-radius: 12px;
                border: 1px solid {border_color};
            }}
            QFrame
                border: 1px solid {COLOR_ACCENT};
                background-color:
            }}
        """)
        frame.setFixedHeight(80)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        self.checkbox = QCheckBox()
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {COLOR_TEXT_GRAY};
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_ACCENT};
                border: 2px solid {COLOR_ACCENT};
                image: url(none); /* We could add checks tick if we had icon */
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLOR_ACCENT};
            }}
        """)
        self.checkbox.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(self.checkbox)
        
        type_lbl = QLabel(dlc_id[:2])
        type_lbl.setFixedSize(45, 45)
        type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if "EP" in dlc_id: color = "#A855F7"
        elif "GP" in dlc_id: color = "#3B82F6"
        elif "SP" in dlc_id: color = "#22C55E"
        else: color = "#64748B"
        
        type_lbl.setStyleSheet(f"background-color: {color}; color: white; border-radius: 10px; font-weight: 800; font-size: 16px;")
        layout.addWidget(type_lbl)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        name_lbl = QLabel(info['name'])
        name_lbl.setStyleSheet(f"font-weight: 700; font-size: 15px; color: {COLOR_TEXT_WHITE};")
        
        meta_text = dlc_id
        if size > 0:
            meta_text += f" • {FileUtils.format_size(size)}"
            
        id_lbl = QLabel(meta_text)
        id_lbl.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 12px; font-weight: 500;")
        
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(id_lbl)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(36)
        
        if self.mode == "catalog":
            btn.setText(Localization.get("download"))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_BG_DARK};
                    border: 1px solid {COLOR_SUCCESS};
                    color: {COLOR_SUCCESS};
                    border-radius: 6px;
                    padding: 0 15px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_SUCCESS};
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda _, id=dlc_id: self.start_download([id]))
        else:
            btn.setText(Localization.get("uninstall"))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {COLOR_DANGER};
                    color: {COLOR_DANGER};
                    border-radius: 6px;
                    padding: 0 15px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_DANGER};
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda _, id=dlc_id: self.start_uninstall([id]))
            
        layout.addWidget(btn)
        frame.action_button = btn
        
        frame.mousePressEvent = lambda e: self.toggle_selection(dlc_id, frame)
        
        frame.checkbox = self.checkbox
        
        return frame

    def toggle_selection(self, dlc_id, frame):
        if dlc_id in self.selected_items:
            self.selected_items.remove(dlc_id)
            frame.checkbox.setChecked(False)
            frame.setStyleSheet(f"""
                QFrame
                    background-color: {COLOR_BG_LIGHT};
                    border-radius: 12px;
                    border: 1px solid
                }}
                QFrame
                    border: 1px solid {COLOR_ACCENT};
                    background-color:
                }}
            """)
        else:
            self.selected_items.add(dlc_id)
            frame.checkbox.setChecked(True)
            frame.setStyleSheet(f"""
                QFrame
                    background-color:
                    border-radius: 12px;
                    border: 1px solid {COLOR_ACCENT};
                }}
            """)
            
        self.update_action_bar()

    def clear_selection(self):
        self.selected_items.clear()
        
        self.btn_select_all.setChecked(False)
        self.btn_select_all.setText(Localization.get("select_all"))
        
        for i in range(self.scroll_layout.count()):
            w = self.scroll_layout.itemAt(i).widget()
            if w and hasattr(w, "dlc_id"):
                 w.checkbox.setChecked(False)
                 w.setStyleSheet(f"""
                    QFrame
                        background-color: {COLOR_BG_LIGHT};
                        border-radius: 12px;
                        border: 1px solid
                    }}
                    QFrame
                        border: 1px solid {COLOR_ACCENT};
                        background-color:
                    }}
                """)
        self.update_action_bar()

    def update_action_bar(self):
        count = len(self.selected_items)
        if count > 0:
            self.lbl_selected_count.setText(f"{count} selected")
            self.action_bar.show()
        else:
            self.action_bar.hide()

    def batch_download(self):
        self.start_download(list(self.selected_items))
        self.clear_selection()

    def batch_uninstall(self):
        self.start_uninstall(list(self.selected_items))
        self.clear_selection()
        
    def start_download(self, dlc_ids):
        db = DLCDatabase()
        all_dlcs = db.all()
        
        for dlc_id in dlc_ids:
            if dlc_id in all_dlcs:
                if dlc_id in [d[0] for d in self.pending_downloads] or dlc_id in self.active_downloads:
                    continue
                
                info = all_dlcs[dlc_id]
                target_btn = None
                for i in range(self.scroll_layout.count()):
                    w = self.scroll_layout.itemAt(i).widget()
                    if w and hasattr(w, "dlc_id") and w.dlc_id == dlc_id:
                        if hasattr(w, "action_button"):
                            target_btn = w.action_button
                        break
                
                self.pending_downloads.append((dlc_id, info, target_btn))
                if target_btn:
                    target_btn.setEnabled(False)
                    target_btn.setText(Localization.get("waiting") if Localization.get("waiting") else "Waiting...")
            else:
                print(f"DLC {dlc_id} not found in database")
        
        self.process_next_download()

    def process_next_download(self):
        if self.active_downloads:
            return
            
        if not self.pending_downloads:
            return
            
        dlc_id, info, btn = self.pending_downloads.pop(0)
        
        target_btn = btn
        if btn is None or sip.isdeleted(btn):
            for i in range(self.scroll_layout.count()):
                w = self.scroll_layout.itemAt(i).widget()
                if w and hasattr(w, "dlc_id") and w.dlc_id == dlc_id:
                    if hasattr(w, "action_button"):
                        target_btn = w.action_button
                    break
                    
        self.download_dlc(dlc_id, info, target_btn)
             
    def start_uninstall(self, dlc_ids):
        reply = QMessageBox.question(self, "Confirm", f"Delete {len(dlc_ids)} DLCs?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            config = ConfigManager()
            game_path = config.get("game_path")
            success_count = 0
            for dlc in dlc_ids:
                try:
                    target = os.path.join(game_path, dlc)
                    import shutil
                    if os.path.exists(target):
                        shutil.rmtree(target)
                        success_count += 1
                except:
                    pass
            
            self.populate()
            if hasattr(self.parent_window, 'dashboard_page'):
                self.parent_window.dashboard_page.check_stats()
            
            QMessageBox.information(self, "Done", f"Deleted {success_count} DLCs.")

    def filter_list(self, text):
        self.apply_filters()

    def download_dlc(self, dlc_id, info, btn=None):
        config = ConfigManager()
        game_path = config.get("game_path")
        if not game_path or not os.path.exists(game_path):
            QMessageBox.warning(self, "No Game Path", "Please select your game folder in the Dashboard first.")
            self.parent_window.switch_page(0)
            return

        if AdminElevator.requires_admin(game_path) and not AdminElevator.is_admin():
            QMessageBox.warning(self, "Admin Required", "Your game folder requires Administrator privileges.\nPlease restart Lemon Unlocker as Administrator.")
            return

        if btn and not sip.isdeleted(btn):
            btn.setEnabled(False)
            btn.setText("Downloading...")
        
        logger = ImprovedLogger() 
        logger.widget = self.parent_window.unlocker_page.console 
        
        downloader = SmartDownloader(logger)
        extractor = Extractor(logger)
        
        thread = QThread()
        worker = DownloadWorker(dlc_id, info, game_path, downloader, extractor)
        worker.moveToThread(thread)
        
        self.active_downloads[dlc_id] = (thread, worker)
        
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        thread.finished.connect(lambda d=dlc_id: self.active_downloads.pop(d, None))
        
        if btn:
            worker.progress.connect(lambda p, b=btn: b.setText(f"{int(p)}%") if not sip.isdeleted(b) else None)
            worker.completed.connect(lambda s, b=btn: self.on_download_complete(s, b) if not sip.isdeleted(b) else None)
            worker.error_msg.connect(lambda msg: self.on_download_error(msg))
        else:
            worker.completed.connect(lambda s: self.on_download_complete(s, None))
            worker.error_msg.connect(lambda msg: self.on_download_error(msg))
        
        thread.start()

    def on_download_complete(self, success, btn=None):
        if success:
            if btn and not sip.isdeleted(btn):
                btn.setText("Installed")
                btn.setStyleSheet(f"background-color: {COLOR_BG_DARK}; border: 1px solid {COLOR_SUCCESS}; color: {COLOR_SUCCESS};")
            QTimer.singleShot(1000, self.refresh_all_lists)
        else:
            if btn and not sip.isdeleted(btn):
                btn.setText("Failed ⓘ")
                btn.setEnabled(True)
                btn.setStyleSheet(f"background-color: {COLOR_BG_DARK}; border: 1px solid {COLOR_DANGER}; color: {COLOR_DANGER};")
                if not btn.toolTip():
                    btn.setToolTip("Download failed. Check logs/ folder for details.")
        
        QTimer.singleShot(500, self.process_next_download)

    def on_download_error(self, error_msg):
        """Show download error in a popup so user can see it even from .exe"""
        QMessageBox.warning(self, "Download Error", f"Download failed:\n\n{error_msg}")

    def uninstall_dlc(self, dlc_id):
        reply = QMessageBox.question(self, 'Uninstall DLC', 
                                     f"Are you sure you want to delete {dlc_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            config = ConfigManager()
            game_path = config.get("game_path")
            target_path = os.path.join(game_path, dlc_id)
            try:
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                    QMessageBox.information(self, "Success", f"{dlc_id} uninstalled.")
                    self.refresh_all_lists()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete folder: {str(e)}")

    def verify_files(self):
        self.btn_verify.setEnabled(False)
        self.btn_verify.setText("Checking..." if Localization.current_lang == "en" else "Проверка...")
        
        dlc_list = []
        path = self.integrity_manager.game_path
        
        if not path or not os.path.exists(path):
             QMessageBox.warning(self, Localization.get("error"), "Game path not set!")
             self.btn_verify.setEnabled(True)
             self.btn_verify.setText(Localization.get("verify_files"))
             return

        all_dlcs = self.db.all()
        for dlc_id in all_dlcs:
            if os.path.exists(os.path.join(path, dlc_id)):
                dlc_list.append((dlc_id, all_dlcs[dlc_id]['name']))
        
        self.verification_worker = IntegrityWorker(self.integrity_manager, dlc_list)
        self.verification_worker.finished.connect(self.on_verify_finished)
        self.verification_worker.start()

    def on_verify_status(self, dlc_id, status_code):
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'dlc_id') and widget.dlc_id == dlc_id:
                     icon = ""
                     if status_code == 0: icon = "✅"
                     elif status_code == 1: icon = "❌"
                     elif status_code == 2: icon = "⚠️"
                     elif status_code == 4: icon = "⏳"
                     
                     if not hasattr(widget, 'integrity_icon'):
                         lbl = QLabel(icon)
                         lbl.setStyleSheet("font-size: 16px; background: transparent; border: none;")
                         widget.layout().insertWidget(1, lbl)
                         widget.integrity_icon = lbl
                     else:
                         widget.integrity_icon.setText(icon)
                     
                     if status_code in [1, 2]:
                         if hasattr(widget, 'action_button'):
                             btn = widget.action_button
                             btn.setText("Repair" if Localization.current_lang == "en" else "Починить") 
                             btn.setStyleSheet(f"background-color: {COLOR_ACCENT}; color: {COLOR_BG_DARK}; border-radius: 6px; font-weight: 700;")
                             try: btn.clicked.disconnect()
                             except: pass
                             
                             info = self.db.get_by_id(dlc_id)
                             btn.clicked.connect(lambda checked, d=dlc_id, inf=info, b=btn: self.download_dlc(d, inf, b))
                             btn.setEnabled(True)
                     break

    def on_verify_finished(self):
        self.btn_verify.setEnabled(True)
        self.btn_verify.setText(Localization.get("verify_files"))
        QMessageBox.information(self, "Verification", "Integrity check completed!")

    def refresh_all_lists(self):
        self.parent_window.library_page.populate()
        self.parent_window.catalog_page.populate()
        self.parent_window.dashboard_page.check_stats()

class UnlockerPage(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        header = QLabel(Localization.get("unlocker"))
        header.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {COLOR_TEXT_WHITE}; letter-spacing: 1px;")
        layout.addWidget(header)
        
        self.status_card = QFrame()
        self.status_card.setObjectName("UnlockerStatusCard")
        self.status_card.setStyleSheet(f"""
            QFrame
                background-color: {COLOR_BG_LIGHT};
                border-radius: 16px;
                border: 1px solid
            }}
        """)
        self.status_card.setFixedHeight(100)
        
        status_layout = QHBoxLayout(self.status_card)
        status_layout.setContentsMargins(30, 20, 30, 20)
        
        self.status_icon = QLabel("❓")
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_icon.setStyleSheet("font-size: 40px; background: transparent;")
        
        status_info = QVBoxLayout()
        status_info.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.lbl_status_title = QLabel("STATUS") 
        self.lbl_status_title.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 13px; font-weight: 700; letter-spacing: 1.2px; background: transparent;")
        
        self.lbl_status_val = QLabel("Checking...")
        self.lbl_status_val.setStyleSheet("color: white; font-size: 20px; font-weight: 800; background: transparent;")
        
        status_info.addWidget(self.lbl_status_title)
        status_info.addWidget(self.lbl_status_val)
        
        status_layout.addWidget(self.status_icon)
        status_layout.addSpacing(20)
        status_layout.addLayout(status_info)
        status_layout.addStretch()
        
        layout.addWidget(self.status_card)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(20)
        
        self.btn_install = self.create_action_card("🚀", Localization.get("install_unlocker"), "#22C55E")
        self.btn_install.clicked.connect(self.install_unlocker)
        
        self.btn_config = self.create_action_card("📝", Localization.get("update_config"), "#3B82F6")
        self.btn_config.clicked.connect(self.update_config)
        
        self.btn_uninstall = self.create_action_card("🗑️", Localization.get("uninstall_unlocker"), "#EF4444")
        self.btn_uninstall.clicked.connect(self.uninstall_unlocker)
        
        actions_layout.addWidget(self.btn_install)
        actions_layout.addWidget(self.btn_config)
        actions_layout.addWidget(self.btn_uninstall)
        
        layout.addLayout(actions_layout)
        
        info_lbl = QLabel(Localization.get("unlocker_info"))
        info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_lbl.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 14px; margin-top: 10px; font-style: italic;")
        layout.addWidget(info_lbl)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(f"""
            QTextEdit {{
                background-color:
                color:
                border: 1px solid
                font-family: Consolas, monospace;
                font-size: 12px;
                padding: 10px;
                border-radius: 8px;
            }}
        """)
        self.console.setFixedHeight(150)
        self.console.hide() 
        
        self.btn_logs = QPushButton("Show Logs")
        self.btn_logs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logs.setCheckable(True)
        self.btn_logs.setStyleSheet(f"color: {COLOR_ACCENT}; background: transparent; border: none; font-weight: bold;")
        self.btn_logs.toggled.connect(lambda c: self.console.setVisible(c))
        
        layout.addStretch()
        layout.addWidget(self.btn_logs, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.console)
        
        self.update_status()

    def update_status(self):
        is_installed = UnlockerManager.check_status()
        if is_installed:
            self.lbl_status_val.setText(Localization.get("status_installed"))
            self.status_icon.setText("✅")
            self.status_card.setStyleSheet(f"""
                QFrame
                    background-color: {COLOR_BG_LIGHT};
                    border-radius: 16px;
                    border: 1px solid {COLOR_SUCCESS};
                }}
            """)
            self.lbl_status_val.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 20px; font-weight: 800; background: transparent;")
        else:
            self.lbl_status_val.setText(Localization.get("status_not_installed"))
            self.status_icon.setText("❌")
            self.status_card.setStyleSheet(f"""
                QFrame
                    background-color: {COLOR_BG_LIGHT};
                    border-radius: 16px;
                    border: 1px solid {COLOR_DANGER};
                }}
            """)
            self.lbl_status_val.setStyleSheet(f"color: {COLOR_DANGER}; font-size: 20px; font-weight: 800; background: transparent;")

    def create_action_card(self, icon, text, color):
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(140)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_LIGHT};
                border: 1px solid
                border-radius: 16px;
                text-align: center;
            }}
            QPushButton:hover {{
                border: 1px solid {color};
                background-color: {color}10;
            }}
        """)
        
        layout = QVBoxLayout(btn)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        
        lbl_text = QLabel(text)
        lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet(f"font-weight: 700; font-size: 14px; color: {COLOR_TEXT_WHITE}; background: transparent; border: none;")
        
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_text)
        
        return btn

    def install_unlocker(self):
        try:
            if not AdminElevator.is_admin():
                reply = QMessageBox.question(self, Localization.get("app_settings"), "Administrator rights required to install Unlocker.\nRestart as Administrator?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    AdminElevator.elevate()
                return

            self.console.setVisible(True)
            self.btn_logs.setChecked(True)
            self.parent_window.logger.widget = self.console
            self.parent_window.logger.log("Starting installation...", "INFO")

            success, msg = UnlockerManager.install_ea_unlocker(self.parent_window.logger)
            
            if success:
                self.parent_window.logger.log(msg, "SUCCESS")
                QMessageBox.information(self, Localization.get("success"), msg)
            else:
                self.parent_window.logger.log(msg, "ERROR")
                QMessageBox.critical(self, Localization.get("error"), msg)
                
            self.update_status()
            self.parent_window.dashboard_page.check_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "Critical Error", f"App crashed during install: {str(e)}")
            import traceback
            traceback.print_exc()

    def update_config(self):
        try:
            self.console.setVisible(True)
            self.btn_logs.setChecked(True)
            self.parent_window.logger.widget = self.console
            
            success, msg = UnlockerManager.update_sims4_config(self.parent_window.logger)
            if success:
                 self.parent_window.logger.log(msg, "SUCCESS")
                 QMessageBox.information(self, Localization.get("success"), msg)
            else:
                 self.parent_window.logger.log(msg, "ERROR")
                 QMessageBox.critical(self, Localization.get("error"), msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def uninstall_unlocker(self):
        try:
            if not AdminElevator.is_admin():
                reply = QMessageBox.question(self, Localization.get("app_settings"), "Administrator rights required to uninstall.\nRestart as Administrator?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    AdminElevator.elevate()
                return
                
            self.console.setVisible(True)
            self.btn_logs.setChecked(True)
            self.parent_window.logger.widget = self.console
            self.parent_window.logger.log("Starting uninstall...", "INFO")

            success, msg = UnlockerManager.uninstall_ea_unlocker(self.parent_window.logger)
            
            if success:
                self.parent_window.logger.log(msg, "SUCCESS")
                QMessageBox.information(self, Localization.get("success"), msg)
            else:
                self.parent_window.logger.log(msg, "ERROR")
                QMessageBox.critical(self, Localization.get("error"), msg)
                
            self.update_status()
            self.parent_window.dashboard_page.check_stats()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        

class Updater:
    @staticmethod
    def check_updates():
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                remote_ver = data.get("tag_name", "").lstrip("v")
                
                if remote_ver != APP_VERSION:
                    download_url = None
                    assets = data.get("assets", [])
                    for asset in assets:
                        if asset["name"].endswith(".exe"):
                            download_url = asset["browser_download_url"]
                            break
                    
                    if download_url:
                        return True, remote_ver, download_url, data.get("body", "")
            return False, None, None, None
        except Exception as e:
            print(f"Update check failed: {e}")
            return False, None, None, None

    @staticmethod
    def get_latest_news():
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                tag = data.get("tag_name", "Unknown")
                body = data.get("body", "No details.")
                published = data.get("published_at", "")[:10]
                return tag, body, published
        except:
            pass
        return None, None, None

    @staticmethod
    def download_update(url, progress_callback=None):
        try:
            temp_path = os.path.join(tempfile.gettempdir(), "LemonUnlocker_Update.exe")
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_length = int(r.headers.get('content-length', 0))
                dl = 0
                with open(temp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        if chunk: 
                            dl += len(chunk)
                            f.write(chunk)
                            if progress_callback and total_length > 0:
                                progress_callback(dl / total_length * 100)
            return True, temp_path
        except Exception as e:
            return False, str(e)

    @staticmethod
    def apply_update(new_exe_path):
        try:
            current_exe = sys.argv[0]
            batch_script = tempfile.mktemp(suffix=".bat")
            
            script_content = f"""
@echo off
timeout /t 2 /nobreak >nul
move /y "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
            with open(batch_script, "w") as f:
                f.write(script_content)
                
            subprocess.Popen(batch_script, shell=True)
            sys.exit(0)
        except Exception as e:
            return False, str(e)

class SettingsPage(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.config = ConfigManager()
        self.setup_ui()

    def setup_ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        header = QLabel(Localization.get("settings"))
        header.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {COLOR_TEXT_WHITE}; letter-spacing: 1px;")
        layout.addWidget(header)

        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_LIGHT};
                border-radius: 16px;
                border: 1px solid
            }}
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(20)

        lang_lbl = QLabel(Localization.get("language"))
        lang_lbl.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
        
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Русский", "English"])
        self.combo_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_lang.setFixedHeight(40)
        self.combo_lang.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLOR_BG_DARK};
                border: 1px solid
                border-radius: 8px;
                padding: 5px 15px;
                color: {COLOR_TEXT_WHITE};
                font-size: 14px;
                font-weight: 500;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: url(none);
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLOR_TEXT_GRAY};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLOR_BG_DARK};
                color: {COLOR_TEXT_WHITE};
                selection-background-color: {COLOR_ACCENT};
                selection-color: black;
                border: 1px solid
            }}
        """)
        
        current_lang = self.config.get("language", "ru")
        self.combo_lang.setCurrentIndex(0 if current_lang == "ru" else 1)
        self.combo_lang.currentIndexChanged.connect(self.change_language)
        
        container_layout.addWidget(lang_lbl)
        container_layout.addWidget(self.combo_lang)
        
        self.lbl_restart = QLabel(Localization.get("restart_required"))
        self.lbl_restart.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 13px; font-style: italic; background: transparent; border: none;")
        self.lbl_restart.setVisible(False)
        container_layout.addWidget(self.lbl_restart)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #334155; border: none; max-height: 1px;")
        container_layout.addWidget(line)

        update_title = QLabel("Updates")
        update_title.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
        container_layout.addWidget(update_title)

        update_row = QHBoxLayout()
        
        self.lbl_version = QLabel(f"Current Version: v{APP_VERSION}")
        self.lbl_version.setStyleSheet(f"color: {COLOR_TEXT_WHITE}; font-size: 14px; background: transparent;")
        
        self.btn_check_update = QPushButton("Check for Updates")
        self.btn_check_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_update.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_DARK};
                border: 1px solid {COLOR_ACCENT};
                color: {COLOR_ACCENT};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ACCENT};
                color: {COLOR_BG_DARK};
            }}
        """)
        self.btn_check_update.clicked.connect(self.check_updates)
        
        update_row.addWidget(self.lbl_version)
        update_row.addStretch()
        update_row.addWidget(self.btn_check_update)
        
        container_layout.addLayout(update_row)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        line2.setStyleSheet("background-color: #334155; border: none; max-height: 1px;")
        container_layout.addWidget(line2)
        
        
        about_title = QLabel(Localization.get("about"))
        about_title.setStyleSheet(f"color: {COLOR_TEXT_GRAY}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
        container_layout.addWidget(about_title)
        
        info_row = QHBoxLayout()
        
        app_logo = QLabel("🍋")
        app_logo.setStyleSheet("font-size: 48px; background: transparent; border: none;")
        
        info_text_layout = QVBoxLayout()
        lbl_app_name = QLabel(f"Lemon Unlocker v{APP_VERSION}")
        lbl_app_name.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {COLOR_ACCENT}; background: transparent; border: none;")
        
        lbl_creator = QLabel(Localization.get("created_by"))
        lbl_creator.setStyleSheet(f"font-size: 14px; color: {COLOR_TEXT_WHITE}; background: transparent; border: none;")
        
        info_text_layout.addWidget(lbl_app_name)
        info_text_layout.addWidget(lbl_creator)
        
        info_row.addWidget(app_logo)
        info_row.addSpacing(15)
        info_row.addLayout(info_text_layout)
        info_row.addStretch()
        
        container_layout.addLayout(info_row)
        
        links_layout = QHBoxLayout()
        links_layout.setSpacing(15)
        
        btn_channel = QPushButton(Localization.get("telegram_channel"))
        btn_channel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_channel.setIcon(QIcon())
        btn_channel.setText("📢  " + Localization.get("telegram_channel"))
        btn_channel.setStyleSheet(f"""
            QPushButton {{
                background-color:
                color: white; 
                border-radius: 8px; 
                padding: 10px 20px; 
                font-weight: bold;
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color:
        """)
        btn_channel.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/lemon4elosimshub")))
        
        btn_chat = QPushButton(Localization.get("telegram_chat"))
        btn_chat.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_chat.setText("💬  " + Localization.get("telegram_chat"))
        btn_chat.setStyleSheet(f"""
            QPushButton {{
                background-color:
                color: white; 
                border-radius: 8px; 
                padding: 10px 20px; 
                font-weight: bold;
                border: none;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color:
        """)
        btn_chat.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/+euBeCOkQDIdmNGJi")))
        
        links_layout.addWidget(btn_channel)
        links_layout.addWidget(btn_chat)
        links_layout.addStretch()
        
        container_layout.addLayout(links_layout)

        layout.addWidget(container)
        layout.addStretch()

    def change_language(self, index):
        lang_code = "ru" if index == 0 else "en"
        if lang_code != self.config.get("language", "ru"):
            self.config.set("language", lang_code)
            self.config.save()
            Localization.set_language(lang_code)
    def check_updates(self):
        self.btn_check_update.setText("Checking...")
        self.btn_check_update.setEnabled(False)
        QTimer.singleShot(100, self._perform_update_check)
        
    def _perform_update_check(self):
        has_update, version, url, notes = Updater.check_updates()
        if has_update:
            msg = f"New version v{version} available!\n\n{notes}\n\nUpdate now?"
            reply = QMessageBox.question(self, "Update Available", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.btn_check_update.setText("Downloading...")
                QTimer.singleShot(100, lambda: self._start_update_download(url))
            else:
                self.btn_check_update.setText("Check for Updates")
                self.btn_check_update.setEnabled(True)
        else:
            QMessageBox.information(self, "No Updates", "You are using the latest version.")
            self.btn_check_update.setText("Check for Updates")
            self.btn_check_update.setEnabled(True)

    def _start_update_download(self, url):
        success, path_or_err = Updater.download_update(url)
        if success:
            Updater.apply_update(path_or_err)
        else:
            QMessageBox.critical(self, "Update Failed", f"Failed to download update:\n{path_or_err}")
            self.btn_check_update.setText("Check for Updates")
            self.btn_check_update.setEnabled(True)

class LemonWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1000, 700)
        
        base_path = UnlockerManager.get_base_path()
        icon_path = os.path.join(base_path, "icon.png")
        if os.path.exists(icon_path):
             self.setWindowIcon(QIcon(icon_path))
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("Central")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.sidebar = Sidebar(self)
        self.main_layout.addWidget(self.sidebar)
        
        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"background-color: {COLOR_BG_DARK}; border-top-left-radius: 20px; border-bottom-left-radius: 20px;")
        
        self.right_layout = QVBoxLayout(self.content_area)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        
        self.title_bar = TitleBar(self)
        self.right_layout.addWidget(self.title_bar)
        
        self.pages = QStackedWidget()
        self.right_layout.addWidget(self.pages)
        
        self.dashboard_page = DashboardPage(self)
        self.library_page = DLCListPage(self, mode="installed")
        self.catalog_page = DLCListPage(self, mode="catalog")
        self.unlocker_page = UnlockerPage(self)
        self.settings_page = SettingsPage(self)
        
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.library_page)
        self.pages.addWidget(self.catalog_page)
        self.pages.addWidget(self.unlocker_page)
        self.pages.addWidget(self.settings_page)

        self.main_layout.addWidget(self.content_area)
        
        self.setStyleSheet(STYLE_SHEET)
        
        self.logger = ImprovedLogger()
        self.switch_page(0)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        self.sidebar.set_active(index)

if __name__ == "__main__":
    CrashHandler.install()
    
    app = QApplication(sys.argv)
    window = LemonWindow()
    window.show()
    sys.exit(app.exec())