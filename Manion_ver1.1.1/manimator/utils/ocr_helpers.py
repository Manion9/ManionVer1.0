"""OCR utilities for handwriting recognition using Mathpix and Google Vision APIs."""

import os
import base64
import requests
from typing import Optional, Tuple, Union
from io import BytesIO
from PIL import Image
import pdf2image
from google.cloud import vision
from fastapi import HTTPException


def setup_google_vision_client() -> vision.ImageAnnotatorClient:
    """Setup Google Vision API client using API key.
    
    Returns:
        vision.ImageAnnotatorClient: Configured client
    """
    # Set up Google Vision API key from environment
    api_key = os.getenv("GOOGLE_VISION_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Google Vision API key not configured")
    
    # For API key authentication, we'll use the REST API directly
    # since google-cloud-vision library prefers service account auth
    return None  # We'll use REST API instead


def mathpix_ocr(image_content: bytes) -> str:
    """Extract mathematical formulas and text from image using Mathpix OCR.
    
    Args:
        image_content: Raw image bytes
        
    Returns:
        str: Extracted text with LaTeX formulas
        
    Raises:
        HTTPException: If OCR processing fails
    """
    try:
        app_id = os.getenv("MATHPIX_APP_ID")
        app_key = os.getenv("MATHPIX_APP_KEY")
        
        if not app_id or not app_key:
            raise HTTPException(status_code=500, detail="Mathpix API credentials not configured")
            
        # Encode image to base64
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Mathpix API endpoint
        url = "https://api.mathpix.com/v3/text"
        
        headers = {
            "app_id": app_id,
            "app_key": app_key,
            "Content-type": "application/json"
        }
        
        data = {
            "src": f"data:image/jpeg;base64,{image_base64}",
            "formats": ["text", "latex_simplified"],
            "data_options": {
                "include_line_data": True,
                "include_word_data": True
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract text content
        if "text" in result:
            return result["text"]
        elif "latex_simplified" in result:
            return result["latex_simplified"]
        else:
            return "No text extracted from image"
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Mathpix API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mathpix OCR failed: {str(e)}")


def google_vision_ocr(image_content: bytes) -> str:
    """Extract text from image using Google Vision OCR.
    
    Args:
        image_content: Raw image bytes
        
    Returns:
        str: Extracted text
        
    Raises:
        HTTPException: If OCR processing fails
    """
    try:
        api_key = os.getenv("GOOGLE_VISION_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Google Vision API key not configured")
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Google Vision API endpoint
        url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "requests": [
                {
                    "image": {
                        "content": image_base64
                    },
                    "features": [
                        {
                            "type": "TEXT_DETECTION",
                            "maxResults": 1
                        }
                    ],
                    "imageContext": {
                        "languageHints": ["ko", "en"]  # Korean and English
                    }
                }
            ]
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract text from response
        if "responses" in result and len(result["responses"]) > 0:
            annotations = result["responses"][0].get("textAnnotations", [])
            if annotations:
                return annotations[0]["description"]
        
        return "No text extracted from image"
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Google Vision API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Vision OCR failed: {str(e)}")


def combined_ocr(image_content: bytes) -> Tuple[str, str]:
    """Extract both mathematical formulas and general text from image.
    
    Args:
        image_content: Raw image bytes
        
    Returns:
        Tuple[str, str]: (mathpix_result, google_vision_result)
    """
    mathpix_result = ""
    google_result = ""
    
    try:
        mathpix_result = mathpix_ocr(image_content)
    except Exception as e:
        print(f"Mathpix OCR failed: {str(e)}")
        mathpix_result = "Mathpix OCR failed"
    
    try:
        google_result = google_vision_ocr(image_content)
    except Exception as e:
        print(f"Google Vision OCR failed: {str(e)}")
        google_result = "Google Vision OCR failed"
    
    return mathpix_result, google_result


def pdf_to_images(pdf_content: bytes) -> list[bytes]:
    """Convert PDF pages to images for OCR processing.
    
    Args:
        pdf_content: Raw PDF bytes
        
    Returns:
        list[bytes]: List of image bytes (one per page)
        
    Raises:
        HTTPException: If PDF conversion fails
    """
    try:
        # Convert PDF to images using pdf2image
        images = pdf2image.convert_from_bytes(pdf_content, dpi=300, fmt='JPEG')
        
        image_bytes_list = []
        for image in images:
            # Convert PIL Image to bytes
            img_buffer = BytesIO()
            image.save(img_buffer, format='JPEG', quality=95)
            image_bytes_list.append(img_buffer.getvalue())
        
        return image_bytes_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to image conversion failed: {str(e)}")


def process_image_file(file_content: bytes, file_type: str = "auto") -> str:
    """Process image file and extract text using both OCR services.
    
    Args:
        file_content: Raw file bytes
        file_type: File type ("image", "pdf", or "auto")
        
    Returns:
        str: Combined extracted text
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        # Auto-detect file type if not specified
        if file_type == "auto":
            # Simple file type detection based on file signature
            if file_content.startswith(b'%PDF'):
                file_type = "pdf"
            elif file_content.startswith(b'\xff\xd8\xff') or file_content.startswith(b'\x89PNG'):
                file_type = "image"
            else:
                file_type = "image"  # Default to image
        
        extracted_texts = []
        
        if file_type == "pdf":
            # Convert PDF pages to images and process each
            image_list = pdf_to_images(file_content)
            
            for i, image_bytes in enumerate(image_list):
                mathpix_text, google_text = combined_ocr(image_bytes)
                
                page_text = f"=== Page {i+1} ===\n"
                if mathpix_text and mathpix_text != "Mathpix OCR failed":
                    page_text += f"Mathematical content:\n{mathpix_text}\n\n"
                if google_text and google_text != "Google Vision OCR failed":
                    page_text += f"Text content:\n{google_text}\n"
                
                extracted_texts.append(page_text)
                
        else:  # image
            mathpix_text, google_text = combined_ocr(file_content)
            
    # Process image directly
            combined_text = ""
            if mathpix_text and mathpix_text != "Mathpix OCR failed":
                combined_text += f"Mathematical content:\n{mathpix_text}\n\n"
            if google_text and google_text != "Google Vision OCR failed":
                combined_text += f"Text content:\n{google_text}\n"
            
            extracted_texts.append(combined_text)
        
        # Combine all extracted texts
        final_text = "\n".join(extracted_texts)
        
        if not final_text.strip():
            return "No text could be extracted from the provided file"
        
        return final_text
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


def validate_image_size(file_content: bytes, max_size_mb: int = 10) -> bool:
    """Validate image file size.
    
    Args:
        file_content: Raw file bytes
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        bool: True if size is acceptable
    """
    size_mb = len(file_content) / (1024 * 1024)
    return size_mb <= max_size_mb