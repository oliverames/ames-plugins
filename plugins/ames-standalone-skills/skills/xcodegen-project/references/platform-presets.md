# XcodeGen Setting Presets Reference

These are the built-in setting presets that XcodeGen applies automatically when generating Xcode projects. They are sourced from the Bitrig-bundled XcodeGen at `/Applications/Bitrig.app/Contents/Resources/XcodeGen_XcodeGenKit.bundle/Contents/Resources/SettingPresets/`. You do not need to manually set any of these values in `Project.json` unless you want to override them.

Presets are layered in this order: **base** -> **config (debug/release)** -> **platform** -> **product type** -> **product+platform combination** -> **supportedDestinations**. Later layers override earlier ones.

---

## Base Preset (`base.yml`)

Applied to every target in every project.

```yaml
ALWAYS_SEARCH_USER_PATHS: NO
CLANG_ANALYZER_NONNULL: YES
CLANG_ANALYZER_NUMBER_OBJECT_CONVERSION: YES_AGGRESSIVE
CLANG_CXX_LANGUAGE_STANDARD: gnu++14
CLANG_CXX_LIBRARY: libc++
CLANG_ENABLE_MODULES: YES
CLANG_ENABLE_OBJC_ARC: YES
CLANG_ENABLE_OBJC_WEAK: YES
CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING: YES
CLANG_WARN_BOOL_CONVERSION: YES
CLANG_WARN_COMMA: YES
CLANG_WARN_CONSTANT_CONVERSION: YES
CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS: YES
CLANG_WARN_DIRECT_OBJC_ISA_USAGE: YES_ERROR
CLANG_WARN_DOCUMENTATION_COMMENTS: YES
CLANG_WARN_EMPTY_BODY: YES
CLANG_WARN_ENUM_CONVERSION: YES
CLANG_WARN_INFINITE_RECURSION: YES
CLANG_WARN_INT_CONVERSION: YES
CLANG_WARN_NON_LITERAL_NULL_CONVERSION: YES
CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF: YES
CLANG_WARN_OBJC_LITERAL_CONVERSION: YES
CLANG_WARN_OBJC_ROOT_CLASS: YES_ERROR
CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER: YES
CLANG_WARN_RANGE_LOOP_ANALYSIS: YES
CLANG_WARN_STRICT_PROTOTYPES: YES
CLANG_WARN_SUSPICIOUS_MOVE: YES
CLANG_WARN_UNGUARDED_AVAILABILITY: YES_AGGRESSIVE
CLANG_WARN_UNREACHABLE_CODE: YES
CLANG_WARN__DUPLICATE_METHOD_MATCH: YES
COPY_PHASE_STRIP: NO
ENABLE_STRICT_OBJC_MSGSEND: YES
GCC_C_LANGUAGE_STANDARD: gnu11
GCC_NO_COMMON_BLOCKS: YES
GCC_WARN_64_TO_32_BIT_CONVERSION: YES
GCC_WARN_ABOUT_RETURN_TYPE: YES_ERROR
GCC_WARN_UNDECLARED_SELECTOR: YES
GCC_WARN_UNINITIALIZED_AUTOS: YES_AGGRESSIVE
GCC_WARN_UNUSED_FUNCTION: YES
GCC_WARN_UNUSED_VARIABLE: YES
MTL_FAST_MATH: YES
PRODUCT_NAME: $(TARGET_NAME)
SWIFT_VERSION: '5.0'
```

---

## Config Presets

### Debug (`Configs/debug.yml`)

Applied when a configuration maps to `"debug"`.

```yaml
DEBUG_INFORMATION_FORMAT: dwarf
ENABLE_TESTABILITY: YES
GCC_DYNAMIC_NO_PIC: NO
GCC_OPTIMIZATION_LEVEL: '0'
GCC_PREPROCESSOR_DEFINITIONS: ["$(inherited)", "DEBUG=1"]
MTL_ENABLE_DEBUG_INFO: INCLUDE_SOURCE
ONLY_ACTIVE_ARCH: YES
SWIFT_ACTIVE_COMPILATION_CONDITIONS: DEBUG
SWIFT_OPTIMIZATION_LEVEL: -Onone
```

### Release (`Configs/release.yml`)

Applied when a configuration maps to `"release"`.

```yaml
DEBUG_INFORMATION_FORMAT: dwarf-with-dsym
ENABLE_NS_ASSERTIONS: NO
MTL_ENABLE_DEBUG_INFO: NO
SWIFT_COMPILATION_MODE: wholemodule
SWIFT_OPTIMIZATION_LEVEL: -O
```

---

## Platform Presets

