#!/usr/bin/env python3
"""Test PDF to Manim pipeline using existing manimator functionality"""

import os
import sys
import re
from dotenv import load_dotenv

# Add the manimator module to path
sys.path.insert(0, os.path.abspath('..'))

from manimator.api.scene_description import process_pdf_with_images
from manimator.api.animation_generation import generate_animation_response
from manimator.utils.schema import ManimProcessor

# Load environment variables
load_dotenv('../config/.env')

def test_pdf_to_manim_pipeline():
    """Test the complete PDF to Manim pipeline using existing functionality"""
    
    print("📄 PDF TO MANIM PIPELINE TEST")
    print("=" * 50)
    
    # Check API keys
    print("🔑 Checking API configurations...")
    openai_key = os.getenv('OPENAI_API_KEY')
    code_gen_model = os.getenv('CODE_GEN_MODEL')
    pdf_scene_model = os.getenv('PDF_SCENE_GEN_MODEL')
    
    print(f"   OpenAI API Key: {'✅' if openai_key and openai_key != 'sk-your-actual-openai-key-here' else '❌'}")
    print(f"   PDF Scene Model: {'✅' if pdf_scene_model else '❌'} ({pdf_scene_model})")
    print(f"   Code Gen Model: {'✅' if code_gen_model else '❌'} ({code_gen_model})")
    
    if not all([openai_key, pdf_scene_model, code_gen_model]):
        print("❌ Missing required API configurations!")
        return
    
    # Step 1: Find and load PDF file
    print(f"\n📖 Step 1: Loading fector.pdf...")
    
    # Find the PDF file
    pdf_path = '../inputs/fector.pdf'
    if not os.path.exists(pdf_path):
        pdf_path = None
    
    if not pdf_path:
        print("❌ fector.pdf not found!")
        return
    
    print(f"   📁 Found PDF: {pdf_path}")
    
    # Load PDF content
    with open(pdf_path, 'rb') as f:
        pdf_content = f.read()
    
    print(f"   📊 PDF size: {len(pdf_content)} bytes")
    
    # Step 2: Generate Scene Description using existing PDF processor
    print(f"\n🎬 Step 2: Generating scene description from PDF...")
    try:
        scene_description = process_pdf_with_images(pdf_content)
        
        print(f"   ✅ Scene description generated successfully!")
        print(f"   📏 Length: {len(scene_description)} characters")
        
        print(f"\n📄 Scene Description Preview:")
        print("-" * 50)
        print(scene_description[:800] + "..." if len(scene_description) > 800 else scene_description)
        print("-" * 50)
        
    except Exception as e:
        print(f"   ❌ Scene description failed: {e}")
        return
    
    # Step 3: Generate Manim Animation Code
    print(f"\n🎯 Step 3: Generating Manim animation code...")
    try:
        animation_response = generate_animation_response(scene_description)
        
        print(f"   ✅ Animation code generated!")
        print(f"   📏 Response length: {len(animation_response)} characters")
        
        # Extract code from response
        processor = ManimProcessor()
        manim_code = processor.extract_code(animation_response)
        
        if not manim_code:
            print("   ❌ No valid Manim code found in response!")
            print("   📄 Raw response preview:")
            print(animation_response[:500] + "...")
            return
        
        print(f"   ✅ Manim code extracted!")
        print(f"   📏 Code length: {len(manim_code)} characters")
        
        # Save the code to file
        code_filename = 'pdf_generated_animation.py'
        with open(code_filename, 'w', encoding='utf-8') as f:
            f.write(manim_code)
        
        print(f"   💾 Code saved to '{code_filename}'")
        
        print(f"\n🐍 Generated Manim Code Preview:")
        print("-" * 50)
        print(manim_code[:800] + "..." if len(manim_code) > 800 else manim_code)
        print("-" * 50)
        
    except Exception as e:
        print(f"   ❌ Animation code generation failed: {e}")
        return
    
    # Step 4: Render Animation Video
    print(f"\n🎥 Step 4: Rendering animation video...")
    try:
        # Extract scene class name
        class_match = re.search(r"class (\w+)\(Scene\)", manim_code)
        if not class_match:
            print("   ❌ No Scene class found in generated code!")
            return
        
        scene_name = class_match.group(1)
        print(f"   🎭 Scene class: {scene_name}")
        
        # Create temporary directory and render
        with processor.create_temp_dir() as temp_dir:
            scene_file = processor.save_code(manim_code, temp_dir)
            video_path = processor.render_scene(scene_file, scene_name, temp_dir)
            
            if not video_path:
                print("   ❌ Failed to render animation!")
                return
            
            print(f"   ✅ Animation rendered successfully!")
            print(f"   📹 Video saved to: {video_path}")
            
            # Copy video to current directory
            import shutil
            final_video_path = f"pdf_animation_{scene_name}.mp4"
            shutil.copy2(video_path, final_video_path)
            print(f"   📁 Video copied to: {final_video_path}")
            
    except Exception as e:
        print(f"   ❌ Video rendering failed: {e}")
        return
    
    # Success!
    print(f"\n🎉 PDF TO MANIM PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("📋 Generated Files:")
    print(f"   📝 Manim Code: {code_filename}")
    print(f"   🎬 Animation Video: {final_video_path}")
    print(f"\n💡 You can now:")
    print(f"   - View the animation: {final_video_path}")
    print(f"   - Edit the code: {code_filename}")
    print(f"   - Re-render with: manim {code_filename} {scene_name}")

def main():
    """Main function"""
    
    print("🎯 PDF to Manim Pipeline Test using existing manimator functionality")
    print("📄 Target: fector.pdf")
    print()
    
    test_pdf_to_manim_pipeline()

if __name__ == "__main__":
    main()