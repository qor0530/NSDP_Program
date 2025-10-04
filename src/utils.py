# utils.py
import json
import subprocess
import os
import threading
import psutil
import time
import random
import sys

# ... (load_problems, load_config, save_config, judge_single_case 함수는 이전과 동일) ...
def load_problems(filepath="problems.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError: return []
def load_config(filepath="config.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"unlock_condition": {"mode": "count", "value": 1}, "blocked_apps": [], "user_points": 0, "daily_unlock_enabled": True, "last_completion_date": "", "solve_history": []}
def save_config(data, filepath="config.json"):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"설정 저장 중 오류 발생: {e}")
def judge_single_case(user_code: str, input_data: str, time_limit: int, memory_limit_mb: int) -> dict:
    solution_filename = "temp_solution.py"
    with open(solution_filename, "w", encoding="utf-8") as f: f.write(user_code)
    memory_limit_bytes = memory_limit_mb * 1024 * 1024
    try:
        proc = subprocess.Popen(['python', solution_filename],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, encoding="utf-8")
        p = psutil.Process(proc.pid)
        memory_exceeded = threading.Event()
        def monitor_memory():
            while proc.poll() is None:
                try:
                    if p.memory_info().rss > memory_limit_bytes:
                        memory_exceeded.set()
                        p.kill()
                        return
                except psutil.NoSuchProcess: return
                time.sleep(0.05)
        mon_thread = threading.Thread(target=monitor_memory)
        mon_thread.daemon = True
        mon_thread.start()
        stdout, stderr = proc.communicate(input=input_data, timeout=time_limit)
        if memory_exceeded.is_set():
            return {"status": "memory_limit_exceeded"}
        if stderr:
            return {"status": "error", "stderr": stderr}
        return {"status": "success", "output": stdout.strip()}
    except subprocess.TimeoutExpired:
        proc.kill()
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error", "stderr": str(e)}
    finally:
        if os.path.exists(solution_filename): os.remove(solution_filename)

# ▼▼▼ 레벨 계산 함수 새로 추가 ▼▼▼
def calculate_user_level(solve_history, max_history=10):
    """최근 풀이 기록을 바탕으로 사용자의 레벨(평균 별점)을 계산합니다."""
    if not solve_history:
        return 1 # 기록이 없으면 레벨 1로 시작

    # 최근 N개의 기록만 사용
    recent_history = solve_history[-max_history:]
    average_stars = sum(item['stars'] for item in recent_history) / len(recent_history)
    
    # 레벨은 반올림하여 정수로 만듦
    return round(average_stars)

# ▼▼▼ 문제 추천 함수 새로 추가 ▼▼▼
def recommend_problem(all_problems, solve_history):
    """사용자 레벨에 맞는 문제를 추천합니다."""
    user_level = calculate_user_level(solve_history)
    print(f"[추천 시스템] 현재 사용자 레벨: {user_level}")
    
    solved_ids = {item['id'] for item in solve_history}
    unsolved_problems = [p for p in all_problems if p['id'] not in solved_ids]

    if not unsolved_problems:
        return None # 모든 문제를 다 푼 경우

    # 1순위: 현재 레벨과 같거나 +1 높은 문제
    candidates = [p for p in unsolved_problems if user_level <= p.get('stars', 1) <= user_level + 1]
    
    # 2순위: 후보가 없으면, 풀지 않은 문제 전체에서 선택
    if not candidates:
        print("[추천 시스템] 적합한 난이도의 문제가 없어, 풀지 않은 모든 문제 중에서 추천합니다.")
        candidates = unsolved_problems

    return random.choice(candidates)


def check_solution(problem, user_code):
    # ... (이 함수는 이전과 동일)
    time_limit = problem.get("time_limit", 5)
    memory_limit_mb = problem.get("memory_limit", 128)
    for i, case in enumerate(problem["testcases"]):
        input_data = case["input"]
        expected_output = case["output"]
        result = judge_single_case(user_code, input_data, time_limit, memory_limit_mb)
        if result["status"] == "success":
            if result["output"] != expected_output:
                return f"{i+1}번 테스트 케이스에서 '오답'\n- 기대값: {expected_output}\n- 실제값: {result['output']}"
        else:
            result["case_num"] = i + 1
            return result
    return "정답입니다!"

def load_config(filepath="config.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # ▼▼▼ 기본 설정에 incorrect_history 추가 ▼▼▼
        return {"unlock_condition": {"mode": "count", "value": 1}, "blocked_apps": [], "user_points": 0, 
                "daily_unlock_enabled": True, "last_completion_date": "", "solve_history": [], "incorrect_history": []}


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # src 폴더 구조에 맞게 경로를 한 단계 위로 조정
    try:
        base_path = sys._MEIPASS
    except Exception:
        # 개발 환경에서는 현재 파일 위치의 부모 폴더(프로젝트 루트)를 기준으로 설정
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
    # resources 폴더 안의 파일을 찾도록 경로 조합
    return os.path.join(base_path, "resources", relative_path)