import gradio as gr
import re
from importlib import resources
from typing import Tuple, Optional, Dict
import functools

from manimator.api.animation_generation import generate_animation_response
from manimator.api.scene_description import process_prompt_scene, process_pdf_prompt, process_handwriting_prompt
from manimator.utils.schema import ManimProcessor


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
    """자동 모드 - 기존 로직 유지"""
    max_attempts = 2
    attempts = 0

    while attempts < max_attempts:
        try:
            processor = ManimProcessor()
            with processor.create_temp_dir() as temp_dir:
                scene_description = process_prompt_scene(prompt)
                response = generate_animation_response(scene_description)
                code = processor.extract_code(response)

                if not code:
                    attempts += 1
                    if attempts < max_attempts:
                        continue
                    return (
                        None,
                        None,
                        "No valid Manim code generated after multiple attempts",
                    )

                class_match = re.search(r"class (\w+)\(Scene\)", code)
                if not class_match:
                    attempts += 1
                    if attempts < max_attempts:
                        continue
                    return None, None, "No Scene class found after multiple attempts"

                scene_name = class_match.group(1)
                scene_file = processor.save_code(code, temp_dir)
                video_path = processor.render_scene(scene_file, scene_name, temp_dir)

                if not video_path:
                    return None, None, "Failed to render animation"

                return video_path, code, "Animation generated successfully!"

        except Exception as e:
            attempts += 1
            if attempts < max_attempts:
                continue
            return None, None, f"Error after multiple attempts: {str(e)}"

def process_prompt(prompt: str):
    """기존 호환성을 위한 래퍼 함수"""
    return process_prompt_auto(prompt)


# 편집 가능한 PDF 처리 함수
def process_pdf_with_editing(file_path: str, edit_mode: bool, state: dict):
    """편집 모드가 적용된 PDF 처리 함수"""
    try:
        if not file_path:
            return None, None, "Error: No file uploaded"
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            scene_description = process_pdf_prompt(file_bytes)
            
        state["step1_input"] = file_path
        state["step1_output"] = scene_description
        
        if edit_mode:
            state["edit_mode"] = True
            state["current_step"] = 1
            return None, None, "편집 모드: 1단계 - PDF 인식 결과 편집이 필요합니다"
        else:
            # 자동 모드로 계속 진행
            return process_prompt_auto(scene_description)
            
    except Exception as e:
        return None, None, f"PDF 처리 중 오류: {str(e)}"

