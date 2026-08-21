import os
import sys
import subprocess
import time
import socket
import webview

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_streamlit():
    # PyInstaller 패키징된 경우와 로컬 파이썬인 경우를 구분하여 실행
    if getattr(sys, 'frozen', False):
        cmd = [sys.executable, "run_streamlit"]
    else:
        cmd = [sys.executable, sys.argv[0], "run_streamlit"]
    
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    return subprocess.Popen(cmd, startupinfo=startupinfo)

if __name__ == '__main__':
    # "run_streamlit" 인자가 전달되면, UI를 띄우지 않고 Streamlit 서버만 실행합니다.
    # (PyInstaller로 묶었을 때 자기 자신(.exe)을 다시 호출하여 백그라운드 서버로 쓰기 위함)
    if len(sys.argv) > 1 and sys.argv[1] == "run_streamlit":
        from streamlit.web import cli as stcli
        
        # 파일 경로 설정 (exe 내부 임시 폴더인지 로컬 폴더인지 확인)
        if getattr(sys, 'frozen', False):
            app_path = os.path.join(sys._MEIPASS, 'app.py')
        else:
            app_path = os.path.abspath('app.py')
            
        sys.argv = [
            "streamlit", "run", app_path, 
            "--server.headless", "true", 
            "--server.port", "8501", 
            "--global.developmentMode", "false"
        ]
        sys.exit(stcli.main())

    # --- 메인 UI 로직 ---
    port = 8501
    
    print("Streamlit 서버를 시작합니다...")
    process = run_streamlit()
    
    # 포트가 열릴 때까지(서버가 켜질 때까지) 최대 30초 대기
    retries = 0
    while not is_port_in_use(port) and retries < 30:
        time.sleep(1)
        retries += 1
        
    if retries == 30:
        print("Streamlit 서버 실행에 실패했습니다. (Timeout)")
        process.terminate()
        sys.exit(1)
        
    print("앱 창을 엽니다...")
    
    # 웹뷰 창 띄우기
    window = webview.create_window('데이터 대시보드', f'http://localhost:{port}', width=1024, height=768)
    
    # 창 루프 시작 (여기서 멈춰있다가 창이 닫히면 다음 줄로 넘어감)
    webview.start()
    
    # 창이 닫히면 파이썬 백그라운드 서버도 강제 종료
    process.terminate()
    print("프로그램이 완전히 종료되었습니다.")
