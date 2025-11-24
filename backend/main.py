"""
DeepL Translation API Backend
FastAPI service for translating text using DeepL API
"""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

app = FastAPI(
    title="DeepL Translation API",
    description="Translation service using DeepL API",
    version="1.0.0",
    # Served under /api so the frontend's existing /api/ nginx proxy exposes
    # them publicly (the SPA owns the bare /docs path).
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
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

# Optional fallback DeepL API key from environment (bring-your-own-key model).
# The shared demo key was disabled due to abuse; visitors normally supply their
# own key per request. This env value is only used as a fallback if present.
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY") or None

# Friendly message shown when no API key is available at all
NO_KEY_MESSAGE = (
    "The shared demo key was disabled due to abuse; please enter your own "
    "DeepL API key (free keys end in :fx). It is used only to process this "
    "request and is never stored or logged."
)


def deepl_api_url(api_key: str) -> str:
    """Select the DeepL endpoint based on the key (free keys end in :fx)."""
    if api_key.endswith(":fx"):
        return "https://api-free.deepl.com/v2/translate"
    return "https://api.deepl.com/v2/translate"


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
async def translate_text(
    request: TranslationRequest,
    x_deepl_key: Optional[str] = Header(default=None, alias="X-DeepL-Key"),
):
    """
    Translate text using DeepL API (bring-your-own-key)

    - **text**: Text to translate (max 50,000 characters)
    - **source_lang**: Source language code (optional, auto-detect if not provided)
    - **target_lang**: Target language code (required)
    - **X-DeepL-Key** header: your DeepL API key, used only for this request
    """
    # Log request for debugging (never log the API key or the header)
    print(f"Translation request: source={request.source_lang}, target={request.target_lang}, text_len={len(request.text)}")

    # Resolve effective key: request header takes precedence, env is fallback
    request_key = x_deepl_key.strip() if x_deepl_key else None
    effective_key = request_key or DEEPL_API_KEY

    if not effective_key:
        raise HTTPException(status_code=400, detail=NO_KEY_MESSAGE)

    try:
        # Prepare DeepL API request
        data = {
            "auth_key": effective_key,
            "text": request.text,
            "target_lang": request.target_lang,
        }

        # Add source language if provided (skip AUTO for auto-detection)
        if request.source_lang and request.source_lang.upper() != "AUTO":
            # DeepL source languages don't use regional variants
            # Strip regional suffix: EN-US → EN, PT-BR → PT, etc.
            source = request.source_lang.upper().split("-")[0]
            data["source_lang"] = source

        # Make async request to DeepL API (endpoint chosen by the effective key)
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(deepl_api_url(effective_key), data=data)

            # Handle DeepL API errors
            if response.status_code in (401, 403):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "DeepL rejected this API key. Check the key, and note "
                        "free keys must end in :fx."
                    )
                )
            elif response.status_code == 456:
                raise HTTPException(
                    status_code=429,
                    detail="DeepL API quota exceeded for this key. Please try again later."
                )
            elif response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="DeepL rate limit reached for this key. Please slow down and try again."
                )
            elif response.status_code == 400:
                error_data = response.json() if response.text else {}
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid request: {error_data.get('message', 'Unknown error')}"
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"DeepL API error (status {response.status_code}). Please try again later."
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
