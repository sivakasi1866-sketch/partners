from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.api.deps import get_current_user
from google import genai
from google.genai import types
import os
import base64

router = APIRouter()

class AIQuery(BaseModel):
    query: str
    role: str
    
class ImageQuery(BaseModel):
    prompt: str

@router.post("/assistant")
async def ask_assistant(query: AIQuery, current_user: dict = Depends(get_current_user)):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"success": False, "reply": "Gemini API key is not configured. Please add your key to use the AI Assistant."}
            
        client = genai.Client(
            api_key=api_key,
            http_options={'headers': {'User-Agent': 'aistudio-build'}}
        )
        
        system_instruction = (
            f"You are the Elite Bus AI Transit Assistant. "
            f"You are talking to a user with role '{query.role}'. "
        )
        
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=query.query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        reply = response.text if response.text else "I could not generate a response."
        return {"success": True, "reply": reply}
    except Exception as e:
        print(f"AI Assistant Error: {e}")
        return {"success": False, "reply": f"An error occurred: {str(e)}"}

@router.post("/image")
async def generate_image(query: ImageQuery, current_user: dict = Depends(get_current_user)):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"success": False, "error": "Gemini API key is not configured."}
            
        client = genai.Client(
            api_key=api_key,
            http_options={'headers': {'User-Agent': 'aistudio-build'}}
        )
        
        response = client.models.generate_images(
            model="gemini-3.1-flash-image",
            prompt=query.prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
            )
        )
        
        if response.generated_images and len(response.generated_images) > 0:
            img = response.generated_images[0].image
            b64 = base64.b64encode(img.image_bytes).decode("utf-8")
            return {"success": True, "image": f"data:image/jpeg;base64,{b64}"}
            
        return {"success": False, "error": "No image generated."}
    except Exception as e:
        print(f"Image Generation Error: {e}")
        return {"success": False, "error": f"An error occurred: {str(e)}"}
