---
name: ios-capabilities
description: >-
  Reference for iOS/macOS app capabilities, permissions, entitlements, and
  Info.plist keys. Use whenever adding a capability or permission to an iOS or
  macOS app — even if the user doesn't use the exact terms. Triggers for "add
  permission", "request camera access", "Info.plist key", "usage description",
  "privacy permission", "iOS capability", "entitlement", "purpose string",
  "NSLocationUsageDescription", "microphone permission", "camera permission",
  "location access", "HealthKit", "HomeKit", "NFC", "Siri", "Face ID",
  "Bluetooth permission", "push notifications entitlement", or any request to
  enable a system feature that requires user consent or a capability entitlement.
---

# iOS Capabilities & Permissions Reference

Use this skill to look up the correct Info.plist keys, entitlements, and purpose strings when adding capabilities to an iOS app. The full lookup table is in `references/capabilities-reference.md`.

## Workflow

1. Identify which capability the user needs (camera, location, HealthKit, etc.)
2. Look up the capability in the reference table to find:
   - The Info.plist key(s) (e.g., `NSCameraUsageDescription`)
   - Any required entitlements (e.g., `com.apple.developer.healthkit`)
   - A default purpose string to use as a starting point
3. Write a purpose string tailored to the app's actual use case
4. Add the keys to the project configuration

## Purpose String Rules

Every Info.plist usage description key requires a purpose string that iOS displays to the user when requesting permission. Apple reviews these strings and will reject apps with bad ones.

**Requirements:**
- Must be shorter than 4,000 bytes
- Must be one complete sentence (you can add supplementary information after)
- Must be accurate, meaningful, and specific about why the app needs access
- Must describe what the app actually does with the data, not just that it needs it

**Good examples:**
- "Your location is used to show your position on the map, get directions, estimate travel times, and improve search results."
- "This app requires camera access to capture your site photos."
- "This app uses the microphone to record voice memos attached to your journal entries."

**Bad examples (will cause App Store rejection):**
- "We need your location." (not specific about why)
- "Location permission is required." (does not explain usage)
- "" (empty string -- instant rejection)
- A string that doesn't match what the app actually does with the permission

**Writing tips:**
- Start with "This app uses [resource] to [specific action]." or "[Resource] is used to [specific action]."
- Name the feature that requires the permission
- If the capability has multiple Info.plist keys (e.g., location has both `WhenInUse` and `AlwaysAndWhenInUse`), each key needs its own purpose string, and the "always" variant should explain why background access is needed

## Adding Capabilities to Project.json (XcodeGen Format)

In Bitrig projects (and any XcodeGen-based project), capabilities are configured in `Project.json` rather than editing Info.plist directly. The format is XcodeGen's spec serialized as JSON.

### Info.plist keys

Add usage description strings under the target's `info.properties` (or `settings.base.INFOPLIST_KEY_*` for modern Xcode build settings):

```json
{
  "targets": {
    "MyApp": {
      "info": {
        "properties": {
          "NSCameraUsageDescription": "This app uses the camera to scan documents.",
          "NSLocationWhenInUseUsageDescription": "Your location is used to find nearby stores."
        }
      }
    }
  }
}
```

### Entitlements

For capabilities that require entitlements (HealthKit, HomeKit, NFC, Siri, etc.), add them under the target's `entitlements` key:

```json
{
  "targets": {
    "MyApp": {
      "entitlements": {
        "path": "MyApp.entitlements",
        "properties": {
          "com.apple.developer.healthkit": true,
          "com.apple.developer.siri": true
        }
      }
    }
  }
}
```

### Adding to Info.plist directly

If not using XcodeGen, add keys directly to the `<dict>` in `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>This app uses the camera to scan documents.</string>
```

And for entitlements, add them to the `.entitlements` file:

```xml
<key>com.apple.developer.healthkit</key>
<true/>
```

## Capabilities That Require Entitlements

Not all capabilities need entitlements. Most only need an Info.plist usage description key. The ones that also require entitlements are:

- **HealthKit** (Read, Write, Clinical Records) -- `com.apple.developer.healthkit`
- **HomeKit** -- `com.apple.developer.homekit`
- **NFC** -- `com.apple.developer.nfc.readersession.formats`
- **Siri** -- `com.apple.developer.siri`

These must also be enabled in the Signing & Capabilities tab in Xcode (or the Apple Developer portal) in addition to the code-level configuration.

## Reference

See `references/capabilities-reference.md` for the complete lookup table of all 32 iOS capabilities with their keys, Info.plist entries, entitlements, SF Symbol icons, and default purpose strings.
