---
name: Generate Image
description: >-
  Use when the user asks to "generate an image", "create an image", "make a picture of",
  "draw", "design", "illustrate", "edit this image", "modify this photo", "change the
  background", or needs any kind of image generation or editing. Also triggers for
  "create a logo", "make a thumbnail", "generate artwork", "mockup", or visual asset
  creation. Uses Google Gemini's native image generation (text-to-image and image editing).
allowed-tools: Bash
---

# Generate Image

Create and edit images using Google's Gemini image generation API. Supports text-to-image
generation, image editing with reference images, and resolution control up to 4K.

## Quick Start

```bash
# Text to image
uv run ~/.claude/skills/generate-image/generate_image.py -p "description" -f output.png

# Higher resolution
uv run ~/.claude/skills/generate-image/generate_image.py -p "description" -f output.png -r 2K

# Edit an existing image
uv run ~/.claude/skills/generate-image/generate_image.py -p "make the sky purple" -f output.png -i source.png

# Multiple reference images
uv run ~/.claude/skills/generate-image/generate_image.py -p "combine these styles" -f output.png -i ref1.png -i ref2.png
```

## Two Modes

### Text-to-Image (no `-i` flag)

Generate an image purely from a text description. Best for:
- Illustrations, artwork, concept art
- Logos and visual assets
- Thumbnails and social media graphics
- Mockups and design concepts

### Image Editing (with `-i` flag)

Modify existing images using text instructions. Pass one or more reference images:
- `-i photo.png` — edit a single image
- `-i ref1.png -i ref2.png` — combine or reference multiple images

Best for:
- Changing colors, backgrounds, or elements
- Style transfer (apply one image's style to another)
- Removing or adding objects
- Enhancing or transforming photos

When using reference images, resolution auto-detects from the first image (overridable with `-r`).

## Resolution

| Flag | Size | Best for |
|------|------|----------|
| `-r 1K` | ~1024px (default) | Quick drafts, social media, thumbnails |
| `-r 2K` | ~2048px | Blog posts, presentations, detailed work |
| `-r 4K` | ~4096px | Print, high-detail artwork, large displays |

Higher resolution takes longer and uses more API quota. Start with 1K for iteration,
then regenerate at higher res when you're happy with the result.

## Writing Good Prompts

The prompt is everything. A vague prompt gets a generic image; a specific prompt gets
what you actually want.

### Structure: Subject + Style + Details + Mood

```
"A [subject] in [style], [specific details], [mood/lighting/color]"
```

**Weak:** "a cat"
**Better:** "a tabby cat sitting on a windowsill, watercolor style, warm afternoon light, soft pastel colors"

### Tips for Better Results

- **Be specific about style:** "oil painting", "vector illustration", "photorealistic", "pixel art",
  "pencil sketch", "isometric 3D", "flat design", "watercolor"
- **Describe composition:** "close-up", "wide shot", "birds-eye view", "centered", "rule of thirds"
- **Set the mood:** "warm", "dramatic", "minimal", "vibrant", "moody", "clean and professional"
- **Include context:** "on a white background", "in a dark forest", "against a gradient sky"
- **Specify what you don't want** by rephrasing positively: instead of "no text", try
  "clean image without any text or lettering"

### Common Patterns

| Use case | Prompt pattern |
|----------|---------------|
| Logo | "Minimal logo for [brand], [style], on white background, clean lines" |
| Thumbnail | "YouTube thumbnail showing [scene], bold and eye-catching, vibrant colors" |
| Social media | "[Subject], Instagram-style, bright and saturated, square composition" |
| Hero image | "Wide banner showing [scene], professional, [mood], 16:9 aspect ratio" |
| Icon | "App icon of [concept], flat design, rounded corners, single color palette" |
| Concept art | "[Scene description], concept art style, atmospheric, detailed environment" |

## Workflow

1. **Clarify what the user wants** — Subject, style, intended use, any specific requirements
2. **Generate at 1K first** — Fast iteration to get the concept right
3. **Show the result** — Use `open output.png` or let the user see it via `MEDIA:` output
4. **Iterate on the prompt** if needed — Adjust style, composition, details
5. **Regenerate at higher res** once the user is happy with the direction

## Output

The script saves a PNG file to the specified path and prints:
- `MEDIA: /path/to/output.png` — for automatic display in supported environments
- The full resolved path for easy access

To show the user the result:
```bash
open output.png  # macOS: opens in Preview
```

## Requirements

- `GEMINI_API_KEY` environment variable (Google Gemini API key)
- Dependencies (`google-genai`, `pillow`) are auto-installed by `uv run`
- Model: `gemini-3-pro-image-preview`

## Troubleshooting

| Issue | Solution |
|-------|---------|
| "No API key provided" | Set `GEMINI_API_KEY` env var or pass `--api-key` |
| Empty response / safety filter | Rephrase the prompt — some content triggers safety filters |
| "No image was generated" | The model returned text only — try a more visual/descriptive prompt |
| Low quality output | Be more specific in the prompt; try higher resolution |
| Wrong style | Explicitly name the style you want ("photorealistic", "vector", etc.) |
