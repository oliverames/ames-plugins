# Disability:IN DEI Badge -- Highest-Resolution Source Research

## 1. Best Direct Source Image URL

**Official source (vector -- infinitely scalable):**
```
https://disabilityin-bulk.s3.amazonaws.com/2024/DEI/Disability+Equality+Index+2024+Logos/DEI+Score+Logos-General.svg
```
This is a 5 KB SVG exported from Adobe Illustrator 28.6.0, hosted directly on Disability:IN's own AWS S3 bucket (`disabilityin-bulk`). It contains the complete "BEST PLACE TO WORK FOR DISABILITY INCLUSION" badge design with the DI wordmark in green (#4ce35c) on navy (#252e65), in both a bordered and clean variant. As a vector file it scales to any resolution without loss.

**Best raster PNG (2000 x 2444 px, 256 KB):**
```
https://www.cai.io/__data/assets/image/0026/37466/DEIScoreLogos-Countries-UnitedStates_100_Copy.png
```
This is a direct file upload (no CDN transforms) on CAI's web server -- the filename `DEIScoreLogos-Countries-UnitedStates_100_Copy.png` exactly matches the naming convention used in Disability:IN's official S3 asset kit, indicating it is the official 100-score US badge. At 2000x2444 px it is the largest raster version found.

---

## 2. Rendered/Transformed URL (if different)

**Guardian Life -- Next.js image optimizer:**
- Rendered URL (as seen in browser): `https://www.guardianlife.com/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fgau1nv66ynug%2F4qLfy7WOqr0qGcHj5Fq8HU%2F4cc83a45c6f9a7dccaeeb6335e0c4ad2%2FDEI_Score_Logos-Countries-United_States_No_Score.png&w=1920&q=75`
- Underlying Contentful CDN asset (no transforms): `https://images.ctfassets.net/gau1nv66ynug/4qLfy7WOqr0qGcHj5Fq8HU/4cc83a45c6f9a7dccaeeb6335e0c4ad2/DEI_Score_Logos-Countries-United_States_No_Score.png`

The Next.js optimizer adds `w=1920&q=75` -- width cap at 1920px and JPEG quality 75. Stripping those parameters recovers the Contentful-hosted source, which is a 2084x2084 px PNG at 71 KB. Note that the Contentful URL has `No_Score` in the filename, indicating this is the "no score shown" variant (used by Guardian to display the badge without a numeric rating).

**CBRE -- direct JPEG, no transforms:**
- URL: `https://mediaassets.cbre.com/-/media/project/cbre/shared-site/press-releases/2024/july/cbre-named-best-place-to-work-for-disability-inclusion-for-fourth-consecutive-year/dei.jpg`
- Dimensions: 1080 x 1080 px, 83 KB JPEG. No CDN transform parameters; this is the original upload.

---

## 3. Evidence Trail

**Company sites checked:**
1. **Guardian Life** (`guardianlife.com/best-places-to-work-for-disability-inclusion-2024`) -- page uses Next.js; badge served via `/_next/image` optimizer wrapping a Contentful CDN URL. Stripping Next.js params recovered a 2084x2084 Contentful PNG.
2. **CAI** (`cai.io/resources/press-releases/cai-achieves-the-highest-rating-on-the-2024-disability-equality-index`) -- badge served as a direct PNG upload at `/__data/assets/image/...`. Filename matches official Disability:IN asset kit naming (`DEIScoreLogos-Countries-UnitedStates_100_Copy.png`). No CDN transforms. Recovered at 2000x2444 px.
3. **CBRE** (`cbre.com/press-releases/...`) -- badge served as a direct JPEG at `mediaassets.cbre.com`, 1080x1080 px.
4. **MillerKnoll** (`news.millerknoll.com/...`) -- page links to `DEI-thumb.jpg` which redirected to a PR Newswire file cache, only 300x225 px.

**Official source discovery:**
A Google search for `"DEIScoreLogos" disabilityin` surfaced the official S3 bucket at `disabilityin-bulk.s3.amazonaws.com`. Direct probing of paths modeled on the Contentful filename convention found three publicly accessible files in the `2024/DEI/Disability+Equality+Index+2024+Logos/` folder:

| File | Size | Format | HTTP |
|------|------|--------|------|
| `DEI+Score+Logos-General.svg` | 5 KB | SVG vector | 200 |
| `DEI+Score+Logos-General.ai` | 223 KB | Adobe Illustrator | 200 |
| `DEI+Score+Logos-General.eps` | 1.1 MB | EPS vector | 200 |

