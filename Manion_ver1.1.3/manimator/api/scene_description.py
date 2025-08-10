from fastapi import HTTPException
import litellm
import os
from dotenv import load_dotenv

from manimator.utils.helpers import compress_pdf
from manimator.utils.system_prompts import SCENE_SYSTEM_PROMPT
from manimator.few_shot.few_shot_prompts import SCENE_EXAMPLES, PDF_EXAMPLE
from manimator.utils.ocr_helpers import process_image_file, validate_image_size, pdf_to_images
import base64

load_dotenv('../config/.env')


def process_prompt_scene(prompt: str) -> str:
    """Generate a scene description from a text prompt using LLM.

    This function takes a text prompt and generates a detailed scene description
    using the configured LLM model. It includes few-shot examples to improve
    the quality of generated descriptions.

    Args:
        prompt: The text prompt describing the desired scene

    Returns:
        str: Generated scene description

    Raises:
        HTTPException: If the model fails to generate a description
    """

    messages = [
        {
            "role": "system",
            "content": SCENE_SYSTEM_PROMPT,
        },
    ]
    messages.extend(SCENE_EXAMPLES)
    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    response = litellm.completion(
        model=os.getenv("PROMPT_SCENE_GEN_MODEL"),
        messages=messages,
        num_retries=2,
    )
    return response.choices[0].message.content


def process_pdf_prompt(
    file_content: bytes,
    model: str = os.getenv("PDF_SCENE_GEN_MODEL"),
    retry: bool = False,
) -> str:
    """Process a PDF file and generate a scene description using the specified model.

    Args:
        file_content: Raw PDF file bytes
        model: LLM model to use for processing. Defaults to env PDF_SCENE_GEN_MODEL
        retry: Whether this is a retry attempt and should it use the PDF_RETRY_MODEL

    Returns:
        str: Generated scene description

    Raises:
        HTTPException: If PDF processing fails or invalid input
    """
    if not file_content:
        raise HTTPException(status_code=400, detail="Empty PDF file provided")

    try:
        encoded_pdf = compress_pdf(file_content)
        messages = [
            {"role": "system", "content": SCENE_SYSTEM_PROMPT},
            *PDF_EXAMPLE,
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": f"data:application/pdf;base64,{encoded_pdf}",
                    }
                ],
            },
        ]

        response = litellm.completion(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        retry_model = os.getenv("PDF_RETRY_MODEL")
        if not retry and retry_model:
            return process_pdf_prompt(file_content, model=retry_model, retry=True)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


def process_handwriting_prompt(
    file_content: bytes,
    ocr_type: str = "vision", # 기본값을 vision으로 변경
    model: str = os.getenv("PDF_SCENE_GEN_MODEL"), # Vision 모델 사용
) -> str:
    """Process a handwritten image/PDF and generate a scene description.

    Args:
        file_content: Raw image or PDF file bytes
        ocr_type: Processing type to use:
            - "vision": Use GPT-4o Vision directly (recommended for handwriting)
            - "mathpix": Use Mathpix OCR for math formulas
            - "google": Use Google Vision OCR for text
            - "both": Use both OCR services
        model: LLM model to use for scene generation (vision models for "vision" mode)

    Returns:
        str: Generated scene description

    Raises:
        HTTPException: If handwriting processing fails or invalid input
    """
    if not file_content:
        raise HTTPException(status_code=400, detail="Empty file provided")

    # Validate file size
    max_size_mb = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    if not validate_image_size(file_content, max_size_mb):
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds {max_size_mb}MB limit"
        )

    try:
        # Vision 모드: 이미지를 직접 Vision Model에 전달
        if ocr_type == "vision":
            # 이미지를 base64로 인코딩
            image_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # 파일 타입 감지
            if file_content.startswith(b'%PDF'):
                # PDF인 경우 이미지로 변환
                image_list = pdf_to_images(file_content)
                if image_list:
                    image_base64 = base64.b64encode(image_list[0]).decode('utf-8')
                    mime_type = "image/jpeg"
                else:
                    raise HTTPException(status_code=400, detail="Could not convert PDF to image")
            elif file_content.startswith(b'\xff\xd8\xff'):
                mime_type = "image/jpeg"
            elif file_content.startswith(b'\x89PNG'):
                mime_type = "image/png"
            else:
                mime_type = "image/jpeg"  # 기본값
            
            # Vision Model에 직접 전달
            messages = [
                {"role": "system", "content": SCENE_SYSTEM_PROMPT},
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this handwritten mathematical content and create a detailed scene description for animating the concepts shown in the image."
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:{mime_type};base64,{image_base64}",
                        }
                    ],
                },
            ]
            
            response = litellm.completion(
                model=model,
                messages=messages,
                num_retries=2,
            )
            
            return response.choices[0].message.content
        
        else:
            # 기존 OCR 방식
            extracted_text = process_image_file(file_content, file_type="auto")
            
            if not extracted_text or extracted_text.strip() == "No text could be extracted from the provided file":
                raise HTTPException(
                    status_code=400, 
                    detail="No text could be extracted from the handwritten content"
                )

            # Create a prompt that includes the extracted text
            handwriting_prompt = f"""The following text was extracted from handwritten content (including mathematical formulas and regular text):

{extracted_text}

Please create a detailed scene description for animating the concepts found in this handwritten content."""

            # Generate scene description using the existing prompt processing logic
            messages = [
                {
                    "role": "system",
                    "content": SCENE_SYSTEM_PROMPT,
                },
            ]
            messages.extend(SCENE_EXAMPLES)
            messages.append(
                {
                    "role": "user",
                    "content": handwriting_prompt,
                }
            )
            
            response = litellm.completion(
                model=os.getenv("PROMPT_SCENE_GEN_MODEL"),  # 텍스트용 모델
                messages=messages,
                num_retries=2,
            )
            
            return response.choices[0].message.content

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process handwritten content: {str(e)}"
        )


def process_pdf_with_images(
    file_content: bytes,
    model: str = os.getenv("PDF_SCENE_GEN_MODEL"),
    retry: bool = False,
) -> str:
    """Process a PDF file by converting to images and generate a scene description.

    Args:
        file_content: Raw PDF file bytes
        model: LLM model to use for processing. Defaults to env PDF_SCENE_GEN_MODEL
        retry: Whether this is a retry attempt and should it use the PDF_RETRY_MODEL

    Returns:
        str: Generated scene description

    Raises:
        HTTPException: If PDF processing fails or invalid input
    """
    if not file_content:
        raise HTTPException(status_code=400, detail="Empty PDF file provided")

    try:
        # Convert PDF to images
        image_list = pdf_to_images(file_content)
        
        if not image_list:
            raise HTTPException(status_code=400, detail="Could not convert PDF to images")
        
        print(f"Converted PDF to {len(image_list)} images")
        
        # Process first page (or combine multiple pages)
        first_image = image_list[0]
        
        # Encode image to base64
        image_base64 = base64.b64encode(first_image).decode('utf-8')
        
        messages = [
            {"role": "system", "content": SCENE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    }
                ],
            },
        ]

        response = litellm.completion(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        retry_model = os.getenv("PDF_RETRY_MODEL")
        if not retry and retry_model:
            return process_pdf_with_images(file_content, model=retry_model, retry=True)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
