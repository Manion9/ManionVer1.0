#!/usr/bin/env python3
"""Quick handwriting recognition test"""

import os
import sys
from dotenv import load_dotenv

# Add the manimator module to path  
sys.path.insert(0, os.path.abspath('..'))

from manimator.utils.ocr_helpers import combined_ocr

# Load environment variables
load_dotenv('../config/.env')

def quick_ocr_test():
    """Quick OCR test with handwriting.png"""
    
    print("🔍 Quick OCR Test")
    print("=" * 30)
    
    # Check if image exists
    if not os.path.exists('../inputs/handwriting.png'):
        print("❌ handwriting.png not found!")
        print("💡 Please save your handwriting image as 'handwriting.png'")
        return
    
    # Load and test OCR
    with open('../inputs/handwriting.png', 'rb') as f:
        image_data = f.read()
    
    print(f"📸 Image loaded: {len(image_data)} bytes")
    
    # Test OCR
    print(f"\n🔍 Running OCR...")
    try:
        mathpix_result, google_result = combined_ocr(image_data)
        
        print(f"\n📐 Mathpix (수식 전용):")
        print(f"   {mathpix_result}")
        
        print(f"\n📝 Google Vision (텍스트 전용):")
        print(f"   {google_result}")
        
        # Determine best result
        if mathpix_result and "OCR failed" not in mathpix_result:
            print(f"\n✅ 수식 인식 성공!")
        elif google_result and "OCR failed" not in google_result:
            print(f"\n✅ 텍스트 인식 성공!")
        else:
            print(f"\n⚠️ OCR 결과를 확인하세요")
            
    except Exception as e:
        print(f"❌ OCR 실패: {e}")

if __name__ == "__main__":
    quick_ocr_test()