Score-specific variants (e.g. `..._100.png`) returned 403, suggesting they are gated to recipients only via the Disability:IN member portal (`portal.disabilityin.org`).

---

## 4. Why This is Higher Resolution Than the Thumbnail Version

**SVG:** The official `DEI+Score+Logos-General.svg` is a vector file with a logical `viewBox="0 0 500 375.5"`. Vector art scales to any output resolution -- 4K, 8K, print -- without pixelation. Every thumbnail PNG found elsewhere (300x225, 1080x1080) is a rasterized derivative of this vector source.

**CAI PNG (2000x2444):** The CAI file is likely a high-res PNG export from the same vector kit. At ~4.9 megapixels it is substantially larger than the typical badge thumbnail displayed inline (usually 200-400 px wide). The MillerKnoll "DEI-thumb.jpg" at 300x225 is 73x smaller in area.

**Contentful PNG (2084x2084):** Guardian's Contentful-hosted badge is 2084x2084 px in the original (un-transformed) asset. The Next.js `/_next/image` renderer with `w=1920` would produce a 1920px-wide render, but the underlying Contentful asset is larger. Stripping params (remove `?w=...&q=...`) recovers the full Contentful source.

---

## 5. Caveats

**Official vs. recipient-hosted:**
- The SVG/AI/EPS files at `disabilityin-bulk.s3.amazonaws.com` are the **official Disability:IN source assets**, uploaded to their own AWS bucket and used to generate the toolkit distributed to scored companies. Last-Modified date on the SVG is `2024-08-07`, consistent with 2024 DEI award season.
- The CAI PNG (`DEIScoreLogos-Countries-UnitedStates_100_Copy.png`) is a **recipient-hosted copy** -- CAI uploaded it to their own server. The filename suffix `_Copy` suggests it was exported from the official asset kit. It is the score-100 US variant, while the publicly accessible S3 SVG is the "General" variant (score-agnostic).
- The Contentful PNG (`DEI_Score_Logos-Countries-United_States_No_Score.png`) is hosted in Guardian's Contentful CMS space -- another recipient-hosted copy. The `No_Score` naming matches the General/score-agnostic variant.
- The CBRE JPEG at `mediaassets.cbre.com` is CBRE's own media server -- recipient-hosted.

**Which to use:**
For the highest quality and the official source, use the SVG from Disability:IN's S3 bucket:
```
https://disabilityin-bulk.s3.amazonaws.com/2024/DEI/Disability+Equality+Index+2024+Logos/DEI+Score+Logos-General.svg
```
This is the "General" (score-agnostic) variant -- no specific score number is displayed. Score-specific badges (100/90/80) appear to require member portal access. The CAI PNG is the best raster option for the score-100 US variant at 2000x2444 px, but it is a recipient upload rather than a direct Disability:IN source.

---

## All Candidate URLs (for reference)

| Resolution | Format | URL |
|------------|--------|-----|
| Vector (infinite) | SVG | `https://disabilityin-bulk.s3.amazonaws.com/2024/DEI/Disability+Equality+Index+2024+Logos/DEI+Score+Logos-General.svg` |
| Vector (infinite) | AI | `https://disabilityin-bulk.s3.amazonaws.com/2024/DEI/Disability+Equality+Index+2024+Logos/DEI+Score+Logos-General.ai` |
| Vector (infinite) | EPS | `https://disabilityin-bulk.s3.amazonaws.com/2024/DEI/Disability+Equality+Index+2024+Logos/DEI+Score+Logos-General.eps` |
| 2000x2444 | PNG | `https://www.cai.io/__data/assets/image/0026/37466/DEIScoreLogos-Countries-UnitedStates_100_Copy.png` |
| 2084x2084 | PNG | `https://images.ctfassets.net/gau1nv66ynug/4qLfy7WOqr0qGcHj5Fq8HU/4cc83a45c6f9a7dccaeeb6335e0c4ad2/DEI_Score_Logos-Countries-United_States_No_Score.png` |
| 1080x1080 | JPEG | `https://mediaassets.cbre.com/-/media/project/cbre/shared-site/press-releases/2024/july/cbre-named-best-place-to-work-for-disability-inclusion-for-fourth-consecutive-year/dei.jpg` |
| 300x225 | JPEG | `https://filecache.mediaroom.com/mr5mr_millerknoll/184283/DEI-thumb.jpg` |
