---
name: xcodegen-project
description: >-
  Reference for configuring XcodeGen projects using Bitrig's JSON-based
  Project.json format. Use whenever creating, modifying, or debugging a
  XcodeGen project — even if the user doesn't say "XcodeGen" explicitly.
  Triggers for "Project.json", "XcodeGen", "xcode project config", "add target",
  "add dependency", "deployment target", "bundle identifier", "build settings",
  "create iOS project", "create macOS project", "multi-platform project",
  "local Swift package", "app extension", "widget extension", "framework target",
  "test target", or any task involving generating or editing an Xcode project
  from a declarative config file.
---

# XcodeGen Project Configuration for Bitrig

Bitrig uses XcodeGen to generate Xcode projects from a declarative `Project.json` file. Unlike standard XcodeGen which uses YAML (`project.yml`), Bitrig projects use **JSON format** exclusively. The file is always named `Project.json` and lives at the root of the project directory.

XcodeGen applies built-in setting presets automatically based on the target type, platform, and build configuration. You do not need to manually specify most compiler warnings, SDK roots, or optimization flags -- those come from presets. Only specify settings that differ from or extend the defaults. Consult the `references/platform-presets.md` file in this skill for the full preset values when you need to check what is already set.

## Complete Project.json Schema

```json
{
  "name": "ProjectName",
  "configs": {
    "Debug": "debug",
    "Release": "release"
  },
  "options": {
    "groupSortPosition": "bottom",
    "transitivelyLinkDependencies": false,
    "bundleIdPrefix": "com.example",
    "deploymentTarget": { "iOS": "17.0", "macOS": "14.0" },
    "createIntermediateGroups": true,
    "defaultConfig": "Debug",
    "generateEmptyDirectories": false,
    "minimumXcodeGenVersion": "2.38.0"
  },
  "settings": {
    "CODE_SIGN_IDENTITY": "-",
    "DEVELOPMENT_TEAM": "TEAM_ID"
  },
  "packages": {
    "PackageName": {
      "url": "https://github.com/org/repo.git",
      "from": "1.0.0"
    },
    "LocalPackage": {
      "path": "Packages/LocalPackage"
    }
  },
  "targets": { }
}
```

### Top-Level Keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | string | Yes | Project name. Used as the `.xcodeproj` name. |
| `configs` | object | Yes | Maps configuration names to types. Values must be `"debug"` or `"release"`. |
| `options` | object | No | Project-wide generation options. |
| `settings` | object | No | Project-level build settings applied to all targets. |
| `packages` | object | No | Swift Package Manager dependencies (remote or local). |
| `targets` | object | Yes | Dictionary of target name to target definition. |
| `schemes` | object | No | Custom scheme definitions. XcodeGen auto-generates schemes if omitted. |
| `settingGroups` | object | No | Reusable groups of build settings referenced by targets. |
| `fileGroups` | array | No | Additional file paths to include in the project navigator. |
| `configFiles` | object | No | Project-level xcconfig files keyed by config name. |
| `attributes` | object | No | Project-level attributes (e.g., `LastUpgradeCheck`). |

### Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bundleIdPrefix` | string | - | Auto-generates bundle IDs as `prefix.targetName` when target omits `PRODUCT_BUNDLE_IDENTIFIER`. |
| `deploymentTarget` | object | - | Default deployment targets per platform, e.g. `{"iOS": "17.0"}`. |
| `groupSortPosition` | string | `"bottom"` | Where groups appear relative to files: `"top"`, `"bottom"`, or `"none"`. |
| `transitivelyLinkDependencies` | bool | `false` | Whether to transitively link dependencies of dependencies. |
| `createIntermediateGroups` | bool | `false` | Create intermediate groups for nested paths in sources. |
| `defaultConfig` | string | first config | Which configuration to use for command-line builds. |

## Target Schema

Each key in `targets` is the target name. The value is an object:

```json
{
  "TargetName": {
    "type": "application",
    "platform": "iOS",
    "deploymentTarget": "17.0",
    "sources": [
      { "path": "Sources" },
      { "path": "Resources", "type": "folder" }
    ],
    "dependencies": [],
    "settings": {},
    "info": {
      "path": "App/Info.plist",
      "properties": {}
    },
    "configFiles": {
      "Debug": "Config/Debug.xcconfig",
      "Release": "Config/Release.xcconfig"
    },
    "entitlements": {
      "path": "App/App.entitlements",
      "properties": {
        "com.apple.security.app-sandbox": true
      }
    },
    "preBuildScripts": [],
    "postBuildScripts": [],
    "scheme": {}
  }
}
```

