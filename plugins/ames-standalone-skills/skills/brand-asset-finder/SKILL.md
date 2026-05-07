---
name: brand-asset-finder
description: >-
  Finds the highest-resolution logo, badge, seal, award mark, media kit
  asset, or brand image. Inspects CMS/CDN transform URLs to recover original
  uploaded files; prefers SVG or transparent PNG over JPEG; separates
  official sources from recipient-posted copies; flags licensing
  uncertainty.
when_to_use: >-
  User asks to "find the logo", "get the badge", "download the seal", "find
  this award mark", "get the media kit asset", "find the brand image",
  "highest-res logo", "official logo", "get the official badge", or any
  request to locate a visual brand or recognition asset online. Also
  triggers for "find that award graphic", "download the trust badge", "get
  the accreditation seal", or "where can I get the [organization] logo".
---

# Brand Asset Finder

When asked to find a logo, badge, seal, or brand image, the goal is the highest-
resolution original in the best format — ideally an SVG or a PNG with a transparent
background. Do not declare a result until you have worked through the steps below.

## Format Priority

For any logo or badge, always prefer:

**SVG > PNG with transparency > PNG without transparency > JPEG**

JPEG cannot carry transparency, degrades edges and text, and is almost never the
format the organization actually distributes. If you find a JPEG, it is a signal
to keep looking. Before accepting any JPEG as final, try the same filename with
`.png` and `.svg` extensions. Only accept JPEG if those alternatives 404.

## Required Steps — Do All of These Before Reporting

### 1. Probe the official organization site

Check for a **media kit**, **press kit**, **brand resources**, or **recipient toolkit**
page. Also look for any publicly guessable CDN or S3 path. If you see the
organization's CDN bucket name anywhere (e.g. `orgname-bulk.s3.amazonaws.com` on a
recipient page), probe it directly — official SVG, AI, and EPS files are often stored
in year- or program-named folders and may be publicly accessible even when not linked.

### 2. Search news and press coverage about recipients — do this before giving up

Search for press releases, news articles, and announcements about recipients of the
award or users of the logo. Use queries like:
- `"[award name]" recipient announcement [year]`
- `"[org name]" "[award name]" site:prweb.com OR site:businesswire.com OR site:prnewswire.com`
- `"[award name]" filetype:png OR filetype:svg`

**Do not tell the user "this is the best I could find" until you have done this search.**
News articles and PR newsroom pages frequently embed the badge and expose the original
uploaded file URL. This step regularly surfaces higher-quality assets than the official
site or random recipient pages.

### 3. Visit recipient pages found via the above searches

Navigate to the specific recipient pages found in steps 1–2. For each page, do not
stop at the visually rendered image — always inspect the actual `src` URL of the
badge element and any surrounding `<a href>` or `data-src` attributes. A badge that
renders at 67×73 in a footer may be backed by a 1006×1200 source file.

### 4. Inspect every CMS-hosted image URL for transforms

Any image URL hosted on a known CMS or CDN **must** be inspected for transform
parameters, regardless of how the rendered image looks. The thumbnail might appear
"good enough" — the original file is almost always larger.

Transform signatures to look for:

| Pattern | Platform |
|---------|---------|
| `/v1/fill/w_N,h_N/` or `/v1/crop/...` | Wix |
| `-WxH` suffix before extension, e.g. `logo-300x200.png` | WordPress |
| `?format=Nw` or `?format=webp` | Squarespace |
| `/_next/image?url=...&w=N&q=N` | Next.js |
| `/upload/w_N,h_N/` in URL | Cloudinary |
| `_<uuid>-prv.png` inside a hash-named subdirectory | Press release platforms (IPR Software, etc.) |
| `?width=N`, `?w=N`, `?q=N` query params | Generic CDN |
| `.webp` or `.avif` when the original is likely `.png` | Format conversion |

When you find any of these patterns, derive the original (see step 5) and fetch it
before reporting. A Wix crop path like `w_1006,h_1095` tells you the original
dimensions without fetching — use that as a fast signal.

### 5. Strip the transforms

- **Wix**: remove everything between `/v1/` and the trailing filename →
  `static.wixstatic.com/media/<id>~mv2.png`
- **WordPress**: remove the `-WxH` size suffix → `logo.png` not `logo-300x200.png`
- **Squarespace**: remove `?format=...`
- **Next.js**: extract the inner URL from `url=`, then strip `?w=N&q=N`
- **Cloudinary**: remove `w_N,h_N` between `/upload/` and filename
- **Press release platforms**: replace `<hash>_<filename>/<filename>_<uuid>-prv.png`
  with flat `<filename>.png` at the release directory level
- **Imgix / generic CDN**: remove all query params

Fetch the derived URL and confirm it returns a valid image.

### 6. Apply the quality floor

The result is not ready to report until you have either:
- An SVG or vector file (any size)
- A standalone PNG with no transform in the URL, at **500px or larger in both dimensions**
- A Wix/CDN base URL confirmed to return a valid image (after stripping transforms)

If the best you have is:
- Under 500px → keep searching; you likely have a thumbnail
- A JPEG → look for `.png` and `.svg` variants before accepting
- A PNG without transparency for a badge/seal → look for an SVG or transparent-bg variant

A 335×400 JPEG from a recipient page is not a satisfactory final answer.
A 67×73 AVIF footer thumbnail is not a satisfactory final answer.
Both are signals to apply steps 2–5 harder.

## How to Report

Five bullets, nothing more unless asked:

1. **Best source URL** — the direct link to the highest-quality asset
2. **Where it came from** — one sentence: which page or path led here
3. **Why it wins** — format, dimensions, transparency; one sentence
4. **Official or recipient-hosted** — one sentence
5. **Licensing note** — one sentence if restrictions are known

Do not produce comparison tables unless asked. If the official source was gated,
say so in one sentence and report the best public copy found.

## Key Principle

The original file uploaded by the asset owner — before CMS serving, before CDN
resizing, before format conversion — is almost always larger, lossless, and often
a vector or transparent PNG. Every thumbnail you find is evidence that the original
exists somewhere upstream. The job is to climb back up that chain.
