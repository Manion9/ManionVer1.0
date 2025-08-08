#!/usr/bin/env python3
"""
Desktop App 빌드 스크립트
PyInstaller를 사용해서 .exe 파일로 빌드
"""

import os
import sys
import subprocess

def install_requirements():
    """필수 패키지 설치"""
    print("📦 필수 패키지 설치 중...")
    
    packages = [
        "pyinstaller",
        "tkinter",  # 보통 Python에 포함되어 있음
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} 설치 완료")
        except subprocess.CalledProcessError:
            print(f"❌ {package} 설치 실패")

def build_exe():
    """실행 파일 빌드"""
    print("\n🔨 실행 파일 빌드 중...")
    
    # PyInstaller 명령어
    cmd = [
        "pyinstaller",
        "--onefile",              # 단일 실행 파일
        "--windowed",             # 콘솔 창 숨김 (GUI 앱)
        "--name=ManimatorDesktop", # 실행 파일 이름
        "--icon=app_icon.ico",    # 아이콘 (있다면)
        "--add-data=inputs;inputs", # inputs 폴더 포함
        "desktop_manimator.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ 빌드 완료!")
        print("📁 생성된 파일: dist/ManimatorDesktop.exe")
        print("\n🚀 배포 방법:")
        print("1. dist/ManimatorDesktop.exe 파일을 다른 컴퓨터에 복사")
        print("2. 더블클릭으로 실행")
        print("3. 별도 설치 없이 바로 사용 가능!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
        print("\n🔧 문제 해결:")
        print("1. pyinstaller 설치: pip install pyinstaller")
        print("2. 경로에 한글이 있으면 영문 경로로 이동")
        print("3. 바이러스 백신 예외 설정")

def create_icon():
    """간단한 아이콘 파일 생성"""
    icon_content = """
# app_icon.ico 파일이 없어도 빌드는 가능합니다.
# 원한다면 32x32 또는 64x64 .ico 파일을 만들어서 
# 같은 폴더에 "app_icon.ico" 이름으로 저장하세요.
"""
    
    if not os.path.exists("app_icon.ico"):
        print("💡 아이콘 파일이 없습니다. (선택사항)")
        print("   원한다면 app_icon.ico 파일을 추가하세요.")

def main():
    print("🎬 Manimator Desktop App 빌드 도구")
    print("=" * 50)
    
    # 현재 디렉토리 확인
    if not os.path.exists("desktop_manimator.py"):
        print("❌ desktop_manimator.py 파일이 없습니다.")
        print("   올바른 폴더에서 실행하세요.")
        return
    
    # 옵션 선택
    print("\n빌드 옵션:")
    print("1. 패키지 설치 + 빌드")
    print("2. 빌드만 실행")
    print("3. 패키지 설치만")
    
    choice = input("\n선택하세요 (1-3): ").strip()
    
    if choice in ["1", "3"]:
        install_requirements()
    
    if choice in ["1", "2"]:
        create_icon()
        build_exe()
    
    print("\n✨ 완료!")

if __name__ == "__main__":
    main()