# GPT Vision 원시 인식 함수 (scene_description 생성 전 단계)
def process_handwriting_recognition_only(file_bytes: bytes) -> str:
    """손글씨 파일을 GPT Vision으로 인식만 하고 텍스트 추출"""
    try:
        # 파일 타입 감지 및 JPEG 변환
        if file_bytes.startswith(b'%PDF'):
            from manimator.utils.ocr_helpers import pdf_to_images
            image_list = pdf_to_images(file_bytes)
            if image_list:
                image_base64 = base64.b64encode(image_list[0]).decode('utf-8')
                mime_type = "image/jpeg"
            else:
                raise Exception("Could not convert PDF to image")
        elif file_bytes.startswith(b'\xff\xd8\xff'):
            image_base64 = base64.b64encode(file_bytes).decode('utf-8')
            mime_type = "image/jpeg"
        elif file_bytes.startswith(b'\x89PNG'):
            image_base64 = base64.b64encode(file_bytes).decode('utf-8')
            mime_type = "image/png"
        else:
            image_base64 = base64.b64encode(file_bytes).decode('utf-8')
            mime_type = "image/jpeg"
        
        # GPT Vision으로 원시 텍스트 추출 (scene_description 생성 전)
        messages = [
            {
                "role": "system", 
                "content": "You are an expert at reading handwritten mathematical content. Extract all text, formulas, and diagrams from the image. Provide a clean, accurate transcription of what you see."
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "Please transcribe all the handwritten mathematical content from this image. Include formulas, text, and describe any diagrams. Be precise and maintain the original structure."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:{mime_type};base64,{image_base64}",
                    }
                ],
            },
        ]
        
        import litellm
        import os
        response = litellm.completion(
            model=os.getenv("PDF_SCENE_GEN_MODEL", "gpt-4o"),
            messages=messages,
            num_retries=2,
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Vision recognition failed: {str(e)}")

# 편집 가능한 손글씨 처리 함수
def process_handwriting_with_editing(file_path: str, edit_mode: bool, state: dict):
    """편집 모드가 적용된 손글씨 처리 함수"""
    try:
        if not file_path:
            return None, None, "Error: No file uploaded"
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        state["step1_input"] = file_path
        
        if edit_mode:
            # 편집 모드: GPT Vision 원시 인식 결과만 추출
            recognized_text = process_handwriting_recognition_only(file_bytes)
            state["step1_output"] = recognized_text
            state["edit_mode"] = True
            state["current_step"] = 1
            return None, None, "편집 모드: 1단계 - 손글씨 인식 결과 편집이 필요합니다"
        else:
            # 자동 모드: 기존 파이프라인 그대로
            scene_description = process_handwriting_prompt(file_bytes)
            return process_prompt_auto(scene_description)
            
    except Exception as e:
        return None, None, f"손글씨 처리 중 오류: {str(e)}"

def process_pdf(file_path: str):
    """기존 호환성을 위한 PDF 처리 함수"""
    print("file_path", file_path)
    try:
        if not file_path:
            return "Error: No file uploaded"
        with open(file_path, "rb") as file_path:
            file_bytes = file_path.read()
            scene_description = process_pdf_prompt(file_bytes)
            print("scene_description", scene_description)
        return scene_description
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


def process_handwriting(file_path: str):
    """기존 호환성을 위한 손글씨 처리 함수"""
    print("handwriting file_path", file_path)
    try:
        if not file_path:
            return "Error: No file uploaded"
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            scene_description = process_handwriting_prompt(file_bytes)
            print("handwriting scene_description", scene_description)
        return scene_description
    except Exception as e:
        return f"Error processing handwritten file: {str(e)}"


# 편집 모드 지원 통합 함수
def interface_fn_with_editing(prompt=None, pdf_file=None, handwriting_file=None, edit_mode=False, state=None):
    """편집 모드를 지원하는 통합 인터페이스 함수"""
    if state is None:
        state = {}
    
    if prompt:
        return process_with_editing(prompt, edit_mode, state)
    elif pdf_file:
        return process_pdf_with_editing(pdf_file, edit_mode, state)
    elif handwriting_file:
        return process_handwriting_with_editing(handwriting_file, edit_mode, state)
    else:
        return [None, None, "Please provide either a prompt, upload a PDF file, or upload a handwritten image"]

# 편집 단계 처리 함수들
def process_step1_edit(edited_content: str, state: dict):
    """1단계: 인식 결과 편집 완료 후 다음 단계로"""
    try:
        state["step1_output"] = edited_content
        state["current_step"] = 2
        
        # 스토리보드 생성
        scene_description = process_prompt_scene(edited_content)
        state["step2_output"] = scene_description
        
        return True, scene_description, "2단계: 스토리보드 편집"
    except Exception as e:
        return False, str(e), "오류가 발생했습니다"

def process_step2_edit(edited_content: str, state: dict):
    """2단계: 스토리보드 편집 완료 후 다음 단계로"""
    try:
        state["step2_output"] = edited_content
        state["current_step"] = 3
        
        # Manim 코드 생성
        response = generate_animation_response(edited_content)
        processor = ManimProcessor()
        code = processor.extract_code(response)
        state["step3_output"] = code
        
        return True, code, "3단계: Manim 코드 편집"
    except Exception as e:
        return False, str(e), "오류가 발생했습니다"

def process_step3_edit(edited_content: str, state: dict):
    """3단계: Manim 코드 편집 완료 후 렌더링"""
    try:
        state["step3_output"] = edited_content
        
        # 코드 렌더링
        processor = ManimProcessor()
        with processor.create_temp_dir() as temp_dir:
            class_match = re.search(r"class (\w+)\(Scene\)", edited_content)
            if not class_match:
                return False, None, "Scene 클래스를 찾을 수 없습니다"
            
            scene_name = class_match.group(1)
            scene_file = processor.save_code(edited_content, temp_dir)
            video_path = processor.render_scene(scene_file, scene_name, temp_dir)
            
            if not video_path:
                return False, None, "렌더링에 실패했습니다"
            
            return True, video_path, "렌더링 완료!"
    except Exception as e:
        return False, None, f"렌더링 오류: {str(e)}"

def interface_fn(prompt=None, pdf_file=None, handwriting_file=None):
    """기존 호환성을 위한 래퍼 함수"""
    if prompt:
        video_path, code, message = process_prompt(prompt)
        if video_path:
            return [video_path, code, message]
        return [None, None, message]
    elif pdf_file:
        scene_description = process_pdf(pdf_file)
        if scene_description:
            video_path, code, message = process_prompt(scene_description)
            if video_path:
                return [video_path, code, message]
            return [None, None, message]
    elif handwriting_file:
        scene_description = process_handwriting(handwriting_file)
        if scene_description and not scene_description.startswith("Error"):
            video_path, code, message = process_prompt(scene_description)
            if video_path:
                return [video_path, code, message]
            return [None, None, message]
        else:
            return [None, None, scene_description]
    return [None, None, "Please provide either a prompt, upload a PDF file, or upload a handwritten image"]


description_md = """
## 🎬 manimator

This tool helps you create visualizations of complex concepts using natural language, PDF papers, or handwritten content:

- **Text Prompt**: Describe the concept you want to visualize
- **PDF Upload**: Upload a research paper to extract key visualizations
- **Handwriting Recognition**: Upload handwritten notes, formulas, or diagrams

### Links
- [Manim Documentation](https://docs.manim.community/)
- [Project Repository](https://github.com/HyperCluster-Tech/manimator)
"""

# Constants for examples
EXAMPLE_VIDEOS: Dict[str, str] = {
    "What is a CNN?": "CNNExplanation.mp4",
    "BitNet Paper": "BitNet.mp4",
    "Explain Fourier Transform": "FourierTransformExplanation.mp4",
    "How does backpropagation work in Neural Networks?": "NeuralNetworksBackPropagationExample.mp4",
    "What is SVM?": "SVMExplanation.mp4",
}


@functools.lru_cache(maxsize=None)
def get_example_path(filename: str) -> Optional[str]:
    """Get absolute path to example file using importlib.resources."""
    try:
        with resources.path("manimator.examples", filename) as path:
            if path.exists():
                return str(path)
    except Exception as e:
        print(f"Error loading example {filename}: {e}")
    return None


def show_sample(example: str) -> Tuple[Optional[str], str]:
    """Display sample animation with proper path resolution."""
    if example not in EXAMPLE_VIDEOS:
        return None, "Invalid example selected"

    video_path = get_example_path(EXAMPLE_VIDEOS[example])
    if not video_path:
        return None, f"Example file {EXAMPLE_VIDEOS[example]} not found"

    return video_path, f"Showing example: {example}"


with gr.Blocks(title="manimator") as demo:
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

        with gr.TabItem("📄 PDF Upload"):
            with gr.Column():
                file_input = gr.File(label="Upload a PDF paper", file_types=[".pdf"])
                # 편집 모드 체크박스 추가
                pdf_edit_mode = gr.Checkbox(
                    label="편집하고 싶다면 체크",
                    value=False,
                    info="체크 해제 시: 자동 생성됨 | 체크 시: 각 단계에서 편집 가능"
                )
                pdf_button = gr.Button("Generate Animation from PDF")

            with gr.Row():
                pdf_video_output = gr.Video(label="Generated Animation")

            pdf_code_output = gr.Code(
                label="Generated Manim Code",
                language="python",
                interactive=False,
            )
            pdf_status_output = gr.Textbox(
                label="Status", interactive=False, show_copy_button=True
            )

        with gr.TabItem("✍️ Handwriting"):
            with gr.Column():
                handwriting_input = gr.File(
                    label="Upload handwritten image or PDF", 
                    file_types=[".jpg", ".jpeg", ".png", ".pdf"]
                )
                # 편집 모드 체크박스 추가
                handwriting_edit_mode = gr.Checkbox(
                    label="편집하고 싶다면 체크",
                    value=False,
                    info="체크 해제 시: 자동 생성됨 | 체크 시: 각 단계에서 편집 가능"
                )
                handwriting_button = gr.Button("Generate Animation from Handwriting")
                
                # OCR type selection
                ocr_type_radio = gr.Radio(
                    choices=["both", "mathpix", "google"],
                    value="both",
                    label="OCR Type",
                    info="Choose OCR method: 'both' for math + text, 'mathpix' for formulas, 'google' for text"
                )

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

        with gr.TabItem("Sample Examples"):
            sample_select = gr.Dropdown(
                choices=list(EXAMPLE_VIDEOS.keys()),
                label="Choose an example to display",
                value=None,
            )
            sample_video = gr.Video()
            sample_markdown = gr.Markdown()

            sample_select.change(
                fn=show_sample,
                inputs=sample_select,
                outputs=[sample_video, sample_markdown],
            )

    # 모달 제어 및 편집 처리 함수들
    def handle_text_input(prompt, edit_mode, state):
        """텍스트 입력 처리"""
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

    def handle_pdf_input(pdf_file, edit_mode, state):
        """PDF 입력 처리"""
        if not pdf_file:
            return (
                gr.Modal(visible=False),
                gr.Markdown("### 오류"),
                "",
                None, None, "PDF 파일을 업로드해주세요"
            )
        
        try:
            with open(pdf_file, "rb") as f:
                file_bytes = f.read()
                scene_description = process_pdf_prompt(file_bytes)
            
            if edit_mode:
                state["step1_output"] = scene_description
                state["current_step"] = 1
                state["edit_mode"] = True
                return (
                    gr.Modal(visible=True),
                    gr.Markdown("### 1단계: PDF 인식 결과 편집"),
                    scene_description,
                    None, None, "편집 모드가 활성화되었습니다"
                )
            else:
                # 자동 모드
                video, code, message = process_prompt_auto(scene_description)
                return (
                    gr.Modal(visible=False),
                    gr.Markdown("### 자동 생성 완료"),
                    "",
                    video, code, message
                )
        except Exception as e:
            return (
                gr.Modal(visible=False),
                gr.Markdown("### 오류"),
                "",
                None, None, f"PDF 처리 오류: {str(e)}"
            )

    def handle_handwriting_input(hw_file, edit_mode, state):
        """손글씨 입력 처리"""
        if not hw_file:
            return (
                gr.Modal(visible=False),
                gr.Markdown("### 오류"),
                "",
                None, None, "손글씨 파일을 업로드해주세요"
            )
        
        try:
            with open(hw_file, "rb") as f:
                file_bytes = f.read()
            
            if edit_mode:
                # 편집 모드: GPT Vision 원시 인식 결과만 추출 (scene_description 전 단계)
                recognized_text = process_handwriting_recognition_only(file_bytes)
                state["step1_output"] = recognized_text
                state["current_step"] = 1
                state["edit_mode"] = True
                return (
                    gr.Modal(visible=True),
                    gr.Markdown("### 1단계: GPT Vision 인식 결과 편집"),
                    recognized_text,  # 원시 인식 텍스트
                    None, None, "편집 모드가 활성화되었습니다"
                )
            else:
                # 자동 모드: 기존 파이프라인 그대로
                scene_description = process_handwriting_prompt(file_bytes)
                video, code, message = process_prompt_auto(scene_description)
                return (
                    gr.Modal(visible=False),
                    gr.Markdown("### 자동 생성 완료"),
                    "",
                    video, code, message
                )
        except Exception as e:
            return (
                gr.Modal(visible=False),
                gr.Markdown("### 오류"),
                "",
                None, None, f"손글씨 처리 오류: {str(e)}"
            )

    def handle_edit_save(edited_content, state):
        """편집 저장 및 다음 단계 진행"""
        try:
            current_step = state.get("current_step", 1)
            
            if current_step == 1:
                # 1단계 → 2단계: 스토리보드 생성
                state["step1_output"] = edited_content
                scene_description = process_prompt_scene(edited_content)
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
                response = generate_animation_response(edited_content)
                processor = ManimProcessor()
                code = processor.extract_code(response)
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
                processor = ManimProcessor()
                with processor.create_temp_dir() as temp_dir:
                    class_match = re.search(r"class (\w+)\(Scene\)", edited_content)
                    if not class_match:
                        return (
                            gr.Modal(visible=True),
                            gr.Markdown("### 오류"),
                            edited_content,
                            None, None, "Scene 클래스를 찾을 수 없습니다"
                        )
                    
                    scene_name = class_match.group(1)
                    scene_file = processor.save_code(edited_content, temp_dir)
                    video_path = processor.render_scene(scene_file, scene_name, temp_dir)
                    
                    if not video_path:
                        return (
                            gr.Modal(visible=True),
                            gr.Markdown("### 오류"),
                            edited_content,
                            None, None, "렌더링에 실패했습니다"
                        )
                    
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
    
    pdf_button.click(
        fn=handle_pdf_input,
        inputs=[file_input, pdf_edit_mode, session_state],
        outputs=[edit_modal, edit_step_title, edit_content, pdf_video_output, pdf_code_output, pdf_status_output]
    )
    
    handwriting_button.click(
        fn=handle_handwriting_input,
        inputs=[handwriting_input, handwriting_edit_mode, session_state],
        outputs=[edit_modal, edit_step_title, edit_content, handwriting_video_output, handwriting_code_output, handwriting_status_output]
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


def main():
    """Entry point for the Manimator application."""
    demo.launch()


if __name__ == "__main__":
    main()
