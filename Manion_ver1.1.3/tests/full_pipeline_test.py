#!/usr/bin/env python3
"""Complete pipeline test: Handwriting Recognition -> Scene Description -> Manim Animation"""

import os
import sys
import base64
from dotenv import load_dotenv

# Add the manimator module to path
sys.path.insert(0, os.path.abspath('..'))

from manimator.utils.ocr_helpers import combined_ocr, process_image_file
from manimator.api.scene_description import process_handwriting_prompt
from manimator.api.animation_generation import generate_animation_response
from manimator.utils.schema import ManimProcessor

# Load environment variables
load_dotenv('../config/.env')

def save_user_image():
    """Save the user's handwriting image (this would be done manually)"""
    print("📸 Please save your handwriting image as 'handwriting.png' in this directory")
    print("   (The image should contain the mathematical factorization problem)")
    return 'handwriting.png'

def test_complete_pipeline():
    """Test the complete pipeline from handwriting to animation"""
    
    print("🚀 COMPLETE MANIMATOR PIPELINE TEST")
    print("=" * 60)
    
    # Check API keys
    print("🔑 Checking API configurations...")
    mathpix_id = os.getenv('MATHPIX_APP_ID')
    google_key = os.getenv('GOOGLE_VISION_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"   Mathpix: {'✅' if mathpix_id else '❌'}")
    print(f"   Google Vision: {'✅' if google_key else '❌'}")
    print(f"   OpenAI: {'✅' if openai_key and openai_key != 'sk-your-actual-openai-key-here' else '❌ Please set real API key'}")
    
    if not (mathpix_id and google_key and openai_key and openai_key != 'sk-your-actual-openai-key-here'):
        print("❌ Please configure all API keys properly!")
        return
    
    # Step 1: Load handwriting image
    image_path = '../inputs/handwriting.png'
    if not os.path.exists(image_path):
        print(f"❌ Image file '{image_path}' not found!")
        print("💡 Please save your handwriting image as 'handwriting.png'")
        return
    
    print(f"\n📖 Step 1: Loading handwriting image...")
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    print(f"   Image size: {len(image_data)} bytes")
    
    # Step 2: OCR Recognition
    print(f"\n🔍 Step 2: Performing OCR recognition...")
    try:
        mathpix_result, google_result = combined_ocr(image_data)
        
        print(f"   📐 Mathpix (Math formulas): {mathpix_result}")
        print(f"   📝 Google Vision (Text): {google_result}")
        
        # Use the better result or combine them
        ocr_text = ""
        if mathpix_result and mathpix_result != "Mathpix OCR failed":
            ocr_text += f"Mathematical content: {mathpix_result}\n"
        if google_result and google_result != "Google Vision OCR failed":
            ocr_text += f"Text content: {google_result}"
        
        if not ocr_text.strip():
            print("❌ No text could be extracted from the image!")
            return
        
        print(f"   ✅ Combined OCR result:")
        print(f"   {ocr_text}")
        
    except Exception as e:
        print(f"   ❌ OCR failed: {e}")
        return
    
    # Step 3: Generate Scene Description
    print(f"\n🎬 Step 3: Generating scene description...")
    try:
        scene_description = process_handwriting_prompt(image_data)
        
        print(f"   ✅ Scene description generated!")
        print(f"   Length: {len(scene_description)} characters")
        print(f"\n📄 Scene Description Preview:")
        print("-" * 50)
        print(scene_description[:500] + "..." if len(scene_description) > 500 else scene_description)
        print("-" * 50)
        
    except Exception as e:
        print(f"   ❌ Scene description failed: {e}")
        return
    
    # Step 4: Generate Manim Animation Code
    print(f"\n🎯 Step 4: Generating Manim animation code...")
    try:
        animation_response = generate_animation_response(scene_description)
        
        print(f"   ✅ Animation code generated!")
        print(f"   Response length: {len(animation_response)} characters")
        
        # Extract code from response
        processor = ManimProcessor()
        manim_code = processor.extract_code(animation_response)
        
        if not manim_code:
            print("   ❌ No valid Manim code found in response!")
            print("   Raw response preview:")
            print(animation_response[:300] + "...")
            return
        
        print(f"   ✅ Manim code extracted!")
        print(f"   Code length: {len(manim_code)} characters")
        
        # Save the code to file
        with open('generated_animation.py', 'w', encoding='utf-8') as f:
            f.write(manim_code)
        
        print(f"   💾 Code saved to 'generated_animation.py'")
        
        print(f"\n🐍 Generated Manim Code Preview:")
        print("-" * 50)
        print(manim_code[:800] + "..." if len(manim_code) > 800 else manim_code)
        print("-" * 50)
        
    except Exception as e:
        print(f"   ❌ Animation code generation failed: {e}")
        return
    
    # Step 5: Render Animation Video
    print(f"\n🎥 Step 5: Rendering animation video...")
    try:
        # Extract scene class name
        import re
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
            final_video_path = f"handwriting_animation_{scene_name}.mp4"
            shutil.copy2(video_path, final_video_path)
            print(f"   📁 Video copied to: {final_video_path}")
            
    except Exception as e:
        print(f"   ❌ Video rendering failed: {e}")
        return
    
    # Success!
    print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("📋 Generated Files:")
    print(f"   📝 Manim Code: generated_animation.py")
    print(f"   🎬 Animation Video: {final_video_path}")
    print(f"\n💡 You can now:")
    print(f"   - View the animation: {final_video_path}")
    print(f"   - Edit the code: generated_animation.py")
    print(f"   - Re-render with: manim generated_animation.py {scene_name}")

def main():
    """Main function"""
    
    print("🎯 Ready to test complete pipeline!")
    print("📋 Requirements checklist:")
    print("   1. ✅ OCR APIs configured (Mathpix + Google Vision)")
    print("   2. ⚠️  OpenAI API key in .env file")
    print("   3. 📸 Handwriting image saved as 'handwriting.png'")
    print()
    
    # Check if image exists
    if os.path.exists('handwriting.png'):
        print("✅ Found handwriting.png - starting pipeline test...")
        test_complete_pipeline()
    else:
        print("❌ handwriting.png not found!")
        print("💡 Please save your handwriting image as 'handwriting.png' first")
        print("   Then run: python full_pipeline_test.py")

if __name__ == "__main__":
    main()