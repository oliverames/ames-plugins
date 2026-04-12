---
name: macos-app-icons
description: >-
  Extract high-resolution app icons from macOS .app bundles, including from
  Assets.car asset catalogs for icons up to 1024-2048px. Use when the user
  needs an app's icon as an image file — even if they don't say "extract".
  Triggers for "extract app icon", "get app icon", "app icon", "icns",
  "Assets.car icon", "extract icon from app", "highest resolution icon",
  "app bundle icon", "save icon as PNG", "I need the icon for [App]",
  "get the icon out of the .app", or any request to pull an icon image
  from a macOS application bundle.
---

# macOS App Icon Extraction

Modern macOS apps store icons in two places. You MUST check both to get the highest resolution available.

## Where Icons Live

| Location | Typical Max | Notes |
|----------|------------|-------|
| `Contents/Resources/AppIcon.icns` | 256–512px | Legacy fallback. Often low-res on modern apps. |
| `Contents/Resources/Assets.car` | 1024–2048px | Compiled asset catalog. Contains the real high-res icons. |

**Rule: Never trust `.icns` alone.** Always check `Assets.car` — it almost always has higher resolution.

## Step 1: Identify the icon name

```bash
defaults read "/Applications/Example.app/Contents/Info" CFBundleIconName
```

## Step 2: Check what's in Assets.car

```bash
assetutil -I "/Applications/Example.app/Contents/Resources/Assets.car" | python3 -c "
import json, sys
data = json.load(sys.stdin)
icons = [d for d in data if d.get('Name') == 'AppIcon']
for i in sorted(icons, key=lambda x: x.get('PixelWidth', 0)):
    print(f\"{i.get('PixelWidth')}x{i.get('PixelHeight')} @{i.get('Scale')}x - {i.get('RenditionName')}\")"
```

Replace `'AppIcon'` with whatever `CFBundleIconName` returned if different.

## Step 3: Extract at full resolution

Use `NSWorkspace` via a Swift script — this is the only reliable method that reads both `.icns` and `Assets.car`:

```swift
import Cocoa

let appPath = "/Applications/Example.app"
let appURL = URL(fileURLWithPath: appPath)
let icon = NSWorkspace.shared.icon(forFile: appURL.path)

// Find the largest pixel dimension across all representations
let reps = icon.representations
let maxPx = reps.map { max($0.pixelsWide, $0.pixelsHigh) }.max() ?? 1024
let ptSize = maxPx / 2  // @2x representations: points = pixels / 2

let bitmapRep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: maxPx,
    pixelsHigh: maxPx,
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: .deviceRGB,
    bytesPerRow: 0,
    bitsPerPixel: 0
)!
bitmapRep.size = NSSize(width: ptSize, height: ptSize)

NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmapRep)
icon.draw(in: NSRect(x: 0, y: 0, width: ptSize, height: ptSize),
          from: .zero, operation: .copy, fraction: 1.0)
NSGraphicsContext.restoreGraphicsState()

let pngData = bitmapRep.representation(using: .png, properties: [:])!
let outputPath = FileManager.default.homeDirectoryForCurrentUser
    .appendingPathComponent("Desktop/AppIcon.png")
try! pngData.write(to: outputPath)
print("Saved \(maxPx)x\(maxPx) icon to \(outputPath.path)")
```

Compile and run:
```bash
swiftc /tmp/extract_icon.swift -o /tmp/extract_icon && /tmp/extract_icon
```

## Common Pitfalls

- **`sips` upscales silently.** `sips -s format png --resampleHeightWidthMax 1024 AppIcon.icns` will happily upscale a 256px icon to 1024px. The output looks fine but is blurry. Always check the source resolution first.
- **`iconutil --convert iconset`** only reads `.icns` — it cannot access `Assets.car` at all.
- **Some apps have no `.icns` at all** and rely entirely on the asset catalog.
- **`NSWorkspace.shared.icon(forFile:)`** is the most reliable single call — it automatically resolves icons from both `.icns` and `Assets.car`, including @2x variants.
