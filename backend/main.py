"""
DeepL Translation API Backend
FastAPI service for translating text using DeepL API
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

app = FastAPI(
    title="DeepL Translation API",
    description="Translation service using DeepL API",
    version="1.0.0"
)

# CORS configuration - allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://translate.shaily.dev",
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000"   # Production frontend container
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get DeepL API key from environment
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
if not DEEPL_API_KEY:
    raise ValueError("DEEPL_API_KEY environment variable is required")

# DeepL API endpoint (use api-free.deepl.com for free tier)
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"


class TranslationRequest(BaseModel):
    """Request model for translation"""
    text: str = Field(..., min_length=1, max_length=50000, description="Text to translate")
    source_lang: Optional[str] = Field(None, description="Source language code (auto-detect if None)")
    target_lang: str = Field(..., description="Target language code")

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Validate text is not empty or whitespace only"""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()

    @field_validator('target_lang')
    @classmethod
    def validate_target_lang(cls, v: str) -> str:
        """Validate target language code"""
        valid_langs = {
            'EN-US', 'EN-GB', 'DE', 'FR', 'ES', 'IT', 'JA', 'ZH',
            'PT-PT', 'PT-BR', 'RU', 'NL', 'PL', 'TR', 'SV', 'DA',
            'FI', 'NO', 'CS', 'RO', 'HU', 'BG', 'EL', 'AR', 'KO', 'ID'
        }
        if v.upper() not in valid_langs:
            raise ValueError(f"Invalid target language. Must be one of: {', '.join(valid_langs)}")
        return v.upper()


class TranslationResponse(BaseModel):
    """Response model for translation"""
    translated_text: str
    source_lang: str
    target_lang: str
    character_count: int


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "deepl-translation-api"}


@app.post("/api/translate", response_model=TranslationResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad request"},
    429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def translate_text(request: TranslationRequest):
    """
    Translate text using DeepL API

    - **text**: Text to translate (max 50,000 characters)
    - **source_lang**: Source language code (optional, auto-detect if not provided)
    - **target_lang**: Target language code (required)
    """
    # Log request for debugging
    print(f"Translation request: source={request.source_lang}, target={request.target_lang}, text_len={len(request.text)}")

    try:
        # Prepare DeepL API request
        data = {
            "auth_key": DEEPL_API_KEY,
            "text": request.text,
            "target_lang": request.target_lang,
        }

        # Add source language if provided (skip AUTO for auto-detection)
        if request.source_lang and request.source_lang.upper() != "AUTO":
            # DeepL source languages don't use regional variants
            # Strip regional suffix: EN-US → EN, PT-BR → PT, etc.
            source = request.source_lang.upper().split("-")[0]
            data["source_lang"] = source

        # Make async request to DeepL API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(DEEPL_API_URL, data=data)

            # Handle DeepL API errors
            if response.status_code == 403:
                raise HTTPException(
                    status_code=500,
                    detail="Invalid DeepL API key. Please check configuration."
                )
            elif response.status_code == 456:
                raise HTTPException(
                    status_code=429,
                    detail="DeepL API quota exceeded. Please try again later."
                )
            elif response.status_code == 400:
                error_data = response.json() if response.text else {}
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid request: {error_data.get('message', 'Unknown error')}"
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"DeepL API error: {response.status_code}"
                )

            # Parse response
            result = response.json()
            translations = result.get("translations", [])

            if not translations:
                raise HTTPException(
                    status_code=500,
                    detail="No translation returned from DeepL API"
                )

            translation = translations[0]

            return TranslationResponse(
                translated_text=translation["text"],
                source_lang=translation.get("detected_source_language", request.source_lang or "AUTO"),
                target_lang=request.target_lang,
                character_count=len(request.text)
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Request to DeepL API timed out. Please try again."
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to DeepL API: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except Exception as e:
        # Log unexpected errors (in production, use proper logging)
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during translation"
        )


@app.get("/api/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    languages = [
        {"code": "EN-US", "name": "English (US)"},
        {"code": "EN-GB", "name": "English (UK)"},
        {"code": "DE", "name": "German"},
        {"code": "FR", "name": "French"},
        {"code": "ES", "name": "Spanish"},
        {"code": "IT", "name": "Italian"},
        {"code": "JA", "name": "Japanese"},
        {"code": "ZH", "name": "Chinese"},
        {"code": "PT-PT", "name": "Portuguese (Portugal)"},
        {"code": "PT-BR", "name": "Portuguese (Brazil)"},
        {"code": "RU", "name": "Russian"},
        {"code": "NL", "name": "Dutch"},
        {"code": "PL", "name": "Polish"},
        {"code": "TR", "name": "Turkish"},
        {"code": "SV", "name": "Swedish"},
        {"code": "DA", "name": "Danish"},
        {"code": "FI", "name": "Finnish"},
        {"code": "NO", "name": "Norwegian"},
        {"code": "CS", "name": "Czech"},
        {"code": "RO", "name": "Romanian"},
        {"code": "HU", "name": "Hungarian"},
        {"code": "BG", "name": "Bulgarian"},
        {"code": "EL", "name": "Greek"},
        {"code": "AR", "name": "Arabic"},
        {"code": "KO", "name": "Korean"},
        {"code": "ID", "name": "Indonesian"},
    ]
    return {"languages": languages}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
