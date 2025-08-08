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

# 편집 가능한 손글씨 처리 함수
def process_handwriting_with_editing(file_path: str, edit_mode: bool, state: dict):
    """편집 모드가 적용된 손글씨 처리 함수"""
    try:
        if not file_path:
            return None, None, "Error: No file uploaded"
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            scene_description = process_handwriting_prompt(file_bytes)
            
        state["step1_input"] = file_path
        state["step1_output"] = scene_description
        
        if edit_mode:
            state["edit_mode"] = True
            state["current_step"] = 1
            return None, None, "편집 모드: 1단계 - 손글씨 인식 결과 편집이 필요합니다"
        else:
            # 자동 모드로 계속 진행
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


def interface_fn(prompt=None, pdf_file=None, handwriting_file=None):
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

    with gr.Tabs():
        with gr.TabItem("✍️ Text Prompt"):
            with gr.Column():
                text_input = gr.Textbox(
                    label="Describe the animation you want to create",
                    placeholder="Explain the working of neural networks",
                    lines=3,
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
            text_button.click(
                fn=interface_fn,
                inputs=[text_input],
                outputs=[video_output, code_output, status_output],
            )

        with gr.TabItem("📄 PDF Upload"):
            with gr.Column():
                file_input = gr.File(label="Upload a PDF paper", file_types=[".pdf"])
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
            pdf_button.click(
                fn=lambda pdf: interface_fn(prompt=None, pdf_file=pdf),
                inputs=[file_input],
                outputs=[pdf_video_output, pdf_code_output, pdf_status_output],
            )

        with gr.TabItem("✍️ Handwriting"):
            with gr.Column():
                handwriting_input = gr.File(
                    label="Upload handwritten image or PDF", 
                    file_types=[".jpg", ".jpeg", ".png", ".pdf"]
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
            handwriting_button.click(
                fn=lambda hw_file: interface_fn(prompt=None, pdf_file=None, handwriting_file=hw_file),
                inputs=[handwriting_input],
                outputs=[handwriting_video_output, handwriting_code_output, handwriting_status_output],
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


def main():
    """Entry point for the Manimator application."""
    demo.launch()


if __name__ == "__main__":
    main()
