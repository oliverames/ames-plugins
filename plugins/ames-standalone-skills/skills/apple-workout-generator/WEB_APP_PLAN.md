# Workout File Generator — Web App Implementation Plan

A simple web app that accepts text, images, or PDFs of workout plans, parses them using Claude, and produces a downloadable `.workout` file for Apple Watch.

## Feasibility Assessment

**Difficulty: Low-to-Moderate.** The hardest piece — generating valid `.workout` binaries — is already done. `generate_workout.py` is importable as a Python module with zero external dependencies. The main new work is:

1. A small FastAPI backend wrapping the existing generator + Claude API
2. A single-page frontend with file upload and text input
3. Prompt engineering for reliable workout parsing

An MVP could reasonably be built in a single focused session.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Browser                        │
│  ┌─────────────────────────────────────────────┐ │
│  │  Single-page HTML/CSS/JS                    │ │
│  │  - Text input (paste workout description)   │ │
│  │  - Image upload (drag-and-drop or browse)   │ │
│  │  - PDF upload (drag-and-drop or browse)     │ │
│  │  - Parsed workout preview (editable)        │ │
│  │  - Download .workout button                 │ │
│  └──────────────┬──────────────────────────────┘ │
└─────────────────┼───────────────────────────────┘
                  │ POST /api/convert
                  │ (multipart: text | image | pdf)
                  ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                      │
│                                                   │
│  /api/parse     → Claude API → structured JSON   │
│  /api/generate  → generate_workout.py → .workout │
│  /api/convert   → parse + generate (one-shot)    │
│  /              → serve static frontend           │
│                                                   │
│  Imports:                                         │
│    generate_workout.generate_workout_file()       │
│    anthropic.Anthropic()                          │
└─────────────────────────────────────────────────┘
```

### Why This Stack

| Choice | Rationale |
|--------|-----------|
| **FastAPI** | Lightweight, async, built-in file upload handling, auto-generates API docs |
| **Vanilla HTML/CSS/JS** | No build step, no node_modules, keeps the skill self-contained |
| **Claude API (server-side)** | Keeps API key safe on the server; handles text, images, and PDFs natively |
| **No database** | Stateless — parse, generate, return. Nothing to store |

---

## File Structure

```
skills/apple-workout-generator/
├── generate_workout.py              # Existing (unchanged)
├── SKILL.md                         # Existing (unchanged)
├── README.md                        # Existing (unchanged)
├── RESEARCH.md                      # Existing (unchanged)
├── webapp/
│   ├── app.py                       # FastAPI server (~150-200 lines)
│   ├── parsing_prompt.py            # Claude system prompt + parsing logic (~100 lines)
│   ├── requirements.txt             # fastapi, uvicorn, anthropic, python-multipart
│   ├── static/
│   │   ├── index.html               # Single-page frontend (~200 lines)
│   │   ├── style.css                # Styles (~150 lines)
│   │   └── app.js                   # Frontend logic (~200 lines)
│   ├── Dockerfile                   # Optional: containerized deployment
│   └── README.md                    # Setup & deployment instructions
```

**Total new code estimate: ~800-1000 lines** (excluding comments/whitespace).

---

## Implementation Steps

### Step 1: Backend API (`app.py`)

Three endpoints:

**`POST /api/parse`** — Parse input into structured JSON
- Accepts: multipart form with `text` field, or `file` (image/PDF)
- Sends content to Claude API with the workout-parsing system prompt
- Returns: structured workout JSON for preview/editing
- Error handling: returns clear messages if parsing fails

**`POST /api/generate`** — Generate .workout binary from JSON
- Accepts: JSON body (the workout definition)
- Calls `generate_workout.generate_workout_file(workout_def)`
- Returns: `.workout` file as binary download (`Content-Disposition: attachment`)
- No Claude API call needed — pure computation

**`POST /api/convert`** — One-shot parse + generate
- Combines parse and generate into a single request
- Returns the `.workout` file directly
- Convenience endpoint for users who don't need to edit

**`GET /`** — Serve the frontend
- Static file serving from `static/` directory

```python
# Sketch of app.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
import sys, os

# Import the existing generator as a module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_workout import generate_workout_file

app = FastAPI()

@app.post("/api/parse")
async def parse_workout(
    text: str = Form(None),
    file: UploadFile = File(None),
):
    # Send to Claude API, return structured JSON
    ...

@app.post("/api/generate")
async def generate_workout(workout_def: dict):
    workout_bytes = generate_workout_file(workout_def)
    name = workout_def.get("displayName", "workout").replace(" ", "_")
    return Response(
        content=workout_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{name}.workout"'}
    )

@app.post("/api/convert")
async def convert_workout(
    text: str = Form(None),
    file: UploadFile = File(None),
):
    # Parse then generate in one step
    ...

