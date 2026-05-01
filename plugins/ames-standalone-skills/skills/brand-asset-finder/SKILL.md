---
name: brand-asset-finder
description: >-
  Find the highest-resolution logo, badge, seal, award mark, media kit asset,
  or brand image. Use whenever the user asks to "find the logo", "get the badge",
  "download the seal", "find this award mark", "get the media kit asset", "find
  the brand image", "highest-res logo", "official logo", "get the official badge",
  or any request to locate a visual brand or recognition asset online. Also triggers
  for "find that award graphic", "download the trust badge", "get the accreditation
  seal", or "where can I get the [organization] logo". Inspects CMS/CDN transform
  URLs to recover original uploaded files; separates official sources from
  recipient-posted copies; flags usage and licensing uncertainty.
---

# Brand Asset Finder

When asked to find a logo, badge, seal, award mark, media kit asset, or any brand
image, do not stop at the first obvious web result. The goal is the highest-resolution
original asset — not a thumbnail, resized CDN copy, or screenshot.

## Search Strategy

Work through these steps in order, stopping when you have a clear best candidate.

### 1. Official organization site first

Go to the organization's own website and look for:
- A **media kit**, **press kit**, or **brand resources** page
- A **recipient toolkit** or **partner resources** section (common for award badges)
- Press releases and news pages that link to downloadable assets
- Any `/assets/`, `/media/`, `/downloads/`, or `/brand/` directories if browseable

The official source is almost always higher quality and legally unambiguous.

### 2. Recipient and partner pages

Search for pages from award recipients, licensed partners, or news outlets that
embed the asset. These pages often reference the original file directly via an
`<img src="">` or `<a href="">` tag. Inspect the source URL — it may point back
to the organization's CDN with a full-resolution path.

### 3. Inspect image URLs for CMS/CDN transforms

When you find a candidate image URL, look carefully for transformation parameters
that indicate a resized or reformatted copy rather than the original:

| Pattern | Example | Meaning |
|---------|---------|---------|
| `/fill/w_<n>,h_<n>/` | `/fill/w_200,h_200/` | Wix crop/resize |
| `?width=<n>` or `?w=<n>` | `?width=300` | Query-string resize |
| `?quality=<n>` | `?quality=80` | Quality reduction |
| `/crop/...` | `/crop/200x200+0+0/` | Crop transform |
| `@2x`, `_thumb`, `_small`, `_preview` | `logo_thumb.png` | Named size variant |
| `.webp` or `.avif` converted from a source PNG/SVG | `logo.webp` | Format conversion |
| CDN resize: `cdn.example.com/resize/...` | varies | CDN-side transform |

### 4. Try stripping transform parameters

Attempt to derive the original source file by:
- Removing all query-string parameters (`?width=...&quality=...`)
- Removing CDN path segments like `/fill/w_200,h_200/`
- Replacing `.webp` or `.avif` with `.png` or `.svg`
- Trying the base filename without size suffixes (`logo.png` instead of `logo_300.png`)

Fetch the derived URL and check whether it loads a higher-resolution or different
format version. If it 404s, try one level up in the path.

### 5. Compare candidates

Before declaring a winner, compare candidate files across these dimensions:

- **Pixel dimensions** — larger is almost always better for print/design use
- **File type** — SVG > PNG with transparency > PNG without > JPEG > WebP thumbnail
- **Transparency** — a PNG or SVG with a transparent background is more versatile
- **Version/year** — check for current branding vs. an older or deprecated variant
- **Standalone vs. embedded** — a logo isolated on a transparent background vs. one
  embedded in a larger graphic (e.g., a web banner or composite image)

### 6. Separate official from recipient copies

Clearly distinguish:
- **Official source**: hosted on the organization's own domain or their designated CDN
- **Recipient/partner copy**: hosted by a third party who received or licensed the asset
- **Unknown provenance**: found on an unrelated site with no clear attribution

If the best-quality version is a recipient copy rather than the official source, say so.

Flag any uncertainty about usage rights — for example, award badges often come with
explicit use restrictions (only for a specific year, only for recipients, only in
approved contexts).

### 7. Report the result clearly

Give the user:

1. **Best source URL** — the direct link to the highest-quality asset found
2. **Rendered/visible URL** — the transformed version you first saw, if different
3. **Why this is the best version** — dimensions, file type, transparency, source authority
4. **Official vs. third-party** — which domain is serving it and whether it's authoritative
5. **Licensing note** (if relevant) — any visible use restrictions or terms

If you found multiple viable candidates at different quality levels, list them ranked
from best to worst with a one-line reason for each ranking.

## CMS/CDN URL Patterns by Platform

When the image is hosted on a known platform, apply the platform-specific stripping rule:

| Platform | Transform pattern | How to get the original |
|----------|------------------|------------------------|
| **Wix** | `static.wixstatic.com/media/<id>/v1/fill/w_N,h_N,.../<file>` | Remove everything between `/v1/` and the filename |
| **WordPress** | `example.com/wp-content/uploads/2024/01/logo-300x200.png` | Remove the `-300x200` size suffix |
| **Squarespace** | `images.squarespace-cdn.com/content/...?format=1500w` | Remove `?format=...` |
| **Contentstack** | `images.contentstack.io/v3/assets/.../logo.png?width=200` | Remove `?width=...` |
| **Frontify** | CDN URL with `/transform/...` path segment | Remove the transform segment |
| **Cloudinary** | `res.cloudinary.com/<account>/image/upload/w_200,h_200/logo.png` | Remove the `w_N,h_N` transform between `/upload/` and the filename |
| **Imgix** | `example.imgix.net/logo.png?w=200&auto=format` | Remove all query params |

When the platform isn't listed here, the general rule still applies: look for
numeric dimensions, `?width`/`?height`, crop paths, or format conversions in the
URL and try removing them.

## Key Principle

**A thumbnail is not the asset.** Most image search results and page screenshots
show CMS-resized thumbnails, not the source files. The source file — the one
uploaded by the asset owner before any web serving transformation — is almost
always larger, often in a lossless format, and sometimes available as a vector.
That is the version worth finding.
