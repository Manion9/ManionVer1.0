#!/usr/bin/env python3
"""편집 기능 UI 테스트용 간단한 Gradio 앱"""

import gradio as gr
import re
from typing import Tuple, Optional, Dict
import time

# 임시 모킹 함수들 (실제 API 호출 대신 더미 데이터 반환)
def mock_handwriting_recognition(file_bytes: bytes) -> str:
    """GPT Vision 원시 인식 모킹"""
    time.sleep(1)  # API 호출 시뮬레이션
    return """손글씨 인식 결과:

제목: 이차방정식의 해법

내용:
- 이차방정식: ax² + bx + c = 0 (a ≠ 0)
- 근의 공식: x = (-b ± √(b²-4ac)) / 2a
- 판별식: D = b² - 4ac
  * D > 0: 서로 다른 두 실근
  * D = 0: 중근 (하나의 실근)
  * D < 0: 허근

예제: x² - 5x + 6 = 0
해: x = (5 ± √(25-24))/2 = (5 ± 1)/2
따라서 x = 3 또는 x = 2"""

def mock_process_prompt_scene(prompt: str) -> str:
    """스토리보드 생성 모킹"""
    time.sleep(1)  # API 호출 시뮬레이션
    return f"""
**Topic**: {prompt}

**Key Points**:
* 핵심 개념 1: 기본 원리 설명
* 핵심 개념 2: 수학적 공식 (예: y = mx + b)  
* 핵심 개념 3: 실제 응용 사례
* 핵심 개념 4: 시각적 표현 방법

**Visual Elements**:
* 단계별 애니메이션으로 개념 전개
* 수식과 그래프를 동적으로 표시
* 색상과 움직임으로 핵심 포인트 강조

**Style**: 3Blue1Brown 스타일, 깔끔한 수학적 표현
"""

def mock_generate_animation_response(scene_description: str) -> str:
    """Manim 코드 생성 모킹"""
    time.sleep(2)  # API 호출 시뮬레이션
    return f"""
```python
from manim import *

class TestAnimation(Scene):
    def construct(self):
        # 제목 생성
        title = Text("편집 기능 테스트", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        
        # 사용자 편집 내용을 반영한 애니메이션
        # Scene Description: {scene_description[:100]}...
        
        # 메인 컨텐츠
        main_text = Text("편집된 내용이 여기에 표시됩니다", font_size=36)
        self.play(Write(main_text))
        self.wait(3)
        
        # 정리
        self.play(FadeOut(main_text))
```
"""

def mock_render_video(code: str) -> str:
    """비디오 렌더링 모킹"""
    time.sleep(1)  # 렌더링 시뮬레이션
    return "test_video.mp4"  # 실제로는 렌더링된 비디오 경로 반환

