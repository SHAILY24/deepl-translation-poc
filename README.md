# DeepL Translation Tool

Live demo: https://translate.shaily.dev

## What This Is

A web-based translation tool using the DeepL API. Built in about 2 hours as a proof-of-concept.

FastAPI backend, React frontend, deployed with Docker on my VPS.

## Tech Stack

**Backend:**
- FastAPI with async httpx for API calls
- Pydantic for validation
- uvicorn server
- uv for package management

**Frontend:**
- React 18 with Vite
- Tailwind CSS
- Yarn

**Deployment:**
- Docker containers
- nginx reverse proxy
- Cloudflare SSL

## Features

- 26 language pairs
- Auto-detect source language
- Character counter
- Error handling (rate limits, timeouts, validation)
- Keyboard shortcut (Ctrl+Enter)
- Mobile-friendly

## Running Locally

Need Docker and a DeepL API key (free at deepl.com/pro-api).

```bash
git clone https://github.com/SHAILY24/deepl-translation-poc.git
cd deepl-translation-poc
cp .env.example .env
# Add your DeepL API key to .env
docker compose up -d
```

Frontend: http://localhost:13507  
Backend API: http://localhost:13601  
API docs: http://localhost:13601/docs

## Development Mode

Backend:
```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 13601
```

Frontend:
```bash
cd frontend
yarn install
yarn dev
```

## API Endpoints

**POST /api/translate**
```json
{
  "text": "Hello world",
  "target_lang": "ES"
}
```

Returns:
```json
{
  "translated_text": "Hola mundo",
  "source_lang": "EN",
  "target_lang": "ES",
  "character_count": 11
}
```

**GET /api/languages** - List of supported languages

**GET /health** - Health check

## Project Structure

```
backend/          # FastAPI app
  main.py         # API endpoints
  Dockerfile      # Backend container

frontend/         # React app
  src/
    App.jsx       # Main component
  Dockerfile      # Multi-stage build (Node + nginx)

docker-compose.yml
```

## What's Missing

This is a 2-hour PoC. A production version would add:

- User authentication
- Translation history (database)
- Usage analytics
- Rate limiting per user
- Tests
- CI/CD
- Better error messages
- File translation

## Why FastAPI + React

FastAPI gives you async API calls, automatic validation, and built-in API docs. React with Vite builds fast and the DX is good. Docker makes deployment consistent.

## Similar Projects

I've integrated a bunch of external APIs:

**PureHD** - Built an API gateway handling QuickBooks, Stripe, UPS, Avalara, SendGrid. Processes 100K+ daily API calls. Had to deal with token refresh, rate limiting, retry logic, and timeouts.

**Shelf Bookstore** - Stripe payment integration with webhooks and idempotency keys. Live at shelf.shaily.dev.

The DeepL integration here is straightforward compared to those. Main thing is handling their error codes properly and not sending "AUTO" as source_lang (they want you to omit it for auto-detect).

## Contact

Shaily Sharma  
shailysharmawork@gmail.com

Portfolio: https://portfolio.shaily.dev  
GitHub: https://github.com/SHAILY24
