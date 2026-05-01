# Disability:IN DEI "Best Places to Work" Badge — Asset Recovery

## 1. Best Direct Source Image URL

```
https://iprsoftwaremedia.com/231/files/20246/DEIScoreLogos-Countries-UnitedStates_100.png
```

**File properties (verified by download):**
- Dimensions: 2500 x 2917 pixels
- Format: PNG with RGBA (full transparency — no background)
- File size: ~102 KB
- Aspect ratio: 0.86 (portrait)
- File last-modified: 2025-07-09

## 2. Rendered/Transformed URL It Came From

```
https://iprsoftwaremedia.com/231/files/20246/6696b7f03d6332be77701bcc_DEIScoreLogos-Countries-UnitedStates_100/DEIScoreLogos-Countries-UnitedStates_100_babd9637-912f-4e70-9667-b3d523b0438a-prv.png
```

**Properties of the preview version:**
- Dimensions: 1200 x 1400 pixels
- Format: PNG
- File size: ~118 KB
- The `-prv` suffix in the filename confirms this is a generated preview

**Transform pattern decoded:**
The IPR Software newsroom platform stores each press release asset in two locations:

| Version | Path pattern | Dimensions |
|---------|-------------|-----------|
| Preview | `/231/files/<release_id>/<hash>_<filename>/<filename>_<uuid>-prv.png` | 1200 x 1400 |
| Original | `/231/files/<release_id>/<filename>.png` | 2500 x 2917 |

Stripping the hash-prefixed subdirectory path and the `_<uuid>-prv` suffix, replacing with a flat `/files/<release_id>/<filename>.png`, recovers the full-resolution source upload.

## 3. Evidence Trail

**Company checked:** Associated Bank

**Page:** `https://newsroom.associatedbank.com/releases/associated-bank-recognized-as-a-disability-equality-indexR-best-place-to-work-for-disability-inclusion`

**How found:**
1. Searched for companies publicly displaying the DEI badge with press releases.
2. Associated Bank's newsroom page was found via web search for the badge recognition.
3. The page includes two image URLs for the DEI badge: a preview thumbnail URL (the `-prv.png` in a subdirectory) and a direct flat path. Both are hosted on `iprsoftwaremedia.com`, which is the media hosting CDN for IPR Software's press release platform — the backend that powers Associated Bank's newsroom.
4. The flat URL `DEIScoreLogos-Countries-UnitedStates_100.png` was downloaded and confirmed to be 2500x2917 px RGBA PNG.

**Cross-check against MillerKnoll:**
MillerKnoll's 2024 DEI press release (`news.millerknoll.com`) referenced a `DEI-thumb.jpg` that resolves to `filecache.mediaroom.com/mr5mr_millerknoll/184283/DEI-thumb.jpg` — a JPEG at only 300x225 pixels, clearly the thumbnail. That newsroom (BusinessWire/MediaRoom platform) does not expose a full-resolution original in the same way.

## 4. Why This Is Higher Resolution Than the Thumbnail Version

The thumbnail (`-prv.png`) is 1200x1400 — a server-generated preview that IPR Software creates for inline display in press release pages. The original upload (`DEIScoreLogos-Countries-UnitedStates_100.png`) is 2500x2917 — the file Associated Bank (or their PR team) uploaded to the platform before any resizing was applied.

At 2500 px wide, this version is suitable for:
- Print use at 8–10 inches at 300 DPI
- Full-bleed web hero images
- High-resolution social media use (LinkedIn, Twitter card)

The MillerKnoll JPEG thumbnail at 300x225 is a third-generation compressed copy and would be unsuitable for any print or high-visibility digital use.

Additionally, the full-res PNG has RGBA mode (alpha channel), meaning the badge has a transparent background — making it far more versatile for placement on any background color.

## 5. Caveats

**Official vs. recipient-hosted copy:**
This file is a **recipient-hosted copy**, not an official Disability:IN source file. It is hosted by Associated Bank's press release platform (IPR Software Media, account `231`). The filename `DEIScoreLogos-Countries-UnitedStates_100` suggests it is the score-100 United States badge variant, likely provided by Disability:IN to recipients as part of their annual recognition toolkit.

**No official public download from Disability:IN directly:**
The official Disability:IN website (`disabilityin.org`) and their S3 bucket (`disabilityin-bulk.s3.amazonaws.com`) do not have publicly accessible badge downloads for the DEI seal without authentication. The participant portal at `portal.disabilityin.org` appears to be where recognized companies access their assets — public access is restricted.

**Usage rights:**
The DEI badge is provided to recipient companies under a restricted license. It is intended only for organizations that scored 80 or above in the relevant program year, for use in approved communications referencing that year's recognition. The badge should not be used by non-recipients or by recipients claiming a score year they did not earn.

**Year ambiguity:**
The file last-modified date of 2025-07-09 suggests this is the 2025 Disability Equality Index badge (announced mid-year as is typical). The filename does not include a year, which is consistent with how Disability:IN distributes the asset — it is year-specific in their distribution but not encoded in the filename. Recipients uploading the 2024 badge in July 2024 and the 2025 badge in July 2025 may use the same filename, so you cannot rely on the name alone to determine the program year.

---

## Ranked Candidates

| Rank | URL | Dimensions | Format | Source |
|------|-----|-----------|--------|--------|
| 1 (best) | `iprsoftwaremedia.com/.../DEIScoreLogos-Countries-UnitedStates_100.png` | 2500x2917 | PNG RGBA | Recipient upload (Associated Bank, IPR Software platform) |
| 2 | `iprsoftwaremedia.com/.../-prv.png` | 1200x1400 | PNG | Server-generated preview of above |
| 3 | `filecache.mediaroom.com/mr5mr_millerknoll/184283/DEI-thumb.jpg` | 300x225 | JPEG | Thumbnail from MillerKnoll/BusinessWire newsroom |

The first candidate is clearly the best: largest dimensions, lossless PNG format, transparent background, and it is the pre-resize source upload.