def mock_extract_code(response: str) -> str:
    """코드 추출 모킹"""
    # ```python ... ``` 블록에서 코드 추출
    code_match = re.search(r'```python(.*?)```', response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    return response

# 편집 가능한 파이프라인 함수들
def process_with_editing(prompt: str, edit_mode: bool, state: dict):
    """편집 모드가 적용된 통합 처리 함수"""
    try:
        # 1단계: 인식 (텍스트 입력은 그대로 사용)
        state["step1_input"] = prompt
        state["step1_output"] = prompt
        
        if edit_mode:
            # 편집 모드에서는 단계별로 진행하지 않고 state만 업데이트
            state["edit_mode"] = True
            state["current_step"] = 1
            return None, None, "편집 모드: 1단계 - 입력 내용 편집이 필요합니다"
        else:
            # 자동 모드로 전체 파이프라인 실행
            return process_prompt_auto(prompt)
            
    except Exception as e:
        return None, None, f"처리 중 오류: {str(e)}"

def process_prompt_auto(prompt: str):
    """자동 모드 - 모킹된 전체 파이프라인"""
    try:
        scene_description = mock_process_prompt_scene(prompt)
        response = mock_generate_animation_response(scene_description)
        code = mock_extract_code(response)
        video_path = mock_render_video(code)
        
        return video_path, code, "Animation generated successfully!"
    except Exception as e:
        return None, None, f"Error: {str(e)}"

# Gradio 앱 구성
description_md = """
## 🎬 manimator - 편집 기능 테스트

편집 기능이 추가된 Manimator의 UI 테스트 버전입니다:

- **편집 모드**: 체크박스를 선택하면 각 단계에서 편집할 수 있습니다
- **자동 모드**: 체크박스를 해제하면 자동으로 생성됩니다

### 테스트 기능
- ✅ 체크박스 UI
- ✅ 단계별 편집 모달
- ✅ 편집 내용 전달 및 처리
"""

with gr.Blocks(title="manimator - 편집 기능 테스트") as demo:
    gr.Markdown(description_md)
    
    # 공통 State 변수
    session_state = gr.State({})
    
    # 편집 모달
    with gr.Modal(visible=False) as edit_modal:
        edit_step_title = gr.Markdown("### 1단계: 편집 중...")
        edit_content = gr.Textbox(
            label="편집 내용", 
            lines=15, 
            max_lines=20,
            show_copy_button=True
        )
        with gr.Row():
            edit_save_btn = gr.Button("편집 완료 후 다음 단계로", variant="primary")
            edit_reset_btn = gr.Button("초기값으로 되돌리기")
            edit_close_btn = gr.Button("편집 취소")

    with gr.Tabs():
        with gr.TabItem("✍️ Text Prompt"):
            with gr.Column():
                text_input = gr.Textbox(
                    label="Describe the animation you want to create",
                    placeholder="Explain the working of neural networks",
                    lines=3,
                )
                # 편집 모드 체크박스 추가
                text_edit_mode = gr.Checkbox(
                    label="편집하고 싶다면 체크",
                    value=False,
                    info="체크 해제 시: 자동 생성됨 | 체크 시: 각 단계에서 편집 가능"
                )
                text_button = gr.Button("Generate Animation from Text")

            with gr.Row():
                video_output = gr.Video(label="Generated Animation")

            code_output = gr.Code(
                label="Generated Manim Code",
                language="python",
                interactive=False,
            )
            status_output = gr.Textbox(
                label="Status", interactive=False, show_copy_button=True
            )

        with gr.TabItem("✍️ Handwriting (테스트)"):
            with gr.Column():
                handwriting_input = gr.File(
                    label="Upload handwritten image or PDF", 
                    file_types=[".jpg", ".jpeg", ".png", ".pdf"]
                )
                # 편집 모드 체크박스 추가
                handwriting_edit_mode = gr.Checkbox(
                    label="편집하고 싶다면 체크",
                    value=False,
                    info="체크 해제 시: 자동 생성됨 | 체크 시: GPT Vision 인식 결과부터 편집 가능"
                )
                handwriting_button = gr.Button("Generate Animation from Handwriting")

            with gr.Row():
                handwriting_video_output = gr.Video(label="Generated Animation")

            handwriting_code_output = gr.Code(
                label="Generated Manim Code",
                language="python",
                interactive=False,
            )
            handwriting_status_output = gr.Textbox(
                label="Status", interactive=False, show_copy_button=True
            )

    # 모달 제어 및 편집 처리 함수들
    def handle_text_input(prompt, edit_mode, state):
        """텍스트 입력 처리"""
        if not prompt.strip():
            return (
                gr.Modal(visible=False),
                gr.Markdown("### 오류"),
                "",
                None, None, "텍스트를 입력해주세요"
            )
            
        if edit_mode:
            state["step1_output"] = prompt
            state["current_step"] = 1
            state["edit_mode"] = True
            return (
                gr.Modal(visible=True),  # 모달 열기
                gr.Markdown("### 1단계: 입력 텍스트 편집"),
                prompt,  # 편집 내용에 초기값 설정
                None, None, "편집 모드가 활성화되었습니다"
            )
        else:
            # 자동 모드 - 기존 로직 사용
            video, code, message = process_prompt_auto(prompt)
            return (
                gr.Modal(visible=False),  # 모달 닫기
                gr.Markdown("### 자동 생성 완료"),
                "",  # 편집 내용 초기화
                video, code, message
            )

    def handle_edit_save(edited_content, state):
        """편집 저장 및 다음 단계 진행"""
        try:
            current_step = state.get("current_step", 1)
            
            if current_step == 1:
                # 1단계 → 2단계: 스토리보드 생성
                state["step1_output"] = edited_content
                scene_description = mock_process_prompt_scene(edited_content)
                state["step2_output"] = scene_description
                state["current_step"] = 2
                
                return (
                    gr.Modal(visible=True),  # 모달 유지
                    gr.Markdown("### 2단계: 스토리보드 편집"),
                    scene_description,  # 새 편집 내용
                    None, None, "2단계로 진행되었습니다"
                )
                
            elif current_step == 2:
                # 2단계 → 3단계: 코드 생성
                state["step2_output"] = edited_content
                response = mock_generate_animation_response(edited_content)
                code = mock_extract_code(response)
                state["step3_output"] = code
                state["current_step"] = 3
                
                return (
                    gr.Modal(visible=True),
                    gr.Markdown("### 3단계: Manim 코드 편집"),
                    code,
                    None, None, "3단계로 진행되었습니다"
                )
                
            elif current_step == 3:
                # 3단계 → 렌더링
                state["step3_output"] = edited_content
                
                # 간단한 코드 검증
                if "class" not in edited_content or "Scene" not in edited_content:
                    return (
                        gr.Modal(visible=True),
                        gr.Markdown("### 오류"),
                        edited_content,
                        None, None, "Scene 클래스를 찾을 수 없습니다"
                    )
                
                video_path = mock_render_video(edited_content)
                
                # 편집 완료
                state["edit_mode"] = False
                return (
                    gr.Modal(visible=False),  # 모달 닫기
                    gr.Markdown("### 편집 완료"),
                    "",
                    video_path, edited_content, "렌더링 완료!"
                )
            
        except Exception as e:
            return (
                gr.Modal(visible=True),
                gr.Markdown("### 오류"),
                edited_content,
                None, None, f"처리 오류: {str(e)}"
            )

    def handle_edit_reset(state):
        """편집 내용 초기값으로 되돌리기"""
        current_step = state.get("current_step", 1)
        
        if current_step == 1:
            original_content = state.get("step1_output", "")
            title = "### 1단계: 입력 내용 편집"
        elif current_step == 2:
            original_content = state.get("step2_output", "")
            title = "### 2단계: 스토리보드 편집"
        elif current_step == 3:
            original_content = state.get("step3_output", "")
            title = "### 3단계: Manim 코드 편집"
        else:
            original_content = ""
            title = "### 편집"
        
        return (
            gr.Modal(visible=True),
            gr.Markdown(title),
            original_content
        )

    def handle_edit_close():
        """편집 취소"""
        return (
            gr.Modal(visible=False),
            gr.Markdown("### 편집 취소됨"),
            ""
        )

    # 이벤트 바인딩
    text_button.click(
        fn=handle_text_input,
        inputs=[text_input, text_edit_mode, session_state],
        outputs=[edit_modal, edit_step_title, edit_content, video_output, code_output, status_output]
    )
    
    edit_save_btn.click(
        fn=handle_edit_save,
        inputs=[edit_content, session_state],
        outputs=[edit_modal, edit_step_title, edit_content, video_output, code_output, status_output]
    )
    
    edit_reset_btn.click(
        fn=handle_edit_reset,
        inputs=[session_state],
        outputs=[edit_modal, edit_step_title, edit_content]
    )
    
    edit_close_btn.click(
        fn=handle_edit_close,
        inputs=[],
        outputs=[edit_modal, edit_step_title, edit_content]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
