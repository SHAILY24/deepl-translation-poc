# DeepL Translation Tool

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://translate.shaily.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A clean, self-hostable translation tool built on DeepL's API.

**Live Demo:** https://translate.shaily.dev

## Features

- 26 language pairs with auto-detection
- Real-time translation
- Character counter
- Error handling (rate limits, timeouts, validation)
- Keyboard shortcut (Ctrl+Enter)
- Responsive design

## Stack

**Backend:**
- FastAPI with async httpx
- Pydantic validation
- uvicorn ASGI server
- uv package manager

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Yarn

**Deployment:**
- Docker multi-stage builds
- nginx reverse proxy
- SSL/TLS

## Quick Start

Need Docker and a DeepL API key (free tier: deepl.com/pro-api).

```bash
git clone https://github.com/SHAILY24/deepl-translation-poc.git
cd deepl-translation-poc
cp .env.example .env
# Add your DeepL API key to .env
docker compose up -d
```

- Frontend: http://localhost:13507
- Backend API: http://localhost:13601
- API Docs: http://localhost:13601/docs

## Development

**Backend:**
```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 13601
```

**Frontend:**
```bash
cd frontend
yarn install
yarn dev  # runs on :5173
```

## API

**POST /api/translate**

Request:
```json
{
  "text": "hello world",
  "target_lang": "ES"
}
```

Response:
```json
{
  "translated_text": "hola mundo",
  "source_lang": "EN",
  "target_lang": "ES",
  "character_count": 11
}
```

**GET /api/languages** - List supported languages  
**GET /health** - Health check

Note: For auto-detection, omit `source_lang` entirely. Don't send `"AUTO"` - DeepL's API will error.

## Architecture

```
User → nginx (SSL) → Frontend Container (React) → Backend Container (FastAPI) → DeepL API
```

- Frontend: Multi-stage Docker build (Node.js build, nginx serve)
- Backend: Python container with uv
- Networking: Internal Docker bridge network
- Security: CORS whitelist, input validation, environment variables

## What's Included

- Full translation workflow
- Error handling for API failures
- Docker deployment setup
- Production nginx config
- Clean, documented code

## Possible Improvements

This demo focuses on a clean core. A production version could add:

- User authentication
- Translation history (PostgreSQL)
- Per-user rate limiting
- Test suite
- CI/CD pipeline
- Advanced error messages
- Document translation

## Design Notes

The DeepL integration follows standard third-party API patterns: async HTTP with
httpx, structured error handling for upstream failures, and awareness of provider
rate limits and quotas.

## Project Structure

```
backend/
  main.py           # FastAPI routes
  Dockerfile        # Backend container
  pyproject.toml    # uv dependencies

frontend/
  src/App.jsx       # Main React component
  Dockerfile        # Multi-stage build
  package.json      # Yarn dependencies

docker-compose.yml  # Container orchestration
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Contact

Shaily Sharma  
shailysharmawork@gmail.com

**Portfolio:** https://portfolio.shaily.dev  
**GitHub:** https://github.com/SHAILY24

## Tech Choices

**FastAPI** - Async support, Pydantic validation, auto-generated API docs.

**React + Vite** - Fast dev experience, optimized builds.

**Docker** - Consistent deployment across environments.

**Tailwind** - Rapid UI development without custom CSS.
