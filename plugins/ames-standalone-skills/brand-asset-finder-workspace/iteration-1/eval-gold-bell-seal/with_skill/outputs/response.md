# Gold Bell Seal Award Logo -- Brand Asset Find Report

## 1. Best Direct Source Image URL

```
https://static.wixstatic.com/media/b55db5_ed59a03ada07404bae57105c173f1d78~mv2.png
```

This is the original Wix media file, before any crop/fill/format transformations are applied.

---

## 2. Rendered/Transformed URL It Came From

```
https://static.wixstatic.com/media/b55db5_ed59a03ada07404bae57105c173f1d78~mv2.png/v1/crop/x_0,y_0,w_1006,h_1095/fill/w_67,h_73,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Bell%20Seal%20Logo_Gold%202026.png
```

This is the version served in Gryphon Place's footer on `gryphon.org/about`. Wix applies a crop transform, scales it down to 67x73 px, applies USM sharpening, and converts to AVIF -- producing a 7,285-byte thumbnail. The source PNG is 135,963 bytes.

---

## 3. Evidence Trail

### Step 1 -- Official MHA site
Fetched `mhanational.org/bestemployers` and `mhanational.org/bell-seal-certification/bell-seal-benefits/`. The benefits page explicitly states recipients receive "a digital badge and templates for internal and external communications" via a promotion toolkit, but MHA does not publish the badge image publicly on their site. The badge is gated behind the certification process.

### Step 2 -- Recipient page search
Searched for recipients who might display the badge. The task clue pointed to Gryphon Place (Kalamazoo, MI) and La Prensa coverage. Gryphon Place's website (`gryphon.org`) is built on Wix.

### Step 3 -- Fetching gryphon.org/about
Fetched the page and extracted all image `src` attributes. The footer contains an accreditations row with five badges. The fifth image was identified as "Bell Seal Logo Gold 2026":

```
https://static.wixstatic.com/media/b55db5_ed59a03ada07404bae57105c173f1d78~mv2.png
/v1/crop/x_0,y_0,w_1006,h_1095
/fill/w_67,h_73,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto
/Bell%20Seal%20Logo_Gold%202026.png
```

### Step 4 -- Stripping Wix transforms
Per the Wix URL pattern documented in the skill: `static.wixstatic.com/media/<media_id>/v1/<transforms>/<filename>` -- removing everything between `/v1/` and the trailing filename leaves:

```
https://static.wixstatic.com/media/b55db5_ed59a03ada07404bae57105c173f1d78~mv2.png
```

Fetched this URL directly. It returned a valid PNG (HTTP 200, `content-type: image/png`, `content-length: 135963`).

### Step 5 -- Checking alternate candidates
Also found the CGI (Cummings Graduate Institute) recipient page at `cgi.edu`, which hosts:
- `cgi.edu/wp-content/uploads/3-X_Gold-2024.png` -- 1600x900 PNG, 416 KB. This is a promotional banner (composite graphic: office photo background + "2024 Bell Seal Recipient" text + the badge seal in the corner). Not a standalone badge.
- `cgi.edu/wp-content/uploads/3-X_Gold-2024-1536x864-1.png` -- 1536x864, WordPress-resized version of the above.
- `cgi.edu/wp-content/uploads/Bell-Seal-Logo_Gold-2024-250x250-1.png` -- 250x250, too small.

Also found the St. Bonaventure University page serving a 335x400 JPEG of the 2026 Gold badge -- lower resolution than the Wix source.

### Step 6 -- Visual confirmation
Both the Wix source and the CGI banner were rendered visually. The Wix source confirmed to be the standalone Gold Bell Seal badge: circular gold medal with "THE BELL SEAL FOR WORKPLACE MENTAL HEALTH" around the perimeter, a bell icon with the MHA logo inside, and "2026 GOLD" typography below the circle, on a clean white background. The CGI banner is a promotional composite, not the isolated badge.

---

## 4. Why This Is the Best Version

| Candidate | Format | Dimensions | Pixels | Bytes | Notes |
|-----------|--------|-----------|--------|-------|-------|
| **Gryphon Place Wix source** | **PNG** | **1006x1200** | **1,207,200** | **135,963** | Standalone badge, white bg, 2026 |
| CGI 3-X Gold 2024 (original) | PNG | 1600x900 | 1,440,000 | 416,380 | Promotional banner composite, not standalone badge |
| CGI 3-X Gold 2024 (WP resized) | PNG | 1536x864 | 1,327,104 | 401,755 | Same banner, WP thumbnail |
| SBU Bell Seal Gold 2026 | JPEG | 335x400 | 134,000 | 104,585 | Standalone badge but JPEG lossy + low-res |
| CGI Logo Gold 2024 250x250 | PNG | 250x250 | 62,500 | 14,218 | Too small |
| Wix thumbnail (transformed) | AVIF | 67x73 | 4,891 | 7,285 | Wix-generated thumbnail, not usable |

The Gryphon Place Wix source wins because:
- It is the **standalone badge** (isolated gold seal on white background) rather than a promotional composite or banner
- It is **PNG with a white background** -- lossless, the most versatile format for design use
- It is the **2026 version** of the badge, current as of May 2026
- At **1006x1200** it has roughly 1.2 megapixels of badge-specific content. The CGI banner has more raw pixels (1,440,000) but the badge occupies only a small corner of that frame -- zooming into just the badge would yield far fewer usable pixels than the standalone version
- The Wix media hash (`b55db5_ed59a03ada07404bae57105c173f1d78~mv2.png`) is the original as uploaded by the Gryphon Place Wix site admin -- it predates any CDN transformation

---

## 5. Caveats About Usage Rights

**This is a recipient-hosted copy, not served from MHA's own CDN.**

- The file is served from `static.wixstatic.com` under Gryphon Place's Wix account (media bucket `b55db5`). It is not hosted on `mhanational.org` or any MHA-controlled CDN.
- MHA's Bell Seal promotion toolkit (including the digital badge) is distributed only to certified recipients. The badge image is not published in MHA's public media kit or press resources.
- The badge design itself is MHA's intellectual property. MHA's recognition program terms typically restrict badge use to: the specific year awarded, the specific recipient organization, and approved contexts (marketing materials, website, press releases).
- The 2026 badge design visible in this file is current. A 2024-vintage badge (visible in CGI's hosted versions) would be out of date.
- For any third-party use beyond research, obtaining the badge directly from MHA (by becoming a certified recipient or requesting via press inquiry) is the appropriate path.
- The `gryphon.org` Wix account's media bucket prefix (`b55db5`) is distinct from the `77b896` bucket used for Gryphon Place's other accreditation badges (COA, AIRS, AAS), suggesting Gryphon Place may have uploaded this badge themselves from the MHA promotion toolkit -- meaning this is as close to the "original distributed file" as publicly accessible.
