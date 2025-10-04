import tkinter as tk
from PIL import Image, ImageTk
import win32gui
import win32api
import win32con
import win32ui # 이 모듈을 올바르게 사용합니다.
import os

def extract_icon(exe_path, size=(32, 32)):
    """
    가장 안정적인 'DrawIcon' 방식으로 아이콘을 추출합니다.
    """
    try:
        # 1. 아이콘 핸들 추출
        large, small = win32gui.ExtractIconEx(exe_path, 0)
        h_icon = large[0] if large else (small[0] if small else 0)
        
        if not h_icon:
            for handle in large: win32api.DestroyIcon(handle)
            for handle in small: win32api.DestroyIcon(handle)
            return None

        # 2. 아이콘을 그릴 비트맵과 디바이스 컨텍스트(DC) 생성
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, size[0], size[1])
        mem_dc = hdc.CreateCompatibleDC()
        mem_dc.SelectObject(hbmp)

        # 3. 생성된 비트맵에 아이콘을 그림
        mem_dc.DrawIcon((0,0), h_icon)
        
        # 4. 그려진 비트맵의 데이터를 가져와 PIL Image로 변환
        bmp_str = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGBA',
            size,
            bmp_str, 'raw', 'BGRA', 0, 1
        )
        
        # 5. 사용한 모든 리소스 핸들 정리
        win32gui.DestroyIcon(h_icon)
        for handle in large: win32api.DestroyIcon(handle)
        for handle in small: win32api.DestroyIcon(handle)
        mem_dc.DeleteDC()
        hdc.DeleteDC()
        win32gui.DeleteObject(hbmp.GetHandle())

        return ImageTk.PhotoImage(img)

    except Exception as e:
        # print(f"--- 아이콘 추출 실패: {os.path.basename(exe_path)}, 원인: {e}")
        return None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("아이콘 표시 테스트")

    notepad_path = r"C:\Windows\System32\notepad.exe"
    print(f"'{notepad_path}'에서 아이콘을 추출합니다...")
    
    icon = extract_icon(notepad_path)

    if icon:
        print("아이콘 추출 성공! 창에 표시합니다.")
        label = tk.Label(root, image=icon, text="메모장 아이콘", compound="left", font=("Arial", 14))
        label.image = icon 
        label.pack(padx=20, pady=20)
    else:
        print("테스트 실패: 아이콘 추출 함수가 이미지를 반환하지 않았습니다.")
        label = tk.Label(root, text="아이콘 표시에 실패했습니다.", font=("Arial", 14))
        label.pack(padx=20, pady=20)

    root.mainloop()