### iOS (`Platforms/iOS.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks"]
SDKROOT: iphoneos
TARGETED_DEVICE_FAMILY: '1,2'
```

### macOS (`Platforms/macOS.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/../Frameworks"]
SDKROOT: macosx
COMBINE_HIDPI_IMAGES: 'YES'
```

### watchOS (`Platforms/watchOS.yml`)

```yaml
SDKROOT: watchos
SKIP_INSTALL: 'YES'
TARGETED_DEVICE_FAMILY: 4
```

### tvOS (`Platforms/tvOS.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks"]
SDKROOT: appletvos
TARGETED_DEVICE_FAMILY: 3
```

### visionOS (`Platforms/visionOS.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks"]
SDKROOT: xros
TARGETED_DEVICE_FAMILY: 7
```

---

## Product Type Presets

### Application (`Products/` -- no product-level preset)

No additional product-level settings for applications. Platform-specific application settings are in the Product+Platform section below.

### App Extension (`Products/app-extension.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks", "@executable_path/../../Frameworks"]
```

### App Extension - Intents Service (`Products/app-extension.intents-service.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks", "@executable_path/../../Frameworks", "@executable_path/../../../../Frameworks"]
```

### App Extension - Messages (`Products/app-extension.messages.yml`)

```yaml
ASSETCATALOG_COMPILER_APPICON_NAME: iMessage App Icon
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks", "@executable_path/../../Frameworks"]
```

### Unit Test Bundle (`Products/bundle.unit-test.yml`)

```yaml
BUNDLE_LOADER: $(TEST_HOST)
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks", "@loader_path/Frameworks"]
```

### UI Testing Bundle (`Products/bundle.ui-testing.yml`)

```yaml
BUNDLE_LOADER: $(TEST_HOST)
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks", "@loader_path/Frameworks"]
```

### Framework (`Products/framework.yml`)

```yaml
CURRENT_PROJECT_VERSION: 1
DEFINES_MODULE: 'YES'
CODE_SIGN_IDENTITY: ""
DYLIB_COMPATIBILITY_VERSION: 1
DYLIB_CURRENT_VERSION: 1
VERSIONING_SYSTEM: "apple-generic"
INSTALL_PATH: "$(LOCAL_LIBRARY_DIR)/Frameworks"
DYLIB_INSTALL_NAME_BASE: "@rpath"
SKIP_INSTALL: 'YES'
```

### Static Framework (`Products/framework.static.yml`)

```yaml
CURRENT_PROJECT_VERSION: 1
DEFINES_MODULE: 'YES'
CODE_SIGN_IDENTITY: ""
DYLIB_COMPATIBILITY_VERSION: 1
DYLIB_CURRENT_VERSION: 1
VERSIONING_SYSTEM: "apple-generic"
INSTALL_PATH: "$(LOCAL_LIBRARY_DIR)/Frameworks"
DYLIB_INSTALL_NAME_BASE: "@rpath"
SKIP_INSTALL: 'YES'
```

### Static Library (`Products/library.static.yml`)

```yaml
SKIP_INSTALL: 'YES'
```

### TV App Extension (`Products/tv-app-extension.yml`)

```yaml
SKIP_INSTALL: 'YES'
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks", "@executable_path/../../Frameworks"]
```

### WatchKit 2 Extension (`Products/watchkit2-extension.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/Frameworks", "@executable_path/../../Frameworks"]
ASSETCATALOG_COMPILER_COMPLICATION_NAME: Complication
```

---

## Product + Platform Presets

These are applied when a specific product type is combined with a specific platform.

### Application - iOS (`Product_Platform/application_iOS.yml`)

```yaml
CODE_SIGN_IDENTITY: iPhone Developer
ASSETCATALOG_COMPILER_APPICON_NAME: AppIcon
```

### Application - macOS (`Product_Platform/application_macOS.yml`)

```yaml
ASSETCATALOG_COMPILER_APPICON_NAME: AppIcon
```

### Application - tvOS (`Product_Platform/application_tvOS.yml`)

```yaml
ASSETCATALOG_COMPILER_APPICON_NAME: App Icon & Top Shelf Image
ASSETCATALOG_COMPILER_LAUNCHIMAGE_NAME: LaunchImage
```

### Application - visionOS (`Product_Platform/application_visionOS.yml`)

```yaml
ASSETCATALOG_COMPILER_APPICON_NAME: AppIcon
```

### Application - watchOS (`Product_Platform/application_watchOS.yml`)

```yaml
ASSETCATALOG_COMPILER_APPICON_NAME: AppIcon
```

### App Extension - macOS (`Product_Platform/app-extension_macOS.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/../Frameworks", "@executable_path/../../../../Frameworks"]
```

### Unit Test Bundle - macOS (`Product_Platform/bundle.unit-test_macOS.yml`)

```yaml
LD_RUNPATH_SEARCH_PATHS: ["$(inherited)", "@executable_path/../Frameworks", "@loader_path/../Frameworks"]
```

---

## Supported Destinations Presets

Used when a target specifies `supportedDestinations` instead of a single `platform`. These configure multi-platform support.

### iOS (`SupportedDestinations/iOS.yml`)

```yaml
SUPPORTED_PLATFORMS: iphoneos iphonesimulator
TARGETED_DEVICE_FAMILY: '1,2'
SUPPORTS_MACCATALYST: NO
SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD: YES
SUPPORTS_XR_DESIGNED_FOR_IPHONE_IPAD: YES
```

### macOS (`SupportedDestinations/macOS.yml`)

```yaml
SUPPORTED_PLATFORMS: macosx
SUPPORTS_MACCATALYST: NO
SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD: NO
```

### macCatalyst (`SupportedDestinations/macCatalyst.yml`)

```yaml
SUPPORTS_MACCATALYST: YES
SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD: NO
```

### tvOS (`SupportedDestinations/tvOS.yml`)

```yaml
SUPPORTED_PLATFORMS: appletvos appletvsimulator
TARGETED_DEVICE_FAMILY: '3'
```

### visionOS (`SupportedDestinations/visionOS.yml`)

```yaml
SUPPORTED_PLATFORMS: xros xrsimulator
TARGETED_DEVICE_FAMILY: '7'
SUPPORTS_XR_DESIGNED_FOR_IPHONE_IPAD: NO
```

### watchOS (`SupportedDestinations/watchOS.yml`)

```yaml
SUPPORTED_PLATFORMS: watchos watchsimulator
TARGETED_DEVICE_FAMILY: '4'
```
