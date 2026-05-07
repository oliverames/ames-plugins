---
name: testflight-deployment
description: >-
  Automates iOS app deployment to TestFlight with GitHub Actions, manual
  approval gates, and environment protection. Use proactively any time an
  iOS project needs a deployment pipeline.
when_to_use: >-
  Deploying an iOS app to TestFlight, setting up an iOS CI/CD pipeline,
  distributing a build to beta testers, automating iOS app releases via
  GitHub Actions, or troubleshooting App Store Connect uploads and code
  signing errors. Also triggers for "deploy my app", "upload to
  TestFlight", "set up TestFlight CI/CD", "configure code signing for
  GitHub Actions", "write ExportOptions.plist", "base64 encode a
  certificate", "add a manual approval gate", "provisioning profile
  error", "App Store Connect upload failed", or any task involving
  automating the iOS build-sign-upload workflow.
---

# TestFlight Deployment via GitHub Actions

Automate iOS app deployment to TestFlight with GitHub Actions, manual approval, and environment protection.

## Quick Reference

1. Encode `.p12`, `.mobileprovision`, `.p8` as base64 and push as GitHub secrets
2. Add `ci/ExportOptions.plist` to the repo
3. Create `.github/workflows/deploy-to-testflight.yml`
4. Configure `testflight` environment with manual approval (GitHub web UI or API)
5. Trigger via `workflow_dispatch` or tag push, approve, and monitor

## Prerequisites

Required files (obtain from Apple Developer portal):
- Distribution certificate (`.p12`) + password
- App Store provisioning profile (`.mobileprovision`)
- App Store Connect API key (`.p8`) + Key ID + Issuer ID
- Team ID

## 1. Encode and Set GitHub Secrets

```bash
# Encode signing assets
CERT_BASE64=$(base64 -i cert.p12)
PROFILE_BASE64=$(base64 -i YourApp_AppStore.mobileprovision)
API_KEY=$(cat AuthKey_XXXXXXXXXX.p8)

# Push secrets to repo
gh secret set IOS_DISTRIBUTION_P12_BASE64 -b"$CERT_BASE64"
gh secret set IOS_DISTRIBUTION_P12_PASSWORD -b"your-password"
gh secret set IOS_PROVISIONING_PROFILE_BASE64 -b"$PROFILE_BASE64"
gh secret set APP_STORE_CONNECT_ISSUER_ID -b"YOUR_ISSUER_ID"
gh secret set APP_STORE_CONNECT_KEY_ID -b"YOUR_KEY_ID"
gh secret set APP_STORE_CONNECT_PRIVATE_KEY -b"$API_KEY"
```

## 2. ExportOptions.plist

Place at `ci/ExportOptions.plist` in the repo:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>method</key>
  <string>app-store</string>
  <key>signingStyle</key>
  <string>manual</string>
  <key>teamID</key>
  <string>YOUR_TEAM_ID</string>
  <key>provisioningProfiles</key>
  <dict>
    <key>com.your.bundleid</key>
    <string>YourApp_AppStore</string>
  </dict>
</dict>
</plist>
```

## 3. GitHub Actions Workflow

Save as `.github/workflows/deploy-to-testflight.yml`:

```yaml
name: Deploy to TestFlight

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version number'
        required: true
      build-number:
        description: 'Build number'
        required: true
  push:
    tags:
      - "v*"

jobs:
  deploy:
    runs-on: macos-latest
    environment: testflight

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Select Xcode version
        # Pin to the Xcode version your project requires; update as needed
        run: sudo xcode-select -s /Applications/Xcode_16.2.app/Contents/Developer

      - name: Import code-signing certs
        uses: Apple-Actions/import-codesign-certs@v6
        with:
          p12-file-base64: ${{ secrets.IOS_DISTRIBUTION_P12_BASE64 }}
          p12-password: ${{ secrets.IOS_DISTRIBUTION_P12_PASSWORD }}

      - name: Install provisioning profile
        run: |
          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
          echo "${{ secrets.IOS_PROVISIONING_PROFILE_BASE64 }}" | base64 --decode > ~/Library/MobileDevice/Provisioning\ Profiles/profile.mobileprovision

      - name: Archive app
        run: |
          xcodebuild \
            -workspace YourApp.xcworkspace \
            -scheme YourApp \
            -configuration Release \
            -sdk iphoneos \
            -archivePath "$PWD/build/YourApp.xcarchive" \
            clean archive

      - name: Export IPA
        run: |
          xcodebuild -exportArchive \
            -archivePath "$PWD/build/YourApp.xcarchive" \
            -exportPath "$PWD/build" \
            -exportOptionsPlist "$PWD/ci/ExportOptions.plist"

      - name: Upload to TestFlight
        uses: Apple-Actions/upload-testflight-build@v1
        with:
          app-path: build/YourApp.ipa
          issuer-id: ${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}
          api-key-id: ${{ secrets.APP_STORE_CONNECT_KEY_ID }}
          api-private-key: ${{ secrets.APP_STORE_CONNECT_PRIVATE_KEY }}
```

## 4. Environment Protection

Configure the `testflight` environment in **Settings > Environments** on GitHub (recommended), or via API:

```bash
# Create environment with manual approval (requires reviewer user ID, not username)
gh api --method PUT "repos/{owner}/{repo}/environments/testflight" \
  --input - <<'EOF'
{
  "reviewers": [{"type": "User", "id": YOUR_GITHUB_USER_ID}],
  "deployment_branch_policy": {"protected_branches": true, "custom_branch_policies": false}
}
EOF
```

To find your user ID: `gh api user --jq '.id'`

## 5. Trigger and Approve

```bash
# Manual trigger
gh workflow run deploy-to-testflight.yml \
  -f version=1.0.0 \
  -f build-number=42

# Or tag-based trigger
git tag v1.0.0 && git push origin v1.0.0

# List pending deployments
gh run list --environment=testflight --status=waiting

# Approve
gh run approve RUN_ID --environment=testflight

# Monitor
gh run watch RUN_ID
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No matching provisioning profiles | Profile name in ExportOptions.plist must match exactly |
| Code signing certificate not found | Verify .p12 base64 encoding and password are correct |
| `errSecInternalComponent` | Keychain is locked in CI; `import-codesign-certs` action should handle this -- verify it ran successfully |
| App Store Connect API key invalid | Regenerate key in App Store Connect, update secret |
| `ITMS-90189` redundant binary upload | Build number already exists; increment build number |
| `ITMS-90046` invalid Code Signing | Certificate/profile mismatch; ensure both match the same team and bundle ID |
| Upload timeout on large IPA | Network issue on runner; retry the job or split build/upload into separate jobs |
| Xcode version mismatch on runner | Add `xcode-select` step pinning to the version you need |
| Environment protection blocked | Approve via `gh run approve RUN_ID --environment=testflight` |
