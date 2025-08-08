from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import re
from pydantic import BaseModel
from dotenv import load_dotenv

from manimator.utils.schema import ManimProcessor
from manimator.utils.helpers import download_arxiv_pdf
from manimator.api.animation_generation import generate_animation_response
from manimator.api.scene_description import process_prompt_scene, process_pdf_prompt, process_handwriting_prompt


load_dotenv('config/.env')


class PromptRequest(BaseModel):
    prompt: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health-check")
async def health_check():
    return {"status": "ok"}


@app.post("/generate-pdf-scene")
async def generate_pdf_scene(file: UploadFile = File(...)):
    try:
        content = await file.read()
        scene_description = process_pdf_prompt(content)
        return {"scene_description": scene_description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-handwriting-scene")
async def generate_handwriting_scene(file: UploadFile = File(...)):
    """Generate scene description from handwritten image or PDF"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
            )
        
        content = await file.read()
        scene_description = process_handwriting_prompt(content)
        return {"scene_description": scene_description}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing handwriting: {str(e)}")


@app.post("/generate-prompt-scene")
async def generate_prompt_scene(request: PromptRequest):
    try:
        return {"scene_description": process_prompt_scene(request.prompt)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating scene descriptions: {str(e)}"
        )


@app.get("/pdf/{arxiv_id}")
async def process_arxiv_by_id(arxiv_id: str):
    """Process arxiv paper by ID"""
    try:
        arxiv_url = f"https://arxiv.org/pdf/{arxiv_id}"
        pdf_content = download_arxiv_pdf(arxiv_url)
        scene_description = process_pdf_prompt(pdf_content)
        return {"scene_description": scene_description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-animation")
async def generate_animation(request: PromptRequest):
    processor = ManimProcessor()

    try:
        with processor.create_temp_dir() as temp_dir:
            response = generate_animation_response(request.prompt)
            code = processor.extract_code(response)
            if not code:
                raise HTTPException(
                    status_code=400, detail="No valid Manim code generated"
                )
            class_match = re.search(r"class (\w+)\(Scene\)", code)
            if not class_match:
                raise HTTPException(
                    status_code=400, detail="No Scene class found in code"
                )
            scene_name = class_match.group(1)
            scene_file = processor.save_code(code, temp_dir)
            video_path = processor.render_scene(scene_file, scene_name, temp_dir)
            if not video_path:
                raise HTTPException(
                    status_code=500, detail="Failed to render animation"
                )
            return FileResponse(video_path, media_type="video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
