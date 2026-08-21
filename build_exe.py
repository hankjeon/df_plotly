import PyInstaller.__main__
import os
import shutil

# 이전 빌드 잔여물 정리
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

PyInstaller.__main__.run([
    'desktop_app.py',       # 진입점 스크립트
    '--name=df_plotly',     # 생성될 exe 파일 이름
    '--noconsole',          # 터미널 창 숨기기 (GUI 앱)
    '--onefile',            # 단일 파일로 묶기
    '--add-data=app.py;.',  # app.py를 패키지에 포함
    '--copy-metadata=streamlit', # Streamlit 메타데이터 에러 해결
    '--collect-data=streamlit',  # Streamlit 정적 파일(웹 UI) 포함
    '--hidden-import=streamlit.runtime.scriptrunner.magic_funcs', # 누락된 내부 모듈 강제 포함
    '--clean',              # 빌드 전 정리
])
