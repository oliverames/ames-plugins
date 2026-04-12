#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate images using Google's Nano Banana Pro (Gemini 3 Pro Image) API.
Enhanced version with support for multiple reference images.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png" [--resolution 1K|2K|4K] [--api-key KEY]
    
    # With multiple reference images:
    uv run generate_image.py -p "prompt" -f output.png -i ref1.png -i ref2.png -i ref3.png
"""

import argparse
import os
import sys
from pathlib import Path


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("GEMINI_API_KEY")


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana Pro (Gemini 3 Pro Image)"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    parser.add_argument(
        "--input-image", "-i",
        action='append',
        dest='input_images',
        help="Optional input image path(s) for reference/editing (can be used multiple times)"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Gemini API key (overrides GEMINI_API_KEY env var)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Import here after checking API key to avoid slow import on error
    from google import genai
    from google.genai import types
    from PIL import Image as PILImage

    # Initialise client
    client = genai.Client(api_key=api_key)

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load input images if provided
    loaded_images = []
    output_resolution = args.resolution
    
    if args.input_images:
        for img_path in args.input_images:
            try:
                img = PILImage.open(img_path)
                loaded_images.append(img)
                print(f"Loaded reference image: {img_path}")
                
                # Auto-detect resolution from first image if using default
                if len(loaded_images) == 1 and args.resolution == "1K":
                    width, height = img.size
                    max_dim = max(width, height)
                    if max_dim >= 3000:
                        output_resolution = "4K"
                    elif max_dim >= 1500:
                        output_resolution = "2K"
                    else:
                        output_resolution = "1K"
                    print(f"Auto-detected resolution: {output_resolution} (from first image {width}x{height})")
            except Exception as e:
                print(f"Error loading input image {img_path}: {e}", file=sys.stderr)
                sys.exit(1)

    # Build contents: images first (if any), then prompt
    if loaded_images:
        contents = loaded_images + [args.prompt]
        print(f"Generating with {len(loaded_images)} reference image(s) at resolution {output_resolution}...")
    else:
        contents = args.prompt
        print(f"Generating image with resolution {output_resolution}...")

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    image_size=output_resolution
                )
            )
        )

        # Check if response has parts
        if not response.parts:
            print("Error: API returned empty response (possible safety filter or content block)", file=sys.stderr)
            sys.exit(1)

        # Process response and convert to PNG
        image_saved = False
        for part in response.parts:
            if part.text is not None:
                print(f"Model response: {part.text}")
            elif part.inline_data is not None:
                # Convert inline data to PIL Image and save as PNG
                from io import BytesIO

                # inline_data.data is already bytes, not base64
                image_data = part.inline_data.data
                if isinstance(image_data, str):
                    # If it's a string, it might be base64
                    import base64
                    image_data = base64.b64decode(image_data)

                image = PILImage.open(BytesIO(image_data))

                # Ensure RGB mode for PNG (convert RGBA to RGB with white background if needed)
                if image.mode == 'RGBA':
                    rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    rgb_image.save(str(output_path), 'PNG')
                elif image.mode == 'RGB':
                    image.save(str(output_path), 'PNG')
                else:
                    image.convert('RGB').save(str(output_path), 'PNG')
                image_saved = True

        if image_saved:
            full_path = output_path.resolve()
            print(f"\nImage saved: {full_path}")
            # Clawdbot parses MEDIA tokens and will attach the file on supported providers.
            print(f"MEDIA: {full_path}")
        else:
            print("Error: No image was generated in the response.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
