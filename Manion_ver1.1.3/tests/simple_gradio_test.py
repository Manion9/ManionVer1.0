#!/usr/bin/env python3
"""Simple Gradio interface for handwriting recognition test"""

import gradio as gr
import os
import sys
from dotenv import load_dotenv

# Add the manimator module to path
sys.path.insert(0, os.path.abspath('.'))

from manimator.api.scene_description import process_handwriting_prompt

# Load environment variables
load_dotenv()

def process_handwriting_image(image_file):
    """Process uploaded handwriting image"""
    try:
        if not image_file:
            return "❌ No file uploaded"
        
        # Read the uploaded file
        with open(image_file, "rb") as f:
            image_data = f.read()
        
        print(f"Processing image: {image_file}")
        print(f"Image size: {len(image_data)} bytes")
        
        # Process with our handwriting function
        result = process_handwriting_prompt(image_data)
        
        return f"✅ Scene Description Generated:\n\n{result}"
        
    except Exception as e:
        return f"❌ Error processing image: {str(e)}"

def check_api_keys():
    """Check if API keys are configured"""
    mathpix_id = os.getenv('MATHPIX_APP_ID')
    google_key = os.getenv('GOOGLE_VISION_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    status = f"""🔑 API Key Status:
    
Mathpix: {'✅ Configured' if mathpix_id else '❌ Missing'}
Google Vision: {'✅ Configured' if google_key else '❌ Missing'}
OpenAI: {'✅ Configured' if openai_key and openai_key != 'sk-your-actual-openai-key-here' else '❌ Please set real API key'}

Ready for testing: {'✅ Yes' if all([mathpix_id, google_key, openai_key and openai_key != 'sk-your-actual-openai-key-here']) else '❌ Configure missing keys'}
"""
    return status

# Create Gradio interface
with gr.Blocks(title="Manimator Handwriting Test") as demo:
    gr.Markdown("# 🎬 Manimator 손글씨 인식 테스트")
    gr.Markdown("인수분해 손글씨 이미지를 업로드하여 Scene Description을 생성해보세요!")
    
    # API status
    with gr.Row():
        status_output = gr.Textbox(
            label="API 상태", 
            value=check_api_keys(),
            interactive=False,
            lines=8
        )
    
    # File upload and processing
    with gr.Row():
        with gr.Column():
            image_input = gr.File(
                label="손글씨 이미지 업로드 (JPG, PNG)", 
                file_types=[".jpg", ".jpeg", ".png"]
            )
            process_btn = gr.Button("🔍 Scene Description 생성", variant="primary")
        
        with gr.Column():
            result_output = gr.Textbox(
                label="결과", 
                lines=20,
                placeholder="여기에 결과가 표시됩니다..."
            )
    
    # Button click handler
    process_btn.click(
        fn=process_handwriting_image,
        inputs=[image_input],
        outputs=[result_output]
    )
    
    gr.Markdown("""
    ### 📋 사용 방법:
    1. 첨부해주신 인수분해 손글씨 이미지를 다운로드
    2. 위의 파일 업로드 버튼으로 업로드
    3. "Scene Description 생성" 버튼 클릭
    4. 결과 확인!
    
    ### ⚠️ 주의사항:
    - OpenAI API 키가 .env 파일에 제대로 설정되어야 합니다
    - 모든 API 키가 "✅ Configured"로 표시되어야 정상 작동합니다
    """)

if __name__ == "__main__":
    print("🚀 Starting Manimator Handwriting Test Interface...")
    print("📱 Web interface will open in your browser")
    print("🔑 Make sure your OpenAI API key is set in .env file!")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        debug=True
    )