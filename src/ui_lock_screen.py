# ui_lock_screen.py (오류 수정 버전)
import customtkinter as ctk
from tkinter import messagebox
import random
from datetime import date
from utils import load_problems, check_solution, load_config, save_config, recommend_problem
from CTkCodeBox import *

class Theme:
    PRIMARY_BLUE = "#0B60B0"
    DEEP_BLUE = "#0B2447"
    BACKGROUND_DARK = "#181818"
    RED = "#F05454"
    GRAY_DARK = "#3F3F3F"
    CONSOLE_BG = "#2B2B2B"
    STAR_COLOR = "#FFC300"
    FONT_FAMILY = "Malgun Gothic"
    
class LockScreenApp:
    def __init__(self, root):
        # ... (__init__ 내용은 거의 동일)
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        ctk.set_appearance_mode("dark")
        loading_frame = ctk.CTkFrame(self.root, fg_color=Theme.BACKGROUND_DARK)
        loading_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(loading_frame, text="Loading...", font=(Theme.FONT_FAMILY, 24, "bold")).pack(pady=(20, 0))
        progressbar = ctk.CTkProgressBar(loading_frame, mode="indeterminate")
        progressbar.pack(pady=10, padx=100, fill="x")
        progressbar.start()
        self.root.update()
        self.problem = None
        self.config = load_config()
        self.target_solve_count = self.config['unlock_condition']['value']
        self.solved_count = 0
        self.points = self.config.get("user_points", 0)
        self.all_problems = load_problems()
        self.is_review_mode = False # 복습 모드 상태 변수 추가
        self.refresh_confirm_pending = False
        self.give_up_confirm_pending = False
        self.action_button_reset_timer = None
        loading_frame.destroy()
        self.setup_ui()
        self.load_new_problem()

    def on_submit(self):
        self.reset_action_buttons()
        user_code = self.code_editor.get("1.0", "end-1c")
        if not self.problem or not user_code.strip(): return
        
        self.output_console.configure(state="normal")
        self.output_console.delete("1.0", "end")
        
        result = check_solution(self.problem, user_code)

        if isinstance(result, str):
            if "정답" in result:
                self.handle_correct_answer()
            else: # 오답일 경우
                self.result_label.configure(text="")
                self.output_console.insert("1.0", result)
                # ▼▼▼ 틀린 문제 기록 ▼▼▼
                incorrect_ids = set(self.config.get("incorrect_history", []))
                incorrect_ids.add(self.problem["id"])
                self.config["incorrect_history"] = list(incorrect_ids)
                save_config(self.config)

        elif isinstance(result, dict): # 에러/시간초과일 경우
            self.result_label.configure(text="")
            error_text = ""
            if result["status"] == "error":
                error_text = f'테스트 케이스 #{result["case_num"]} 에서 에러 발생:\n\n{result["stderr"]}'
            elif result["status"] == "timeout":
                error_text = f'테스트 케이스 #{result["case_num"]} 에서 시간 초과!'
            elif result["status"] == "memory_limit_exceeded":
                error_text = f'테스트 케이스 #{result["case_num"]} 에서 메모리 초과!'
            self.output_console.insert("1.0", error_text)
            # ▼▼▼ 틀린 문제 기록 ▼▼▼
            incorrect_ids = set(self.config.get("incorrect_history", []))
            incorrect_ids.add(self.problem["id"])
            self.config["incorrect_history"] = list(incorrect_ids)
            save_config(self.config)
            
        self.output_console.configure(state="disabled")

    def load_new_problem(self):
        self.reset_action_buttons()
        self.output_console.configure(state="normal")
        self.output_console.delete("1.0", "end")
        self.output_console.configure(state="disabled")
        
        if not self.is_review_mode: # 일반 모드일 경우
            self.problem = recommend_problem(self.all_problems, self.config.get("solve_history", []))
        else: # 복습 모드일 경우
            incorrect_ids = self.config.get("incorrect_history", [])
            review_problems = [p for p in self.all_problems if p["id"] in incorrect_ids]
            if review_problems:
                self.problem = random.choice(review_problems)
            else:
                self.problem = None # 복습할 문제도 더 이상 없는 경우

        if not self.problem: # 풀 문제가 더 이상 없는 경우
            incorrect_ids = self.config.get("incorrect_history", [])
            if incorrect_ids and not self.is_review_mode:
                # 복습 모드로 전환
                self.is_review_mode = True
                self.problem_label.configure(text="모든 문제를 해결했습니다! 이제 틀렸던 문제에 다시 도전하세요.")
                self.root.after(2000, self.load_new_problem) # 2초 후 복습 문제 시작
            else:
                # 모든 복습까지 완료
                self.problem_label.configure(text="완벽합니다! 모든 문제를 마스터했습니다. 축하합니다!")
                self.submit_button.configure(state="disabled")
                self.refresh_button.configure(state="disabled")
                self.give_up_button.configure(state="disabled")
            return

        # ... 이하 UI 업데이트 로직은 이전과 동일 ...
        stars = self.problem.get('stars', 1)
        points = stars * 2
        self.difficulty_label.configure(text="★" * stars)
        self.problem_label.configure(text=f"{self.problem['title']} ({points}P)\n\n{self.problem['description']}")
        time_limit = self.problem.get("time_limit", 5)
        mem_limit = self.problem.get("memory_limit", 128)
        self.limits_label.configure(text=f"제한: {time_limit}초, {mem_limit}MB")
        if self.problem.get("hint"): self.hint_label.configure(text=f"💡 힌트: {self.problem['hint']}")
        else: self.hint_label.configure(text="")
        self.input_example_box.configure(state="normal")
        self.output_example_box.configure(state="normal")
        self.input_example_box.delete("1.0", "end")
        self.output_example_box.delete("1.0", "end")
        if self.problem['testcases']:
            input_text = self.problem['testcases'][0]['input']
            output_text = self.problem['testcases'][0]['output']
            self.input_example_box.insert("1.0", f"> Input\n---\n{input_text}")
            self.output_example_box.insert("1.0", f"> Output\n---\n{output_text}")
        self.input_example_box.configure(state="disabled")
        self.output_console.configure(state="disabled")
        self.code_editor.delete("1.0", "end")
        self.result_label.configure(text="")
        self.update_status()

    def handle_correct_answer(self, is_give_up=False):
        if not self.problem: return
            
        self.reset_action_buttons()
        self.solved_count += 1
        
        gain = 0
        result_text = ""

        if not is_give_up:
            stars = self.problem.get("stars", 1)
            gain = stars * 2
            self.points += gain
            self.config["user_points"] = self.points
            
            # 풀이 기록(solve_history)에 현재 문제 추가 (중복 방지)
            solved_ids = {item['id'] for item in self.config.get("solve_history", [])}
            if self.problem["id"] not in solved_ids:
                self.config.get("solve_history", []).append({"id": self.problem["id"], "stars": stars})
            
            # 틀린 문제 기록(incorrect_history)에서 현재 문제 제거
            incorrect_ids = set(self.config.get("incorrect_history", []))
            if self.problem["id"] in incorrect_ids:
                incorrect_ids.remove(self.problem["id"])
                self.config["incorrect_history"] = list(incorrect_ids)

            result_text = f"정답입니다! {gain}P 획득!"
        
        self.update_status()

        if self.solved_count >= self.target_solve_count:
            if self.config.get("daily_unlock_enabled", False):
                self.config["last_completion_date"] = str(date.today())
            save_config(self.config)
            final_text = result_text + " 목표 달성! 잠금 해제됩니다." if not is_give_up else "목표 달성! 잠금 해제됩니다."
            self.result_label.configure(text=final_text, text_color="lightgreen")
            self.root.after(2000, self.root.destroy)
        else:
            save_config(self.config)
            final_text = result_text + " 다음 문제로 넘어갑니다." if not is_give_up else "다음 문제로 넘어갑니다."
            self.result_label.configure(text=final_text, text_color="lightgreen")
            self.root.after(2000, self.load_new_problem)