### Target Keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `type` | string | Yes | Product type. See "Target Types" below. |
| `platform` | string | Yes* | `iOS`, `macOS`, `watchOS`, `tvOS`, or `visionOS`. *Can use `supportedDestinations` instead. |
| `deploymentTarget` | string | No | Minimum OS version, e.g. `"17.0"`. Overrides project-level default. |
| `sources` | array | Yes | Source file paths. Each entry is a string or object with `path` and optional keys. |
| `dependencies` | array | No | Target, package, framework, or SDK dependencies. |
| `settings` | object | No | Build settings for this target. |
| `info` | object | No | Info.plist configuration with `path` and/or `properties`. |
| `configFiles` | object | No | Per-configuration xcconfig files. |
| `entitlements` | object | No | Entitlements with `path` and/or `properties`. |
| `supportedDestinations` | array | No | Multi-platform targets: `["iOS", "macOS", "tvOS", "watchOS", "visionOS", "macCatalyst"]`. |
| `preBuildScripts` | array | No | Scripts to run before building. |
| `postBuildScripts` | array | No | Scripts to run after building. |
| `scheme` | object | No | Inline scheme configuration for this target. |
| `transitivelyLinkDependencies` | bool | No | Override project-level transitive linking for this target. |

### Target Types

| Type | Description |
|------|-------------|
| `application` | App bundle (iOS, macOS, watchOS, tvOS, visionOS) |
| `app-extension` | App extension (share, today, notification, etc.) |
| `app-extension.messages` | iMessage extension |
| `app-extension.intents-service` | Intents extension |
| `bundle.unit-test` | Unit test bundle |
| `bundle.ui-testing` | UI test bundle |
| `framework` | Dynamic framework |
| `framework.static` | Static framework |
| `library.static` | Static library |
| `tv-app-extension` | tvOS app extension |
| `watchkit2-extension` | watchOS app extension (legacy) |
| `widget-extension` | Widget extension (WidgetKit) |

### Source Entry Options

Sources can be simple strings or objects with additional control:

```json
{ "path": "Sources" }
{ "path": "Resources", "type": "folder" }
{ "path": "Generated", "optional": true }
{ "path": "ObjC", "compilerFlags": ["-fno-objc-arc"] }
{ "path": "Sources", "excludes": ["**/*.generated.swift"] }
{ "path": "Sources", "includes": ["**/*.swift"] }
{ "path": "Assets.xcassets", "buildPhase": "resources" }
```

## Dependencies

### Package Dependencies (Swift Package Manager)

First declare the package at the project level, then reference it in targets:

```json
{
  "packages": {
    "Alamofire": {
      "url": "https://github.com/Alamofire/Alamofire.git",
      "from": "5.9.0"
    }
  },
  "targets": {
    "MyApp": {
      "dependencies": [
        { "package": "Alamofire" }
      ]
    }
  }
}
```

Package version specifiers:

```json
{ "url": "...", "from": "1.0.0" }
{ "url": "...", "exactVersion": "1.2.3" }
{ "url": "...", "minVersion": "1.0.0", "maxVersion": "2.0.0" }
{ "url": "...", "branch": "main" }
{ "url": "...", "revision": "abc123" }
```

When a package contains multiple products, specify which one:

```json
{ "package": "Firebase", "product": "FirebaseAuth" }
{ "package": "Firebase", "product": "FirebaseFirestore" }
```

### Local Swift Package Dependencies

```json
{
  "packages": {
    "SharedModels": {
      "path": "Packages/SharedModels"
    }
  },
  "targets": {
    "MyApp": {
      "dependencies": [
        { "package": "SharedModels" }
      ]
    }
  }
}
```

The `path` is relative to the project root. The local package must have a valid `Package.swift`.

### Target Dependencies

Reference another target in the same project:

```json
{ "target": "MyFramework" }
{ "target": "MyFramework", "embed": true }
{ "target": "MyFramework", "embed": false }
```

### Framework and SDK Dependencies

```json
{ "framework": "Vendor/Analytics.xcframework", "embed": true }
{ "sdk": "HealthKit.framework" }
{ "sdk": "libsqlite3.tbd" }
{ "carthage": "Realm", "findFrameworks": true }
```

## Info.plist Configuration

Use `info` to either reference an existing plist or generate one inline:

