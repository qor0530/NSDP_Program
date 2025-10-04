# ui_settings.py (리디자인 및 기능 추가 버전)
import customtkinter as ctk
from tkinter import messagebox
import winreg
import os
import json
import winshell
from itertools import chain
from utils import load_config

# ... (get_installed_apps 함수 등은 이전과 동일)
def get_installed_apps():
    final_apps_dict = {}
    for app in chain(get_apps_from_registry(), get_apps_from_start_menu()):
        final_apps_dict[app['name']] = app['path']
    final_apps_list = [{"name": name, "path": path} for name, path in final_apps_dict.items()]
    final_apps_list.sort(key=lambda x: x['name'].lower())
    return final_apps_list
def get_apps_from_registry():
    apps = {}
    blacklist = {"unins", "uninstall", "setup.exe", "redist.exe", "vcredist"}
    registry_paths = [ r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall" ]
    for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for reg_path in registry_paths:
            try:
                with winreg.OpenKey(hkey, reg_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    try: is_system_component = winreg.QueryValueEx(subkey, "SystemComponent")[0]
                                    except (FileNotFoundError, OSError): is_system_component = 0
                                    if display_name and not is_system_component:
                                        exe_path = ""
                                        try:
                                            icon_path_raw = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                            potential_path = icon_path_raw.split(',')[0].replace('"', '').strip()
                                            is_blacklisted = any(b in potential_path.lower() for b in blacklist)
                                            if not is_blacklisted and os.path.exists(potential_path) and potential_path.lower().endswith(".exe"):
                                                exe_path = potential_path
                                        except (FileNotFoundError, OSError): pass
                                        if not exe_path:
                                            try:
                                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                                app_name_guess = display_name.split(" ")[0].lower() + ".exe"
                                                potential_path = os.path.join(install_location, app_name_guess)
                                                if os.path.exists(potential_path):
                                                    exe_path = potential_path
                                            except (FileNotFoundError, OSError): pass
                                        if exe_path and os.path.exists(exe_path):
                                            apps[display_name] = exe_path
                                except (FileNotFoundError, OSError): pass
                        except OSError: pass
            except FileNotFoundError: pass
    return [{"name": name, "path": path} for name, path in apps.items()]
def get_apps_from_start_menu():
    apps = {}
    start_menu_paths = [ os.path.join(os.environ["PROGRAMDATA"], r"Microsoft\Windows\Start Menu\Programs"), os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs") ]
    for path in start_menu_paths:
        for root, _, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith(".lnk"):
                    try:
                        lnk_path = os.path.join(root, filename)
                        shortcut = winshell.shortcut(lnk_path)
                        target_path = shortcut.path
                        name = os.path.splitext(filename)[0]
                        if target_path and os.path.exists(target_path) and target_path.lower().endswith(".exe"):
                            if target_path not in apps.values():
                                apps[name] = target_path
                    except Exception: pass
    return [{"name": name, "path": path} for name, path in apps.items()]

class SettingsWindow:
    def __init__(self, root):
        self.window = ctk.CTkToplevel(root)
        self.window.title("설정")
        self.window.geometry("800x600")
        self.window.attributes("-topmost", True)
        
        self.config = load_config()
        self.app_vars = {}

        # --- 메인 레이아웃 ---
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # 1. 왼쪽 네비게이션 프레임
        navigation_frame = ctk.CTkFrame(self.window, corner_radius=0)
        navigation_frame.grid(row=0, column=0, sticky="nsew")
        navigation_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(navigation_frame, text="설정", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        
        general_button = ctk.CTkButton(navigation_frame, text="일반", command=lambda: self.show_frame("general"), corner_radius=0, height=40, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        general_button.grid(row=1, column=0, sticky="ew")
        
        app_lock_button = ctk.CTkButton(navigation_frame, text="앱 잠금", command=lambda: self.show_frame("app_lock"), corner_radius=0, height=40, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        app_lock_button.grid(row=2, column=0, sticky="ew")

        system_button = ctk.CTkButton(navigation_frame, text="시스템", command=lambda: self.show_frame("system"), corner_radius=0, height=40, border_spacing=10, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        system_button.grid(row=3, column=0, sticky="ew")

        # 2. 오른쪽 컨텐츠 프레임들
        self.frames = {}
        self.frames["general"] = self.create_general_frame()
        self.frames["app_lock"] = self.create_app_lock_frame()
        self.frames["system"] = self.create_system_frame()
        
        self.show_frame("general") # 기본으로 '일반' 프레임 표시

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.grid_forget()
        self.frames[frame_name].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
    def create_general_frame(self):
        frame = ctk.CTkFrame(self.window, fg_color="transparent")
        ctk.CTkLabel(frame, text="일반 설정", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        ctk.CTkLabel(frame, text="잠금 해제를 위해 풀어야 할 문제 수:").pack(anchor="w", pady=(20, 5))
        self.solve_count_spinbox = ctk.CTkEntry(frame)
        self.solve_count_spinbox.insert(0, self.config.get("unlock_condition", {}).get("value", 1))
        self.solve_count_spinbox.pack(anchor="w")
        
        ctk.CTkButton(frame, text="저장", command=self.save_settings).pack(anchor="w", pady=20)
        return frame

    def create_app_lock_frame(self):
        frame = ctk.CTkFrame(self.window, fg_color="transparent")
        ctk.CTkLabel(frame, text="앱 잠금 설정", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        scrollable_frame = ctk.CTkScrollableFrame(frame, label_text="PC에 설치된 프로그램 목록 (.exe)")
        scrollable_frame.pack(fill="both", expand=True, pady=(20,5))
        
        apps = get_installed_apps()
        blocked_apps = self.config.get("blocked_apps", [])
        for app in apps:
            var = ctk.StringVar(value="on" if os.path.normpath(app["path"]) in [os.path.normpath(p) for p in blocked_apps] else "off")
            cb = ctk.CTkCheckBox(scrollable_frame, text=app["name"], variable=var, onvalue="on", offvalue="off")
            cb.pack(anchor="w", padx=10, pady=2)
            self.app_vars[app["path"]] = var
        
        ctk.CTkButton(frame, text="저장", command=self.save_settings).pack(anchor="w", pady=20)
        return frame

    def create_system_frame(self):
        frame = ctk.CTkFrame(self.window, fg_color="transparent")
        ctk.CTkLabel(frame, text="시스템 설정", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")

        self.daily_unlock_var = ctk.StringVar(value="on" if self.config.get("daily_unlock_enabled", False) else "off")
        ctk.CTkSwitch(frame, text="일일 목표 달성 시 하루 동안 잠금 해제", variable=self.daily_unlock_var, onvalue="on", offvalue="off").pack(anchor="w", pady=20)
        
        ctk.CTkButton(frame, text="저장", command=self.save_settings).pack(anchor="w", pady=20)
        return frame

    def save_settings(self):
        # 일반 설정 저장
        self.config["unlock_condition"]["value"] = int(self.solve_count_spinbox.get())
        
        # 앱 잠금 설정 저장
        blocked_apps = []
        for path, var in self.app_vars.items():
            if var.get() == "on":
                blocked_apps.append(path.replace('\\', '/'))
        self.config["blocked_apps"] = blocked_apps

        # 시스템 설정 저장
        self.config["daily_unlock_enabled"] = self.daily_unlock_var.get() == "on"

        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("저장 완료", "설정이 성공적으로 저장되었습니다.\n(앱 잠금 등 일부 기능은 재시작해야 적용됩니다)")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("저장 실패", f"설정 저장 중 오류가 발생했습니다:\n{e}")