# 📁 Manimator 프로젝트 구조

## 🎯 개요
이 문서는 정리된 Manimator 프로젝트의 폴더 구조와 각 구성요소를 설명합니다.

## 📂 폴더 구조

```
manimator/
├── 📦 CORE PROJECT FILES (필수)
│   ├── manimator/                    # 원본 manimator 모듈
│   ├── assets/                       # 원본 자원 파일들
│   ├── pyproject.toml               # Python 프로젝트 설정
│   ├── poetry.lock                  # Poetry 잠금 파일
│   └── .gitignore                   # Git 무시 파일
│
├── ⚙️  CONFIGURATION
│   └── config/                      # 모든 설정 파일들
│       ├── .env                            # 환경변수 (API 키들)
│       ├── requirements.txt                # 의존성 목록
│       ├── packages.txt                    # 시스템 패키지 목록
│       ├── Dockerfile                      # Docker 설정
│       └── LICENSE                         # 라이선스
│
├── 📚 DOCUMENTATION
│   └── docs/                        # 모든 문서들
│       ├── PROJECT_STRUCTURE.md            # 프로젝트 구조 가이드 (이 파일)
│       └── README.md                       # 원본 README
│
├── 🧪 DEVELOPMENT & TESTING
│   ├── tests/                       # 테스트 파일들
│   │   ├── vision_vs_ocr_test.py           # Vision vs OCR 비교 테스트
│   │   ├── pdf_pipeline_test.py            # PDF 파이프라인 테스트
│   │   ├── full_pipeline_test.py           # 전체 파이프라인 테스트
│   │   ├── quick_test.py                   # 빠른 OCR 테스트
│   │   └── [기타 테스트들]
│   │
│   ├── inputs/                      # 테스트 입력 파일들
│   │   ├── handwriting.png                 # 손글씨 이미지 (인수분해)
│   │   ├── fector.pdf                      # PDF 테스트 파일
│   │   └── test_equation.png               # 테스트 수식 이미지
│   │
│   └── outputs/                     # 생성된 결과물들
│       ├── handwriting_animation_*.mp4     # 손글씨 → 애니메이션
│       ├── pdf_animation_*.mp4             # PDF → 애니메이션
│       ├── generated_animation.py          # 생성된 Manim 코드
│       └── pdf_generated_animation.py      # PDF 기반 Manim 코드
│
├── 🔬 FOR FUTURE USE
│   ├── experiments/                 # 실험적 기능들 (비어있음)
│   └── deprecated/                  # 더 이상 사용안하는 것들 (비어있음)
│
└── .history/                        # 개발 히스토리
```

## 🚀 주요 기능

### ✅ **구현된 기능들**
1. **📝 손글씨 인식**: PNG/JPG 이미지에서 수학 수식 인식
2. **📄 PDF 처리**: PDF 문서를 이미지로 변환 후 분석
3. **🎬 애니메이션 생성**: 인식된 내용을 Manim 애니메이션으로 변환
4. **🔍 Vision vs OCR**: GPT-4o Vision과 기존 OCR 방식 비교

### 🔧 **기술 스택**
- **OCR**: Mathpix, Google Vision API
- **Vision Model**: GPT-4o (OpenAI)
- **LLM**: GPT-4 (OpenAI)
- **Animation**: Manim
- **UI**: Gradio

## 📋 사용 방법

### **설치 및 설정**
```bash
# 의존성 설치
pip install -r config/requirements.txt

# 또는 Poetry 사용
poetry install
```

### **테스트 실행**
```bash
# 프로젝트 루트에서 실행
cd tests/

# 빠른 OCR 테스트
python quick_test.py

# Vision vs OCR 비교
python vision_vs_ocr_test.py

# PDF 파이프라인 테스트
python pdf_pipeline_test.py

# 전체 파이프라인 테스트
python full_pipeline_test.py
```

### **API 키 설정**
`config/.env` 파일의 API 키들을 실제 값으로 교체하세요:

#### **필수 API 키들:**
```bash
# 1. Mathpix OCR (수학 수식 전용) - https://mathpix.com/
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key

# 2. Google Vision API (텍스트 인식) - https://cloud.google.com/vision
GOOGLE_VISION_API_KEY=your_google_vision_api_key

# 3. OpenAI API (GPT-4, GPT-4V) - https://platform.openai.com/
OPENAI_API_KEY=your_openai_api_key
```

#### **현재 설정된 모델들:**
```bash
PROMPT_SCENE_GEN_MODEL=gpt-4         # 텍스트 Scene Description
PDF_SCENE_GEN_MODEL=gpt-4o           # PDF Vision 분석 (추천)
CODE_GEN_MODEL=gpt-4                 # Manim 코드 생성
```

#### **선택적 설정들:**
```bash
DEFAULT_OCR_TYPE=vision              # 추천: GPT-4o Vision 직접 사용
GRADIO_SERVER_PORT=7860              # Gradio 웹 인터페이스 포트
DEBUG=false                          # 디버그 모드
```

## 📊 입력/출력 형식

### **지원하는 입력**
- **이미지**: JPG, PNG (손글씨 수식)
- **PDF**: 학술 논문, 수학 문서

### **생성되는 출력**
- **MP4 애니메이션**: Manim으로 렌더링된 수학 애니메이션
- **Python 코드**: 재사용 가능한 Manim 스크립트

## 🔄 파이프라인 플로우

### **손글씨 → 애니메이션**
```
PNG/JPG 이미지 → GPT-4o Vision → Scene Description → GPT-4 → Manim 코드 → 애니메이션
```

### **PDF → 애니메이션**
```
PDF → pdf2image → JPEG → GPT-4o Vision → Scene Description → GPT-4 → Manim 코드 → 애니메이션
```

## 📈 성능 비교

| 방식 | 정확도 | 속도 | 수학 이해도 |
|------|--------|------|-------------|
| **GPT-4o Vision** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **OCR (Mathpix)** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **OCR (Google)** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 🎯 권장사항

1. **손글씨 인식**: `ocr_type="vision"` 사용 (기본값)
2. **PDF 처리**: 자동으로 최적화된 파이프라인 사용
3. **API 키**: 모든 서비스 키 설정으로 최상의 결과 보장

---

**🎉 완성된 기능**: 손글씨 수식 → 고품질 수학 애니메이션 자동 생성!