```json
"info": {
  "path": "App/Info.plist",
  "properties": {
    "CFBundleDisplayName": "My App",
    "CFBundleShortVersionString": "1.0",
    "CFBundleVersion": "1",
    "ITSAppUsesNonExemptEncryption": false,
    "UILaunchScreen": {},
    "UISupportedInterfaceOrientations": [
      "UIInterfaceOrientationPortrait",
      "UIInterfaceOrientationLandscapeLeft",
      "UIInterfaceOrientationLandscapeRight"
    ],
    "NSCameraUsageDescription": "Camera access for photos",
    "UIApplicationSceneManifest": {
      "UIApplicationSupportsMultipleScenes": true
    }
  }
}
```

If only `properties` is specified (no `path`), XcodeGen generates the Info.plist automatically. If only `path` is specified, the existing file is used as-is. If both are specified, `properties` are merged into the file at `path`.

## Entitlements

```json
"entitlements": {
  "path": "App/App.entitlements",
  "properties": {
    "com.apple.security.app-sandbox": true,
    "com.apple.developer.healthkit": true,
    "com.apple.developer.healthkit.access": ["health-records"],
    "aps-environment": "development",
    "com.apple.developer.icloud-container-identifiers": ["iCloud.com.example.app"]
  }
}
```

## Build Scripts

```json
"preBuildScripts": [
  {
    "name": "SwiftLint",
    "script": "swiftlint lint --strict",
    "basedOnDependencyAnalysis": false
  }
],
"postBuildScripts": [
  {
    "name": "Upload dSYMs",
    "script": "\"${PODS_ROOT}/FirebaseCrashlytics/upload-symbols\"",
    "inputFiles": ["$(DWARF_DSYM_FOLDER_PATH)/$(DWARF_DSYM_FILE_NAME)"]
  }
]
```

## Common Patterns

### Widget Extension

```json
{
  "targets": {
    "MyApp": {
      "type": "application",
      "platform": "iOS",
      "dependencies": [
        { "target": "MyWidgetExtension" }
      ]
    },
    "MyWidgetExtension": {
      "type": "widget-extension",
      "platform": "iOS",
      "deploymentTarget": "17.0",
      "sources": [{ "path": "Widget" }],
      "dependencies": [
        { "target": "SharedModels", "embed": false }
      ],
      "settings": {
        "PRODUCT_BUNDLE_IDENTIFIER": "com.example.app.widget",
        "SWIFT_VERSION": "5.0"
      },
      "info": {
        "properties": {
          "CFBundleDisplayName": "My Widget",
          "CFBundleShortVersionString": "1.0",
          "CFBundleVersion": "1",
          "NSExtension": {
            "NSExtensionPointIdentifier": "com.apple.widgetkit-extension"
          }
        }
      }
    }
  }
}
```

### Unit Test Target

```json
"MyAppTests": {
  "type": "bundle.unit-test",
  "platform": "iOS",
  "sources": [{ "path": "Tests" }],
  "dependencies": [
    { "target": "MyApp" }
  ],
  "settings": {
    "PRODUCT_BUNDLE_IDENTIFIER": "com.example.app.tests",
    "TEST_HOST": "$(BUILT_PRODUCTS_DIR)/MyApp.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/MyApp"
  }
}
```

### Multi-Platform Target (supportedDestinations)

```json
"SharedKit": {
  "type": "framework",
  "supportedDestinations": ["iOS", "macOS", "watchOS"],
  "sources": [{ "path": "SharedKit/Sources" }],
  "settings": {
    "PRODUCT_BUNDLE_IDENTIFIER": "com.example.sharedkit"
  }
}
```

## Complete Multi-Target iOS App Example

