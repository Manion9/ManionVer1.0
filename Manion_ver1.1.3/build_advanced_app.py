#!/usr/bin/env python3
"""
Advanced Desktop App 빌드 스크립트
Make.com 스타일 워크플로우 GUI 앱 빌드
"""

import os
import sys
import subprocess

def build_advanced_exe():
    """고급 워크플로우 앱 빌드"""
    print("🔨 Advanced Manimator Desktop App 빌드 중...")
    
    # PyInstaller 명령어 (고급 버전)
    cmd = [
        "pyinstaller",
        "--onefile",                    # 단일 실행 파일
        "--windowed",                   # 콘솔 창 숨김
        "--name=ManimatorAdvanced",     # 실행 파일 이름
        "--add-data=inputs;inputs",     # inputs 폴더 포함
        "--hidden-import=tkinter",      # tkinter 명시적 포함
        "--hidden-import=threading",    # threading 모듈 포함
        "advanced_desktop_manimator.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ 고급 버전 빌드 완료!")
        print("📁 생성된 파일: dist/ManimatorAdvanced.exe")
        print("\n🚀 새로운 기능:")
        print("- Make.com 스타일 노드 기반 워크플로우")
        print("- 개별 편집 체크박스 (인식/스토리보드/코드)")
        print("- 실시간 워크플로우 상태 표시")
        print("- 노드 클릭으로 직접 편집")
        print("- 하드코딩 제거, 실제 입력 기반 처리")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")

def main():
    print("🎬 Manimator Advanced Desktop App 빌드 도구")
    print("=" * 60)
    
    if not os.path.exists("advanced_desktop_manimator.py"):
        print("❌ advanced_desktop_manimator.py 파일이 없습니다.")
        return
    
    print("\n🆕 Advanced 버전 특징:")
    print("1. Make.com 스타일 시각적 워크플로우")
    print("2. 개별 편집 체크박스 (3개 독립 옵션)")
    print("3. 노드 기반 인터랙션")
    print("4. 실제 입력 기반 동적 처리")
    print("5. 단계별 상태 시각화")
    
    choice = input("\n빌드를 시작하시겠습니까? (y/n): ").strip().lower()
    
    if choice == 'y':
        # 의존성 설치
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        except:
            print("⚠️ PyInstaller 설치 실패 (이미 설치되어 있을 수 있음)")
        
        build_advanced_exe()
        
        print("\n✨ 사용법:")
        print("1. dist/ManimatorAdvanced.exe 실행")
        print("2. 상단 편집 옵션에서 원하는 편집 단계 선택")
        print("3. 입력 방식 선택 후 파일/텍스트 입력")
        print("4. 워크플로우 시작 클릭")
        print("5. 노드별로 진행 상황 확인")
        print("6. 편집 필요 시 노드 클릭 또는 편집 패널 사용")
    else:
        print("빌드가 취소되었습니다.")

if __name__ == "__main__":
    main()
