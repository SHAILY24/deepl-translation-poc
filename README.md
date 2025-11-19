# DeepL Translation Tool

https://translate.shaily.dev

Quick translation tool I built using DeepL's API. Took about 2 hours.

## Stack

Backend is FastAPI with async httpx talking to DeepL. Frontend is React + Vite with Tailwind. Runs in Docker containers behind nginx.

Used uv instead of pip because it's way faster. Used Yarn for the frontend.

## Running It

You need Docker and a DeepL API key (free tier works - grab one at deepl.com/pro-api).

```bash
git clone https://github.com/SHAILY24/deepl-translation-poc.git
cd deepl-translation-poc
cp .env.example .env
# put your DeepL key in .env
docker compose up -d
```

Frontend runs on :13507, backend API on :13601. API docs at :13601/docs (FastAPI auto-generates them).

## Dev Mode

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
yarn dev  # runs on :5173
```

## How It Works

POST to `/api/translate` with your text and target language. It hits DeepL's API and returns the translation. Added error handling for their rate limits and timeouts. If you send `source_lang: "AUTO"` it breaks - you have to omit that field entirely for auto-detection (took me a minute to figure that out).

Supports 26 languages. Character limit is 50K per request (DeepL's limit).

```json
POST /api/translate
{
  "text": "hello world",
  "target_lang": "ES"
}

→ {
  "translated_text": "hola mundo",
  "source_lang": "EN",
  "target_lang": "ES",
  "character_count": 11
}
```

`GET /api/languages` gives you the full list.

## What's Here

- Translation with 26 language pairs
- Auto-detect source language (just don't send source_lang)
- Character counter in the UI
- Handles DeepL errors (403 bad key, 456 quota exceeded, timeouts)
- Press Ctrl+Enter to translate
- Works on mobile

## What's Not Here

This was a 2 hour build. If I was doing this for real I'd add:

- Login system
- Save translation history in Postgres
- Per-user rate limiting
- Tests
- CI/CD
- Better error messages
- Maybe document translation

## Why These Choices

**FastAPI** - async support out of the box, Pydantic validation, auto API docs. Works well with external APIs.

**React + Vite** - Vite is faster than Create React App. Tailwind because I can build UIs quickly without writing CSS.

**Docker** - easier to deploy. Frontend is a multi-stage build (Node for building, nginx for serving).

## Related Work

At PureHD I built an API gateway that handles QuickBooks, Stripe, UPS, FedEx, Avalara - basically 15+ vendor APIs. Does 100K+ calls per day. Had to solve token refresh, rate limiting, retry with backoff, all that stuff.

Also built shelf.shaily.dev which uses Stripe's API for payments. Had to deal with webhooks and idempotency keys to prevent duplicate charges.

DeepL is simpler than those but same concepts - async HTTP, proper error handling, don't hammer their rate limits.

## File Structure

```
backend/
  main.py           # FastAPI routes
  Dockerfile        

frontend/
  src/App.jsx       # main component
  Dockerfile        # multi-stage: build with node, serve with nginx

docker-compose.yml  # orchestrates both containers
```

Backend uses uv.lock instead of requirements.txt. Frontend has yarn.lock.

---

Shaily Sharma  
shailysharmawork@gmail.com

More stuff: https://portfolio.shaily.dev
