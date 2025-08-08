#!/usr/bin/env python3
"""Test script for handwriting OCR functionality."""

import os
import sys
from dotenv import load_dotenv

# Add the manimator module to path
sys.path.insert(0, os.path.abspath('.'))

from manimator.utils.ocr_helpers import mathpix_ocr, google_vision_ocr, combined_ocr

# Load environment variables
load_dotenv()

def test_with_sample_image():
    """Test OCR with a sample mathematical equation image."""
    
    # Since we don't have the actual image file yet, let's create a simple test
    # to verify our OCR functions are working
    
    print("🔍 Testing OCR Setup...")
    print(f"Mathpix App ID: {os.getenv('MATHPIX_APP_ID')[:10]}..." if os.getenv('MATHPIX_APP_ID') else "❌ No Mathpix App ID")
    print(f"Google Vision API Key: {os.getenv('GOOGLE_VISION_API_KEY')[:10]}..." if os.getenv('GOOGLE_VISION_API_KEY') else "❌ No Google Vision API Key")
    
    # Test if we can import all necessary modules
    try:
        from PIL import Image
        print("✅ PIL import successful")
    except ImportError as e:
        print(f"❌ PIL import failed: {e}")
        return
    
    try:
        import requests
        print("✅ Requests import successful")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return
    
    print("\n📝 Creating test image with equation (x+3)² = 4")
    
    # Create a simple test with a basic mathematical equation
    test_equation = "(x+3)² = 4"
    print(f"Expected to recognize: {test_equation}")
    
    # For now, let's just test if our functions can be called
    print("\n🔧 Testing function availability...")
    
    try:
        # Test imports
        from manimator.utils.ocr_helpers import process_image_file, validate_image_size
        print("✅ OCR helper functions imported successfully")
        
        from manimator.api.scene_description import process_handwriting_prompt
        print("✅ Handwriting processing function imported successfully")
        
        print("\n🎯 Ready for actual image testing!")
        print("Please save your handwriting image as 'test_image.png' in this directory")
        
        # Check if test image exists
        if os.path.exists('test_image.png'):
            print("📸 Found test_image.png, testing OCR...")
            
            with open('test_image.png', 'rb') as f:
                image_data = f.read()
                
            print(f"Image size: {len(image_data)} bytes")
            
            # Test both OCR methods
            print("\n🔍 Testing Mathpix OCR...")
            try:
                mathpix_result = mathpix_ocr(image_data)
                print(f"Mathpix result: {mathpix_result}")
            except Exception as e:
                print(f"Mathpix error: {e}")
            
            print("\n🔍 Testing Google Vision OCR...")
            try:
                google_result = google_vision_ocr(image_data)
                print(f"Google Vision result: {google_result}")
            except Exception as e:
                print(f"Google Vision error: {e}")
                
            print("\n🔍 Testing Combined OCR...")
            try:
                mathpix_res, google_res = combined_ocr(image_data)
                print(f"Combined results:")
                print(f"  Mathpix: {mathpix_res}")
                print(f"  Google: {google_res}")
            except Exception as e:
                print(f"Combined OCR error: {e}")
        else:
            print("ℹ️  No test image found. Save your image as 'test_image.png' to test.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_sample_image()