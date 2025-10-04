# ui_lock_screen.py (자체 코드 에디터 구현 버전)
import customtkinter as ctk
from tkinter import messagebox
import random
from datetime import date
from utils import load_problems, check_solution, load_config, save_config, recommend_problem
from pygments import lex
from pygments.lexers import PythonLexer

# --- 디자인 시스템 색상 및 폰트 정의 ---
class Theme:
    PRIMARY_BLUE = "#0B60B0"
    DEEP_BLUE = "#0B2447"
    BACKGROUND_DARK = "#181818"
    RED = "#F05454"
    GRAY_DARK = "#3F3F3F"
    CONSOLE_BG = "#2B2B2B"
    STAR_COLOR = "#FFC300"
    FONT_FAMILY = "Malgun Gothic"

# ▼▼▼ 우리만의 새로운 코드 에디터 위젯 ▼▼▼
class CodeEditor(ctk.CTkFrame):
    def __init__(self, master, language="python", **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.line_numbers = ctk.CTkTextbox(self, width=40, font=("Courier New", 14), state="disabled",
                                           fg_color=Theme.CONSOLE_BG, border_width=0, corner_radius=0)
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        self.code_text = ctk.CTkTextbox(self, font=("Courier New", 14), wrap="none",
                                        fg_color=Theme.CONSOLE_BG, border_width=0, corner_radius=0)
        self.code_text.grid(row=0, column=1, sticky="nsew")

        self.code_text.bind("<KeyRelease>", self.on_key_release)
        self.code_text.bind("<Return>", self.on_return)
        
        self.lexer = PythonLexer()
        self.tag_colors = {
            "Token.Keyword": "#cc7832",
            "Token.Name.Builtin": "#9876aa",
            "Token.String": "#6a8759",
            "Token.Comment": "#808080",
            "Token.Operator": "#cc7832",
            "Token.Number": "#6897bb",
            "Token.Name.Function": "#ffc66d",
            "Token.Name.Class": "#ffc66d",
        }
        for token, color in self.tag_colors.items():
            self.code_text.tag_config(str(token), foreground=color)

    def on_key_release(self, event=None):
        self.update_line_numbers()
        self.highlight_syntax()
        
    def on_return(self, event=None):
        self.code_text.insert(tk.INSERT, "\n")
        
        current_line_number = int(self.code_text.index(tk.INSERT).split('.')[0])
        if current_line_number > 1:
            previous_line = self.code_text.get(f"{current_line_number-1}.0", f"{current_line_number-1}.end")
            indentation = len(previous_line) - len(previous_line.lstrip())
            
            if previous_line.strip().endswith(":"):
                indentation += 4
                
            self.code_text.insert(tk.INSERT, " " * indentation)
        return "break"
        
    def update_line_numbers(self, event=None):
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        lines = self.code_text.get("1.0", "end-1c").count("\n") + 1
        line_numbers_text = "\n".join(str(i) for i in range(1, lines + 1))
        
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.configure(state="disabled")
        
    def highlight_syntax(self, event=None):
        for tag in self.tag_colors:
            self.code_text.tag_remove(tag, "1.0", "end")

        text = self.code_text.get("1.0", "end-1c")
        
        for token, content in lex(text, self.lexer):
            start_index = self.code_text.index(f"1.0 + {len(self.code_text.get('1.0', 'insert'))}c")
            
            start = self.code_text.index(f"1.0 + {len(text) - len(text.lstrip())}c")
            
            lines = text.splitlines()
            
            start_line = 1
            start_col = 0
            
            text_till_token = text[:text.find(content)]
            
            lines_before = text_till_token.split('\n')
            start_line = len(lines_before)
            start_col = len(lines_before[-1])
            
            end_line = start_line
            end_col = start_col + len(content)

            start_index = f"{start_line}.{start_col}"
            end_index = f"{end_line}.{end_col}"

            if str(token) in self.tag_colors:
                self.code_text.tag_add(str(token), start_index, end_index)
            text = text[text.find(content)+len(content):]

    def get(self, start="1.0", end="end-1c"):
        return self.code_text.get(start, end)
    
    def delete(self, start="1.0", end="end"):
        self.code_text.delete(start, end)
        self.on_key_release()
# ▲▲▲ 우리만의 새로운 코드 에디터 위젯 ▲▲▲

class LockScreenApp:
    def __init__(self, root):
        self.root = root
        # ... (__init__의 나머지 부분은 동일)
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
        self.is_review_mode = False
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

        # ... (상단 UI는 동일)
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

        # ▼▼▼ CTkCodeBox 대신 우리가 만든 CodeEditor 사용 ▼▼▼
        self.code_editor = CodeEditor(editor_console_frame, fg_color=Theme.CONSOLE_BG, corner_radius=10, border_width=1, border_color=Theme.GRAY_DARK)
        self.code_editor.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.output_console = ctk.CTkTextbox(editor_console_frame, font=("Courier New", 14), corner_radius=10, fg_color=Theme.CONSOLE_BG, border_width=1, border_color=Theme.GRAY_DARK)
        self.output_console.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # ... (하단 UI는 동일)
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

    # ... (on_submit, load_new_problem 등 나머지 함수는 이전과 동일)
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
                incorrect_ids = set(self.config.get("incorrect_history", []))
                incorrect_ids.add(self.problem["id"])
                self.config["incorrect_history"] = list(incorrect_ids)
                save_config(self.config)
        elif isinstance(result, dict):
            self.result_label.configure(text="")
            error_text = ""
            if result["status"] == "error": error_text = f'테스트 케이스 #{result["case_num"]} 에서 에러 발생:\n\n{result["stderr"]}'
            elif result["status"] == "timeout": error_text = f'테스트 케이스 #{result["case_num"]} 에서 시간 초과!'
            elif result["status"] == "memory_limit_exceeded": error_text = f'테스트 케이스 #{result["case_num"]} 에서 메모리 초과!'
            self.output_console.insert("1.0", error_text)
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
        if not self.is_review_mode:
            self.problem = recommend_problem(self.all_problems, self.config.get("solve_history", []))
        else:
            incorrect_ids = self.config.get("incorrect_history", [])
            review_problems = [p for p in self.all_problems if p["id"] in incorrect_ids]
            self.problem = random.choice(review_problems) if review_problems else None
        if not self.problem:
            incorrect_ids = self.config.get("incorrect_history", [])
            if incorrect_ids and not self.is_review_mode:
                self.is_review_mode = True
                self.problem_label.configure(text="모든 문제를 해결했습니다! 이제 틀렸던 문제에 다시 도전하세요.")
                self.root.after(2000, self.load_new_problem)
            else:
                self.problem_label.configure(text="완벽합니다! 모든 문제를 마스터했습니다. 축하합니다!")
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
            solved_ids = {item['id'] for item in self.config.get("solve_history", [])}
            if self.problem["id"] not in solved_ids:
                self.config.get("solve_history", []).append({"id": self.problem["id"], "stars": stars})
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