import pystray
from PIL import Image
import customtkinter as ctk
import tkinter as tk
import threading
import time
import psutil
import os
from datetime import date # 날짜 확인을 위해 추가
from utils import load_config, save_config # save_config 추가
from ui_settings import SettingsWindow
from ui_lock_screen import LockScreenApp

class AppController:
    def __init__(self):
        self.root = None
        self.settings_window_instance = None
        self.lock_screen_instance = None
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
    
    def open_settings_window(self):
        if self.settings_window_instance and self.settings_window_instance.window.winfo_exists():
            self.settings_window_instance.window.lift()
        else:
            self.settings_window_instance = SettingsWindow(self.root)

    def start_lockdown(self):
        # ▼▼▼ 일일 잠금 해제 확인 로직 추가 ▼▼▼
        config = load_config()
        if config.get("daily_unlock_enabled", False):
            today_str = str(date.today())
            if config.get("last_completion_date") == today_str:
                print("[시스템] 오늘은 이미 목표를 달성했습니다. 잠금을 시작하지 않습니다.")
                return
        # ▲▲▲ 일일 잠금 해제 확인 로직 추가 ▲▲▲

        if self.lock_screen_instance and self.lock_screen_instance.root.winfo_exists():
            return
        
        lock_window = ctk.CTkToplevel(self.root)
        self.lock_screen_instance = LockScreenApp(lock_window)

    def app_monitor(self):
        config = load_config()
        blocked_apps_paths = [os.path.normpath(p) for p in config.get("blocked_apps", [])]
        if not blocked_apps_paths:
            print("[감시] 감시할 앱이 없습니다.")
            return
        print(f"[감시] 다음 앱들을 감시합니다: {blocked_apps_paths}")
        while not self.stop_monitoring.is_set():
            for proc in psutil.process_iter(['exe']):
                try:
                    exe_path = proc.info['exe']
                    if exe_path:
                        proc_path = os.path.normpath(exe_path)
                        if proc_path in blocked_apps_paths:
                            print(f"[감시] 잠긴 프로그램 실행 감지: {proc_path}")
                            self.root.after(0, self.start_lockdown)
                            return
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            time.sleep(3)
        print("[감시] 감시 스레드를 종료합니다.")

    def start_monitoring_thread(self):
        # ▼▼▼ 프로그램 시작 시 일일 잠금 해제 확인 ▼▼▼
        config = load_config()
        if config.get("daily_unlock_enabled", False):
            today_str = str(date.today())
            if config.get("last_completion_date") == today_str:
                print("[시스템] 오늘은 이미 목표를 달성했습니다. 자동 감시를 시작하지 않습니다.")
                return # 감시 스레드를 아예 시작하지 않음
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
        
        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(target=self.app_monitor)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def run_gui(self, icon):
        self.root = ctk.CTk()
        self.root.withdraw()
        self.start_monitoring_thread()
        icon.visible = True
        self.root.mainloop()

    def exit_app(self, icon, item):
        self.stop_monitoring.set()
        icon.stop()
        if self.root:
            self.root.quit()

def main():
    try:
        image = Image.open("icon.png")
    except (FileNotFoundError, OSError) as e:
        print(f"Error: icon.png 파일을 불러올 수 없습니다. ({e})")
        return
    
    controller = AppController()
    
    menu = (pystray.MenuItem('설정 열기', controller.open_settings_window),
            pystray.MenuItem('잠금 시작 (수동)', controller.start_lockdown),
            pystray.MenuItem('종료', controller.exit_app))

    icon = pystray.Icon("NotSolveDontPlay", image, "Not Solve, Don't Play", menu)
    
    gui_thread = threading.Thread(target=controller.run_gui, args=(icon,))
    gui_thread.daemon = True
    gui_thread.start()
    
    icon.run()