app.mount("/", StaticFiles(directory="static", html=True))
```

### Step 2: Claude Parsing Prompt (`parsing_prompt.py`)

The system prompt is critical for reliable parsing. It should include:

1. **The full JSON schema** (from SKILL.md)
2. **Activity type list** (so Claude maps correctly)
3. **Unit handling rules** (yards vs meters, detect from context)
4. **2-3 examples** of input → JSON output pairs
5. **Instructions for ambiguity** (default to yards for US pools, ask about units if truly unclear)

```python
SYSTEM_PROMPT = """You are a workout parser. Given a workout description
(text, image, or PDF), extract the structure into this exact JSON format:

{schema}

Rules:
- Use the same distance units shown in the source material
- For US pool workouts, default to yards unless meters are explicitly stated
- Map activity types to: {activity_list}
- Include rest periods as recovery steps with time goals
- Preserve set names and descriptions as displayName fields
- Return ONLY valid JSON, no markdown or explanation
"""
```

For **images**: Send as a Claude vision message with the image base64-encoded.
For **PDFs**: Use Claude's native PDF support (pass PDF as a document block in the API).
For **text**: Send as a user message.

### Step 3: Frontend (`index.html` + `app.js` + `style.css`)

**Layout:**
```
┌────────────────────────────────────────┐
│  🏊 Workout File Generator             │
│  Create .workout files for Apple Watch │
├────────────────────────────────────────┤
│                                        │
│  [Text] [Image] [PDF]    ← tab switch  │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  Paste your workout here...      │  │ ← textarea (text mode)
│  │                                  │  │ ← drag-and-drop zone (image/PDF)
│  └──────────────────────────────────┘  │
│                                        │
│  [ Parse Workout ]                     │
│                                        │
├────────────────────────────────────────┤
│  Parsed Workout Preview:              │
│  ┌──────────────────────────────────┐  │
│  │ Name: Masters 0219 Descending.. │  │
│  │ Warm Up: 600 yards              │  │
│  │ Block 1: 6x50 Kick (:15r)      │  │
│  │ Block 2: 6x100 FR Zone 2       │  │
│  │ ...                             │  │
│  │ Cooldown: 400 yards             │  │
│  │ Total: 2700 yards               │  │
│  └──────────────────────────────────┘  │
│                                        │
│  [ Download .workout File ]            │
│                                        │
└────────────────────────────────────────┘
```

**Key frontend behaviors:**
- **Tab switching** between text, image, and PDF input modes
- **Drag-and-drop** for image and PDF files (with click-to-browse fallback)
- **Loading spinner** during Claude API parsing
- **Editable preview** — user can review and tweak the parsed JSON before generating
- **Human-readable summary** alongside raw JSON (total yardage, set breakdown)
- **One-click download** of the generated `.workout` file
- **Mobile-responsive** — people may use this from their phones at the pool
- **File size validation** client-side (reject files over 10MB before uploading)

### Step 4: Dependencies (`requirements.txt`)

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
anthropic>=0.40.0
python-multipart>=0.0.6
```

Four dependencies total. `generate_workout.py` remains zero-dependency.

### Step 5: Deployment

**Option A: Local development (simplest)**
```bash
cd skills/apple-workout-generator/webapp
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn app:app --reload --port 8000
```

**Option B: Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option C: Cloud deployment**
- **fly.io** — `fly launch` with the Dockerfile, set `ANTHROPIC_API_KEY` as a secret
- **Railway** — Connect GitHub repo, auto-deploys
- **Render** — Free tier works for low-traffic use

---

## Input Handling Details

### Text Input
- User pastes workout text (e.g., copied from email, coaching app, whiteboard photo OCR)
- Sent directly to Claude as a text message
- Simplest path — no file handling needed

### Image Input
- Accepts: JPEG, PNG, GIF, WebP (Claude vision supported formats)
- Max file size: 10MB (Claude API limit for images)
- Base64-encode the image and send as an `image` content block in the Claude API message
- Claude reads the image and extracts workout structure

### PDF Input
- Accepts: PDF files up to 10MB
- Send directly to Claude API as a `document` content block (Claude supports native PDF)
- Works for multi-page workout plans, coaching PDFs, etc.
- For PDFs with >20 pages, could add page-range selection in the UI

---

## Error Handling

| Scenario | Response |
|----------|----------|
| Claude can't parse the workout | Show error message + raw Claude response for debugging |
| Ambiguous units (yards vs meters) | Claude response includes a `"note"` field; frontend prompts user to confirm |
| Invalid activity type | Backend returns validation error with supported types list |
| File too large | Client-side rejection before upload (< 10MB) |
| Claude API rate limit / error | Retry once, then show user-friendly error |
| Malformed JSON from Claude | Attempt JSON repair (strip markdown fences, etc.), then fail gracefully |

---

## Security Considerations

- **API key**: `ANTHROPIC_API_KEY` stored as environment variable, never sent to frontend
- **File uploads**: Validate MIME type and size server-side; reject unexpected types
- **Rate limiting**: Add basic rate limiting (e.g., 10 requests/minute per IP) to prevent abuse
- **No data storage**: Files are processed in-memory and never written to disk
- **CORS**: Restrict to same-origin in production

---

## Future Enhancements (Post-MVP)

These are **not** part of the initial build, but natural extensions:

1. **Workout library** — Save/browse previously generated workouts (would need a database)
2. **Direct AirDrop-style transfer** — QR code linking to the `.workout` file download
3. **Batch processing** — Upload multiple workout images at once
4. **Workout editing UI** — Visual drag-and-drop editor for building workouts from scratch
5. **Shareable links** — Generate a URL that produces the same .workout file
6. **PWA support** — Install as a home screen app on iPhone for quick access at the pool

---

## Summary

| Aspect | Details |
|--------|---------|
| **New code** | ~800-1000 lines across 5-6 files |
| **New dependencies** | 4 Python packages (`fastapi`, `uvicorn`, `anthropic`, `python-multipart`) |
| **Existing code reused** | `generate_workout.py` imported directly as a module (unchanged) |
| **Hardest part** | Prompt engineering for reliable parsing of diverse workout formats |
| **Simplest deployment** | `pip install` + `uvicorn` + set API key |
| **Production deployment** | Docker container on fly.io / Railway / Render |
