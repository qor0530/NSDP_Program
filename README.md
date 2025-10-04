<div align="center">
  <img src="https://raw.githubusercontent.com/qor0530/NSDP_Program/main/resources/icon.png" alt="Logo" width="120" height="120">
  <h1 align="center">Not Solve, Don't Play (NSDP)</h1>
  <p align="center">
    프로그래밍 문제를 풀어야만 지정된 앱을 사용할 수 있게 만드는 Windows 생산성 도구입니다.
    <br />
    <a href="https://github.com/qor0530/NSDP_Program/releases">최신 버전 다운로드</a>
    ·
    <a href="https://github.com/qor0530/NSDP_Program/issues">버그 리포트</a>
    ·
    <a href="https://github.com/qor0530/NSDP_Program/issues">기능 제안</a>
  </p>
</div>

---

### 🎯 프로젝트 소개

**Not Solve, Don't Play (NSDP)** 는 게임이나 SNS 등 방해되는 프로그램의 실행을 차단하고, 대신 코딩 문제를 제시하여 사용자의 생산성과 학습을 동시에 돕는 애플리케이션입니다.

![NSDP 잠금 화면 스크린샷](https://raw.githubusercontent.com/qor0530/NSDP_Program/main/screenshot.png)

### ✨ 주요 기능

* **자동 잠금**: 사용자가 설정한 프로그램(예: `League of Legends.exe`) 실행 시, 전체 화면의 문제 풀이 창이 나타나며 다른 작업을 막습니다.
* **지능형 문제 추천**: 사용자의 풀이 기록을 바탕으로 실력에 맞는 난이도의 문제를 자동으로 추천합니다.
* **자체 채점 엔진**: 시간/메모리 제한을 포함한 로컬 코드 채점 기능으로 제출된 코드를 즉시 평가합니다.
* **포인트 시스템**: 문제 풀이를 통해 포인트를 얻어, 어려운 문제를 건너뛰거나(새로고침) 포기하는 데 사용할 수 있습니다.
* **편리한 설정**: 시스템 트레이 아이콘을 통해 GUI로 잠금 앱, 문제 수 등 모든 옵션을 쉽게 설정할 수 있습니다.
* **문제 추가 도우미**: `gemini_parser.py`를 이용해 웹사이트의 문제 텍스트를 복사하면 JSON 형식으로 자동 변환하여 쉽게 문제 은행에 추가할 수 있습니다.

---

### 💻 다운로드 및 실행 (for Users)

코드를 직접 설치할 필요 없이, 아래 방법으로 프로그램을 바로 사용할 수 있습니다.

1.  **[Releases 페이지](https://github.com/qor0530/NSDP_Program/releases)** 로 이동합니다.
2.  가장 최신 버전(Latest)의 'Assets' 항목에서 **`NotSolveDontPlay.exe`** 파일을 다운로드합니다.
3.  다운로드한 `.exe` 파일을 더블클릭하여 실행합니다.
    * **경고**: Windows SmartScreen 경고가 나타날 수 있습니다. 이는 서명되지 않은 실행 파일에 대한 일반적인 경고입니다. **'추가 정보' -> '실행'** 을 눌러 프로그램을 시작할 수 있습니다.

---

### 🛠️ 사용 기술

* **Python 3.10**
* **GUI**: CustomTkinter
* **시스템 제어**: Pystray, Psutil, PyWin32, Winshell
* **기타**: Pillow, Google Generative AI

---

### 👨‍💻 빌드 및 개발 (for Developers)

로컬 환경에서 직접 소스 코드를 빌드하고 개발에 참여하려면 아래 과정을 따르세요.

#### **사전 준비**

* Python 3.10 이상
* Git

#### **설치**

1.  **리포지토리 복제**
    ```sh
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
    cd YOUR_REPOSITORY
    ```
2.  **가상 환경 생성 및 활성화**
    ```sh
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
3.  **필요 라이브러리 설치**
    ```sh
    pip install -r requirements.txt
    ```

---

### 📖 사용법

1.  **프로그램 실행**
    ```sh
    python src/main.py
    ```
2.  **설정**: 화면 우측 하단 트레이 아이콘을 우클릭하여 '설정 열기'를 선택하고, 잠글 프로그램과 문제 수를 지정합니다.
3.  **잠금**: 설정된 프로그램을 실행하면 잠금 화면이 나타납니다.
4.  **해제**: 목표한 문제 수를 모두 해결하면 잠금이 해제됩니다.

---

### 🗺️ 로드맵

-   [ ] 문제 추가
-   [ ] 설정 창에 프로그램 아이콘 표시
-   [ ] 자잘한 오류 해결
-   [ ] `PyInstaller`를 이용한 공식 설치 프로그램(`.msi`) 제작
-   [ ] 사용자 통계 대시보드 기능 추가

---

### 📄 라이선스

MIT 라이선스에 따라 배포됩니다.