```json
{
  "name": "WeatherApp",
  "configs": {
    "Debug": "debug",
    "Release": "release"
  },
  "options": {
    "groupSortPosition": "bottom",
    "transitivelyLinkDependencies": false,
    "bundleIdPrefix": "com.example.weatherapp",
    "deploymentTarget": {
      "iOS": "17.0",
      "watchOS": "10.0"
    },
    "createIntermediateGroups": true
  },
  "settings": {
    "DEVELOPMENT_TEAM": "ABCDE12345",
    "CODE_SIGN_STYLE": "Automatic"
  },
  "packages": {
    "Alamofire": {
      "url": "https://github.com/Alamofire/Alamofire.git",
      "from": "5.9.0"
    },
    "WeatherKit": {
      "path": "Packages/WeatherKit"
    }
  },
  "targets": {
    "WeatherApp": {
      "type": "application",
      "platform": "iOS",
      "deploymentTarget": "17.0",
      "sources": [
        { "path": "App" }
      ],
      "dependencies": [
        { "package": "Alamofire" },
        { "package": "WeatherKit" },
        { "target": "WeatherWidgetExtension" }
      ],
      "settings": {
        "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon",
        "ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME": "AccentColor",
        "CURRENT_PROJECT_VERSION": "1",
        "MARKETING_VERSION": "1.0",
        "PRODUCT_BUNDLE_IDENTIFIER": "com.example.weatherapp",
        "PRODUCT_NAME": "$(TARGET_NAME)",
        "SWIFT_VERSION": "5.0"
      },
      "info": {
        "path": "App/Info.plist",
        "properties": {
          "CFBundleDisplayName": "Weather",
          "CFBundleShortVersionString": "1.0",
          "CFBundleVersion": "1",
          "ITSAppUsesNonExemptEncryption": false,
          "UILaunchScreen": {},
          "UISupportedInterfaceOrientations": [
            "UIInterfaceOrientationPortrait",
            "UIInterfaceOrientationLandscapeLeft",
            "UIInterfaceOrientationLandscapeRight"
          ],
          "NSLocationWhenInUseUsageDescription": "We use your location to show local weather."
        }
      },
      "entitlements": {
        "path": "App/App.entitlements",
        "properties": {
          "com.apple.developer.weatherkit": true
        }
      }
    },
    "WeatherWidgetExtension": {
      "type": "widget-extension",
      "platform": "iOS",
      "deploymentTarget": "17.0",
      "sources": [
        { "path": "Widget" }
      ],
      "dependencies": [
        { "package": "WeatherKit" }
      ],
      "settings": {
        "CURRENT_PROJECT_VERSION": "1",
        "MARKETING_VERSION": "1.0",
        "PRODUCT_BUNDLE_IDENTIFIER": "com.example.weatherapp.widget",
        "SWIFT_VERSION": "5.0"
      },
      "info": {
        "properties": {
          "CFBundleDisplayName": "Weather Widget",
          "CFBundleShortVersionString": "1.0",
          "CFBundleVersion": "1",
          "NSExtension": {
            "NSExtensionPointIdentifier": "com.apple.widgetkit-extension"
          }
        }
      }
    },
    "WeatherWatch": {
      "type": "application",
      "platform": "watchOS",
      "deploymentTarget": "10.0",
      "sources": [
        { "path": "WatchApp" }
      ],
      "dependencies": [
        { "package": "WeatherKit" }
      ],
      "settings": {
        "CURRENT_PROJECT_VERSION": "1",
        "MARKETING_VERSION": "1.0",
        "PRODUCT_BUNDLE_IDENTIFIER": "com.example.weatherapp.watch",
        "SWIFT_VERSION": "5.0",
        "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon"
      },
      "info": {
        "properties": {
          "CFBundleDisplayName": "Weather",
          "CFBundleShortVersionString": "1.0",
          "CFBundleVersion": "1",
          "WKApplication": true
        }
      }
    },
    "WeatherAppTests": {
      "type": "bundle.unit-test",
      "platform": "iOS",
      "sources": [
        { "path": "Tests" }
      ],
      "dependencies": [
        { "target": "WeatherApp" }
      ],
      "settings": {
        "PRODUCT_BUNDLE_IDENTIFIER": "com.example.weatherapp.tests",
        "TEST_HOST": "$(BUILT_PRODUCTS_DIR)/WeatherApp.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/WeatherApp"
      }
    }
  }
}
```

## Key Rules

1. **Always use JSON format** -- never YAML. The file must be valid JSON named `Project.json`.
2. **Do not duplicate preset settings** -- XcodeGen applies base, platform, product, and config presets automatically. Only specify settings that override or extend defaults.
3. **`configs` is required** -- always include at least Debug/Release mapped to `"debug"`/`"release"`.
4. **Widget extensions use `widget-extension` type** -- not `app-extension`. The `NSExtension` info property is still needed.
5. **Local packages use `path`**, remote packages use `url` with a version specifier.
6. **Extension bundle IDs must be prefixed** with the host app's bundle ID (e.g., `com.example.app.widget`).
7. **`sources` paths are relative** to the `Project.json` location.
8. **`SWIFT_VERSION` should be set** per target since the base preset only sets `5.0` -- update to match the project's Swift version.
9. **For Bitrig projects**, `PRODUCT_BUNDLE_IDENTIFIER` typically uses the format `app.bitrig.new.<project-uuid>`.
