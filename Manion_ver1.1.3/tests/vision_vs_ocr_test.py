#!/usr/bin/env python3
"""Compare Vision Model vs OCR for handwriting recognition"""

import os
import sys
from dotenv import load_dotenv

# Add the manimator module to path
sys.path.insert(0, os.path.abspath('..'))

from manimator.api.scene_description import process_handwriting_prompt

# Load environment variables
load_dotenv('../config/.env')

def compare_recognition_methods():
    """Compare OCR vs Vision Model for handwriting recognition"""
    
    print("🔍 VISION MODEL vs OCR COMPARISON TEST")
    print("=" * 60)
    
    # Check if handwriting image exists
    if not os.path.exists('../inputs/handwriting.png'):
        print("❌ handwriting.png not found!")
        return
    
    # Load handwriting image
    with open('../inputs/handwriting.png', 'rb') as f:
        image_data = f.read()
    
    print(f"📸 Image loaded: {len(image_data)} bytes")
    print()
    
    # Test 1: Vision Model (NEW)
    print("🎯 TEST 1: GPT-4o Vision Model (NEW)")
    print("-" * 40)
    try:
        vision_result = process_handwriting_prompt(image_data, ocr_type="vision")
        
        print("✅ Vision Model Result:")
        print(f"Length: {len(vision_result)} characters")
        print(f"Preview:")
        print(vision_result[:600] + "..." if len(vision_result) > 600 else vision_result)
        
    except Exception as e:
        print(f"❌ Vision Model Error: {e}")
        vision_result = None
    
    print()
    
    # Test 2: OCR Method (OLD)
    print("🔍 TEST 2: OCR Method (OLD)")
    print("-" * 40)
    try:
        ocr_result = process_handwriting_prompt(image_data, ocr_type="both")
        
        print("✅ OCR Result:")
        print(f"Length: {len(ocr_result)} characters")
        print(f"Preview:")
        print(ocr_result[:600] + "..." if len(ocr_result) > 600 else ocr_result)
        
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        ocr_result = None
    
    print()
    
    # Comparison
    print("📊 COMPARISON SUMMARY")
    print("=" * 60)
    
    if vision_result and ocr_result:
        print("🏆 Both methods succeeded!")
        print(f"   Vision Model: {len(vision_result)} chars")
        print(f"   OCR Method: {len(ocr_result)} chars")
        
        # Check for mathematical accuracy keywords
        math_keywords = ['polynomial', 'factorization', 'x^3', 'x³', '(x-3)', 'roots']
        
        vision_math_score = sum(1 for keyword in math_keywords if keyword.lower() in vision_result.lower())
        ocr_math_score = sum(1 for keyword in math_keywords if keyword.lower() in ocr_result.lower())
        
        print(f"\n🧮 Mathematical accuracy indicators:")
        print(f"   Vision Model: {vision_math_score}/{len(math_keywords)} keywords found")
        print(f"   OCR Method: {ocr_math_score}/{len(math_keywords)} keywords found")
        
        if vision_math_score > ocr_math_score:
            print(f"🥇 Vision Model appears more mathematically accurate!")
        elif ocr_math_score > vision_math_score:
            print(f"🥇 OCR Method appears more mathematically accurate!")
        else:
            print(f"🤝 Both methods show similar mathematical accuracy!")
            
    elif vision_result:
        print("🏆 Only Vision Model succeeded!")
        print("✅ Vision Model: SUCCESS")
        print("❌ OCR Method: FAILED")
        
    elif ocr_result:
        print("🏆 Only OCR Method succeeded!")
        print("❌ Vision Model: FAILED")
        print("✅ OCR Method: SUCCESS")
        
    else:
        print("❌ Both methods failed!")
    
    print()
    print("💡 RECOMMENDATION:")
    if vision_result and (not ocr_result or len(vision_result) > len(ocr_result)):
        print("   Use Vision Model (ocr_type='vision') for better handwriting recognition!")
    else:
        print("   Continue using OCR methods for this type of content.")

def main():
    """Main function"""
    
    print("🎯 Testing improved handwriting recognition")
    print("📋 Comparing Vision Model vs OCR approaches")
    print()
    
    compare_recognition_methods()

if __name__ == "__main__":
    main()