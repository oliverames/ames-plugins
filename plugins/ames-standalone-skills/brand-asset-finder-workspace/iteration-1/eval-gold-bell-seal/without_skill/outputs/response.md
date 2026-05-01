# Gold Bell Seal Logo — Best Asset Found

## 1. Best Direct Source Image URL

```
https://static.wixstatic.com/media/b55db5_ed59a03ada07404bae57105c173f1d78~mv2.png
```

**Filename context from URL path:** `Bell%20Seal%20Logo_Gold%202026.png` (exposed in the full transformed URL)

## 2. Rendered/Transformed URL It Came From

```
https://static.wixstatic.com/media/b55db5_ed59a03ada07404bae57105c173f1d78~mv2.png/v1/crop/x_0,y_0,w_1006,h_1095/fill/w_67,h_73,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Bell%20Seal%20Logo_Gold%202026.png
```

This is the thumbnail Wix serves in the footer/accreditations area of Gryphon Place's website — cropped and resized to 67x73 pixels, encoded as AVIF with heavy compression.

## 3. Evidence Trail

1. **Task clue:** The task stated Gryphon Place uses the badge in its accreditations/footer area and their site is on Wix.

2. **Initial search:** Searched "Gryphon Place Gold Bell Seal Mental Health America" — confirmed Gryphon Place (gryphon.org) is in Kalamazoo, MI and is a Bell Seal recipient. The official MHA recipients list and Gryphon's own site both confirmed this.

3. **Direct site inspection:** Fetched `https://www.gryphon.org/` and asked specifically for Bell Seal badge image URLs in the accreditations/footer area.

4. **Wix CDN URL discovered:** The fetch returned the full transformed Wix CDN URL with all transformation parameters visible:
   ```
   /v1/crop/x_0,y_0,w_1006,h_1095/fill/w_67,h_73,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Bell%20Seal%20Logo_Gold%202026.png
   ```
   The filename in the URL (`Bell Seal Logo_Gold 2026.png`) confirmed this is the Gold 2026 badge.

5. **Original file recovery:** Removed the entire `/v1/crop/.../fill/.../Bell%20Seal%20Logo_Gold%202026.png` transformation path, leaving only the base Wix media hash URL:
   ```
   https://static.wixstatic.com/media/b55db5_ed59a03ada07404bae57105c173f1d78~mv2.png
   ```

6. **Verification:** Fetched the base URL. WebFetch confirmed it's a valid PNG (132.8 KB). Parsed the PNG IHDR chunk directly to confirm exact dimensions.

## 4. Why This Is Higher Resolution Than the Other Candidates

| Version | Dimensions | File size | Format |
|---------|-----------|-----------|--------|
| Transformed (rendered thumbnail) | 67 x 73 px | ~3-5 KB (AVIF, q_85) | AVIF |
| **Original source (this URL)** | **1006 x 1200 px** | **132.8 KB** | **PNG** |

- The original is **15x larger in each dimension** than the thumbnail.
- It has **247x more pixels** total (1,207,200 vs 4,891).
- It is PNG (lossless), not AVIF with lossy compression.
- The crop instruction in the transformed URL (`w_1006,h_1095`) confirms the original canvas was at least 1006px wide — the actual PNG is 1006x1200, with the extra 105 pixels of height below the crop boundary (likely transparent padding or whitespace).
- No other public candidate was found. MHA's own site does not publicly expose badge downloads; the toolkit is gated for recipients. Gryphon Place's Wix upload is the only publicly accessible, unprotected copy of the original file found.

## 5. Caveats on Usage Rights

- **Source:** This image was uploaded by Gryphon Place to their Wix-hosted website as a display asset. It was not sourced directly from MHA's gated promotion toolkit.
- **Official badge:** The filename (`Bell Seal Logo_Gold 2026.png`) and the link target (`https://mhanational.org/bell-seal-recognition/`) confirm this is the official MHA Gold Bell Seal badge for 2026 — not a custom graphic made by Gryphon Place.
- **Copyright:** The badge is owned by Mental Health America. Official usage rights are governed by MHA's Bell Seal promotion toolkit terms, which are distributed to certified recipients. Using this image outside of a Bell Seal recipient context, or without MHA's permission, may not be authorized.
- **Public accessibility:** Wix does not authenticate CDN media URLs, so the original file is publicly fetchable. This does not imply a license to use the image. If official authorization is needed, request the asset directly from MHA's Bell Seal team.