# ... (Theme 클래스 및 다른 함수들은 이전과 동일)
class Theme:
    PRIMARY_BLUE = "#0B60B0"
    DEEP_BLUE = "#0B2447"
    BACKGROUND_DARK = "#181818"
    RED = "#F05454"
    GRAY_DARK = "#3F3F3F"
    CONSOLE_BG = "#2B2B2B"
    STAR_COLOR = "#FFC300"
    FONT_FAMILY = "Malgun Gothic"

class LockScreenApp:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        ctk.set_appearance_mode("dark")
        loading_frame = ctk.CTkFrame(self.root, fg_color=Theme.BACKGROUND_DARK)
        loading_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(loading_frame, text="Loading...", font=(Theme.FONT_FAMILY, 24, "bold")).pack(pady=(20, 0))
        progressbar = ctk.CTkProgressBar(loading_frame, mode="indeterminate")
        progressbar.pack(pady=10, padx=100, fill="x")
        progressbar.start()
        self.root.update()
        self.problem = None
        self.config = load_config()
        self.target_solve_count = self.config['unlock_condition']['value']
        self.solved_count = 0
        self.points = self.config.get("user_points", 0)
        self.all_problems = load_problems()
        self.refresh_confirm_pending = False
        self.give_up_confirm_pending = False
        self.action_button_reset_timer = None
        loading_frame.destroy()
        self.setup_ui()
        self.load_new_problem()

    def setup_ui(self):
        self.root.title("Not Solve, Don't Play")
        self.main_frame = ctk.CTkFrame(self.root, fg_color=Theme.BACKGROUND_DARK)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        status_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        status_frame.pack(pady=10, padx=40, fill="x")
        self.status_label = ctk.CTkLabel(status_frame, text="", font=(Theme.FONT_FAMILY, 18, "bold"))
        self.status_label.pack(side="left")
        self.points_label = ctk.CTkLabel(status_frame, text="", font=(Theme.FONT_FAMILY, 18, "bold"))
        self.points_label.pack(side="right")
        problem_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        problem_frame.pack(pady=10, padx=40, fill="x")
        self.difficulty_label = ctk.CTkLabel(problem_frame, text="", font=(Theme.FONT_FAMILY, 20, "bold"), text_color=Theme.STAR_COLOR)
        self.difficulty_label.pack()
        self.problem_label = ctk.CTkLabel(problem_frame, text="...", font=(Theme.FONT_FAMILY, 20), wraplength=1200)
        self.problem_label.pack(pady=5)
        self.limits_label = ctk.CTkLabel(problem_frame, text="", font=(Theme.FONT_FAMILY, 12, "italic"), text_color=Theme.GRAY_DARK)
        self.limits_label.pack(pady=2)
        self.hint_label = ctk.CTkLabel(problem_frame, text="", font=(Theme.FONT_FAMILY, 14, "italic"))
        self.hint_label.pack(pady=5)
        io_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        io_frame.pack(pady=10, padx=40, fill="x", expand=True, ipady=10)
        self.input_example_box = ctk.CTkTextbox(io_frame, font=("Courier New", 14), corner_radius=10, fg_color=Theme.CONSOLE_BG, border_width=1, border_color=Theme.GRAY_DARK)
        self.input_example_box.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.output_example_box = ctk.CTkTextbox(io_frame, font=("Courier New", 14), corner_radius=10, fg_color=Theme.CONSOLE_BG, border_width=1, border_color=Theme.GRAY_DARK)
        self.output_example_box.pack(side="right", fill="both", expand=True, padx=(5, 0))
        editor_console_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        editor_console_frame.pack(pady=10, padx=40, fill="both", expand=True)
        self.code_editor = CTkCodeBox(editor_console_frame, language="python", font=("Courier New", 14), corner_radius=10, border_width=1, border_color=Theme.GRAY_DARK)
        self.code_editor.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.output_console = ctk.CTkTextbox(editor_console_frame, font=("Courier New", 14), corner_radius=10, fg_color=Theme.CONSOLE_BG, border_width=1, border_color=Theme.GRAY_DARK)
        self.output_console.pack(side="right", fill="both", expand=True, padx=(5, 0))
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.pack(pady=10, padx=40, fill="x")
        self.result_label = ctk.CTkLabel(bottom_frame, text="", font=(Theme.FONT_FAMILY, 16, "bold"))
        self.result_label.pack(side="left", expand=True)
        button_container = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        button_container.pack(side="right")
        self.refresh_button = ctk.CTkButton(button_container, text="새로고침 (2P)", command=self.on_refresh, font=(Theme.FONT_FAMILY, 16), height=40, fg_color=Theme.GRAY_DARK, hover_color=Theme.DEEP_BLUE, corner_radius=8)
        self.refresh_button.pack(side="left", padx=(0, 5))
        self.give_up_button = ctk.CTkButton(button_container, text="문제 포기 (10P)", command=self.on_give_up, font=(Theme.FONT_FAMILY, 16), height=40, fg_color=Theme.GRAY_DARK, hover_color=Theme.DEEP_BLUE, corner_radius=8)
        self.give_up_button.pack(side="left", padx=(5, 20))
        self.submit_button = ctk.CTkButton(button_container, text="제출", command=self.on_submit, font=(Theme.FONT_FAMILY, 18, "bold"), height=40, fg_color=Theme.PRIMARY_BLUE, corner_radius=8)
        self.submit_button.pack(side="left")
        self.root.bind("<Control-f>", self.on_force_solve)

    def handle_correct_answer(self, is_give_up=False):
        # ▼▼▼ 오류 수정: 풀 문제가 없는 경우 즉시 함수 종료 ▼▼▼
        if not self.problem:
            return
            
        self.reset_action_buttons()
        self.solved_count += 1
        
        gain = 0
        result_text = ""

        if not is_give_up:
            stars = self.problem.get("stars", 1)
            gain = stars * 2
            self.points += gain
            self.config["user_points"] = self.points
            self.config.get("solve_history", []).append({"id": self.problem["id"], "stars": stars})
            result_text = f"정답입니다! {gain}P 획득!"
        
        self.update_status()

        if self.solved_count >= self.target_solve_count:
            if self.config.get("daily_unlock_enabled", False):
                self.config["last_completion_date"] = str(date.today())
            save_config(self.config)
            final_text = result_text + " 목표 달성! 잠금 해제됩니다." if not is_give_up else "목표 달성! 잠금 해제됩니다."
            self.result_label.configure(text=final_text, text_color="lightgreen")
            self.root.after(2000, self.root.destroy)
        else:
            save_config(self.config)
            final_text = result_text + " 다음 문제로 넘어갑니다." if not is_give_up else "다음 문제로 넘어갑니다."
            self.result_label.configure(text=final_text, text_color="lightgreen")
            self.root.after(2000, self.load_new_problem)

    # ... (load_new_problem, on_submit 등 나머지 함수는 이전과 동일)
    def load_new_problem(self):
        self.reset_action_buttons()
        self.output_console.configure(state="normal")
        self.output_console.delete("1.0", "end")
        self.output_console.configure(state="disabled")
        self.problem = recommend_problem(self.all_problems, self.config.get("solve_history", []))
        if not self.problem:
             self.problem_label.configure(text="모든 문제를 해결했습니다! 축하합니다!")
             self.submit_button.configure(state="disabled")
             self.refresh_button.configure(state="disabled")
             self.give_up_button.configure(state="disabled")
             return
        stars = self.problem.get('stars', 1)
        points = stars * 2
        self.difficulty_label.configure(text="★" * stars)
        self.problem_label.configure(text=f"{self.problem['title']} ({points}P)\n\n{self.problem['description']}")
        time_limit = self.problem.get("time_limit", 5)
        mem_limit = self.problem.get("memory_limit", 128)
        self.limits_label.configure(text=f"제한: {time_limit}초, {mem_limit}MB")
        if self.problem.get("hint"): self.hint_label.configure(text=f"💡 힌트: {self.problem['hint']}")
        else: self.hint_label.configure(text="")
        self.input_example_box.configure(state="normal")
        self.output_example_box.configure(state="normal")
        self.input_example_box.delete("1.0", "end")
        self.output_example_box.delete("1.0", "end")
        if self.problem['testcases']:
            input_text = self.problem['testcases'][0]['input']
            output_text = self.problem['testcases'][0]['output']
            self.input_example_box.insert("1.0", f"> Input\n---\n{input_text}")
            self.output_example_box.insert("1.0", f"> Output\n---\n{output_text}")
        self.input_example_box.configure(state="disabled")
        self.output_console.configure(state="disabled")
        self.code_editor.delete("1.0", "end")
        self.result_label.configure(text="")
        self.update_status()
    def on_submit(self):
        self.reset_action_buttons()
        user_code = self.code_editor.get("1.0", "end-1c")
        if not self.problem or not user_code.strip(): return
        self.output_console.configure(state="normal")
        self.output_console.delete("1.0", "end")
        result = check_solution(self.problem, user_code)
        if isinstance(result, str):
            if "정답" in result:
                self.handle_correct_answer()
            else:
                self.result_label.configure(text="")
                self.output_console.insert("1.0", result)
        elif isinstance(result, dict):
            self.result_label.configure(text="")
            error_text = ""
            if result["status"] == "error":
                error_text = f'테스트 케이스 #{result["case_num"]} 에서 에러 발생:\n\n{result["stderr"]}'
            elif result["status"] == "timeout":
                error_text = f'테스트 케이스 #{result["case_num"]} 에서 시간 초과!'
            elif result["status"] == "memory_limit_exceeded":
                error_text = f'테스트 케이스 #{result["case_num"]} 에서 메모리 초과!'
            self.output_console.insert("1.0", error_text)
        self.output_console.configure(state="disabled")
    def on_refresh(self):
        self.reset_action_buttons(except_button="refresh")
        cost = 2
        if self.points < cost:
            self.result_label.configure(text="포인트가 부족합니다.", text_color="lightcoral")
            self.root.after(2000, lambda: self.result_label.configure(text=""))
            return
        if self.refresh_confirm_pending:
            self.points -= cost
            self.config["user_points"] = self.points
            save_config(self.config)
            self.result_label.configure(text=f"{cost} 포인트를 사용했습니다.", text_color="white")
            self.root.after(1000, self.load_new_problem)
        else:
            self.refresh_confirm_pending = True
            self.refresh_button.configure(text=f"확인 ({cost}P 사용)", fg_color=Theme.RED)
            self.action_button_reset_timer = self.root.after(3000, self.reset_action_buttons)
    def on_give_up(self):
        self.reset_action_buttons(except_button="give_up")
        cost = 10
        if self.points < cost:
            self.result_label.configure(text="포인트가 부족합니다.", text_color="lightcoral")
            self.root.after(2000, lambda: self.result_label.configure(text=""))
            return
        if self.give_up_confirm_pending:
            self.points -= cost
            self.config["user_points"] = self.points
            save_config(self.config)
            self.result_label.configure(text=f"{cost}P 사용! 문제를 포기합니다.", text_color="white")
            self.handle_correct_answer(is_give_up=True)
        else:
            self.give_up_confirm_pending = True
            self.give_up_button.configure(text=f"확인 ({cost}P 사용)", fg_color=Theme.RED)
            self.action_button_reset_timer = self.root.after(3000, self.reset_action_buttons)
    def reset_action_buttons(self, except_button=None):
        if self.action_button_reset_timer:
            self.root.after_cancel(self.action_button_reset_timer)
            self.action_button_reset_timer = None
        if except_button != "refresh":
            self.refresh_confirm_pending = False
            self.refresh_button.configure(text="새로고침 (2P)", fg_color=Theme.GRAY_DARK)
        if except_button != "give_up":
            self.give_up_confirm_pending = False
            self.give_up_button.configure(text="문제 포기 (10P)", fg_color=Theme.GRAY_DARK)
    def update_status(self):
        self.status_label.configure(text=f"성공: {self.solved_count} / {self.target_solve_count}")
        self.points_label.configure(text=f"포인트: {self.points}P")
    def on_force_solve(self, event=None):
        self.handle_correct_answer()