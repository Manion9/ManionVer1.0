# 🎬 Manimator Desktop App

브라우저 없이 사용할 수 있는 독립적인 데스크톱 애플리케이션입니다.

## ✨ 특징

- 🖥️ **독립 실행**: 브라우저 없이 데스크톱에서 바로 실행
- 📤 **공유 가능**: .exe 파일로 다른 컴퓨터에 쉽게 배포
- ✏️ **편집 기능**: 각 단계에서 내용 수정 가능
- 🎯 **직관적 UI**: 사용하기 쉬운 그래픽 인터페이스

## 🚀 실행 방법

### 방법 1: Python으로 직접 실행

```bash
# 의존성 설치 (한 번만)
pip install tkinter  # 보통 Python에 기본 포함

# 앱 실행
python desktop_manimator.py
```

### 방법 2: 실행 파일(.exe) 빌드

```bash
# 빌드 도구 실행
python build_desktop_app.py

# 옵션 1 선택 (패키지 설치 + 빌드)
# 완료 후 dist/ManimatorDesktop.exe 파일 생성
```

## 📁 파일 구조

```
프로젝트/
├── desktop_manimator.py      # 메인 데스크톱 앱
├── build_desktop_app.py      # 빌드 스크립트
├── README_Desktop.md         # 이 파일
├── inputs/                   # 테스트용 입력 파일들
│   ├── handwriting.png
│   ├── test_equation.png
│   └── *.pdf
└── dist/                     # 빌드 결과물
    └── ManimatorDesktop.exe  # 최종 실행 파일
```

## 🎯 사용법

### 1. 앱 실행
- Python: `python desktop_manimator.py`
- 실행파일: `ManimatorDesktop.exe` 더블클릭

### 2. 입력 방식 선택
- ✍️ **손글씨**: 이미지/PDF 파일 업로드
- 📄 **PDF**: PDF 문서 업로드  
- 📝 **텍스트**: 직접 텍스트 입력

### 3. 편집 모드 설정
- ☑️ **체크**: 각 단계에서 편집 가능
- ☐ **해제**: 자동으로 생성

### 4. 생성 과정
#### 자동 모드:
```
입력 → 인식 → 스토리보드 → 코드 → 비디오
```

#### 편집 모드:
```
입력 → [편집1] → 스토리보드 → [편집2] → 코드 → [편집3] → 비디오
```

## 🔧 편집 기능

### 1단계: 인식 결과 편집
- GPT Vision으로 인식된 원시 텍스트
- 수식, 텍스트, 구조 수정 가능

### 2단계: 스토리보드 편집
- 애니메이션 시나리오 수정
- 핵심 포인트, 시각 요소 조정

### 3단계: Manim 코드 편집
- 최종 Python 코드 수정
- 애니메이션 세부 사항 조정

## 📤 배포 방법

### 실행 파일 배포
1. `python build_desktop_app.py` 실행
2. `dist/ManimatorDesktop.exe` 파일 생성
3. 이 파일을 다른 컴퓨터에 복사
4. 더블클릭으로 바로 실행

### 주의사항
- Windows Defender가 차단할 수 있음 (예외 설정)
- 첫 실행 시 약간의 로딩 시간 필요
- 인터넷 연결 필요 (API 호출)

## 🛠️ 개발자 정보

### 사용된 기술
- **GUI**: Tkinter (Python 표준 라이브러리)
- **빌드**: PyInstaller
- **플랫폼**: Windows, macOS, Linux

### 확장 가능성
- 다른 GUI 프레임워크로 업그레이드 (PyQt, wxPython)
- 더 많은 파일 형식 지원
- 실시간 미리보기 기능
- 애니메이션 설정 커스터마이징

## 🐛 문제 해결

### 빌드 오류
```bash
# PyInstaller 재설치
pip uninstall pyinstaller
pip install pyinstaller

# 권한 문제 시
python build_desktop_app.py  # 관리자 권한으로 실행
```

### 실행 오류
- 바이러스 백신 예외 설정
- 방화벽 허용 설정
- Python 재설치

## 💡 팁

1. **빠른 테스트**: `inputs/` 폴더의 샘플 이미지 사용
2. **편집 활용**: 복잡한 수식은 편집 모드로 정확도 높이기
3. **배포**: .exe 파일과 함께 사용법 메모 첨부
