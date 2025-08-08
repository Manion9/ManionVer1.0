#!/usr/bin/env python3
"""Test scene generation from mathematical equation."""

import os
import sys
from dotenv import load_dotenv

# Add the manimator module to path
sys.path.insert(0, os.path.abspath('.'))

from manimator.api.scene_description import process_handwriting_prompt, process_prompt_scene

# Load environment variables
load_dotenv()

def test_scene_generation_from_equation():
    """Test scene generation from the equation (x+3)² = 4"""
    
    print("🎬 Testing Scene Generation from Mathematical Equation")
    print("=" * 60)
    
    # Since we know Google Vision can recognize "(x+3)² = 4",
    # let's simulate the handwriting recognition result and generate a scene
    
    equation_text = "(x+3)² = 4"
    print(f"📝 Input equation: {equation_text}")
    
    print(f"\n🎯 Generating scene description...")
    
    try:
        # Use the existing prompt scene processor with our equation
        scene_description = process_prompt_scene(
            f"Create an animated explanation of solving the quadratic equation: {equation_text}"
        )
        
        print(f"✅ Scene description generated successfully!")
        print(f"\n📄 Scene Description:")
        print("-" * 40)
        print(scene_description)
        print("-" * 40)
        
        return scene_description
        
    except Exception as e:
        print(f"❌ Error generating scene: {e}")
        return None

def test_with_image_if_available():
    """Test with actual image if available"""
    
    image_files = ['handwriting.png', 'test_equation.png', 'equation.jpg', 'math.png']
    
    for image_file in image_files:
        if os.path.exists(image_file):
            print(f"\n🖼️ Found image file: {image_file}")
            print(f"Testing handwriting recognition...")
            
            try:
                with open(image_file, 'rb') as f:
                    image_data = f.read()
                
                scene_description = process_handwriting_prompt(image_data)
                
                print(f"✅ Handwriting processing successful!")
                print(f"\n📄 Generated Scene Description:")
                print("-" * 40)
                print(scene_description)
                print("-" * 40)
                
                return scene_description
                
            except Exception as e:
                print(f"❌ Error processing {image_file}: {e}")
                continue
    
    print(f"\nℹ️ No image files found. Tested files: {', '.join(image_files)}")
    print(f"💡 To test with your handwriting, save your image as 'handwriting.png'")
    return None

def main():
    """Main test function"""
    
    # Test 1: Scene generation from text equation
    scene_from_text = test_scene_generation_from_equation()
    
    # Test 2: Try with actual image if available
    scene_from_image = test_with_image_if_available()
    
    print(f"\n🎊 Test Summary:")
    print(f"Text-based scene generation: {'✅ Success' if scene_from_text else '❌ Failed'}")
    print(f"Image-based scene generation: {'✅ Success' if scene_from_image else 'ℹ️ No image available'}")
    
    if scene_from_text or scene_from_image:
        print(f"\n🎬 Ready to generate Manim animation!")
        print(f"Next step: Create the actual animation video using the scene description.")

if __name__ == "__main__":
    main()