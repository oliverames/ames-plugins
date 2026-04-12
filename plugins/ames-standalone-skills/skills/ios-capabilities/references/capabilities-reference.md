# iOS Capabilities Reference

Complete lookup table of all iOS capabilities, their Info.plist keys, entitlements, and default purpose strings. Sourced from Bitrig's Capabilities.plist.

## Capabilities Table

| # | Capability | Key | SF Symbol | Info.plist Keys | Entitlements | Default Purpose String |
|---|-----------|-----|-----------|----------------|-------------|----------------------|
| 1 | Location | `location` | `location` | `NSLocationWhenInUseUsageDescription`, `NSLocationAlwaysAndWhenInUseUsageDescription` | -- | This app uses your location to provide location-based features. |
| 2 | Motion | `motion` | `gyroscope` | `NSMotionUsageDescription` | -- | This app uses motion data to track your activity. |
| 3 | Camera | `camera` | `camera` | `NSCameraUsageDescription` | -- | This app uses the camera to capture photos and videos. |
| 4 | Photo Library | `photo_library` | `photo` | `NSPhotoLibraryUsageDescription` | -- | This app accesses your photo library to save and select photos. |
| 5 | Photo Library (Add Only) | `photo_library_add` | `photo.badge.plus` | `NSPhotoLibraryAddUsageDescription` | -- | This app saves photos to your photo library. |
| 6 | Media Library | `media_library` | `music.note.list` | `NSAppleMusicUsageDescription` | -- | This app accesses your media library to play music and media. |
| 7 | Microphone | `microphone` | `mic` | `NSMicrophoneUsageDescription` | -- | This app uses the microphone to record audio. |
| 8 | Speech Recognition | `speech_recognition` | `waveform` | `NSSpeechRecognitionUsageDescription` | -- | This app uses speech recognition to convert speech to text. |
| 9 | Bluetooth | `bluetooth` | `antenna.radiowaves.left.and.right` | `NSBluetoothAlwaysUsageDescription` | -- | This app uses Bluetooth to connect to nearby devices. |
| 10 | Contacts | `contacts` | `person.crop.circle` | `NSContactsUsageDescription` | -- | This app accesses your contacts to provide contact-based features. |
| 11 | Calendar | `calendar` | `calendar` | `NSCalendarsFullAccessUsageDescription` | -- | This app accesses your calendar to read and write events. |
| 12 | Calendar (Write Only) | `calendar_write` | `calendar.badge.plus` | `NSCalendarsWriteOnlyAccessUsageDescription` | -- | This app creates calendar events. |
| 13 | Reminders | `reminders` | `checklist` | `NSRemindersFullAccessUsageDescription` | -- | This app accesses your reminders to read and write tasks. |
| 14 | Face ID | `face_id` | `faceid` | `NSFaceIDUsageDescription` | -- | This app uses Face ID to authenticate you securely. |
| 15 | Health (Read) | `health_read` | `heart.text.square` | `NSHealthShareUsageDescription` | `com.apple.developer.healthkit`: `true` | This app reads your health data to provide health-related features. |
| 16 | Health (Write) | `health_write` | `heart.text.square.fill` | `NSHealthUpdateUsageDescription` | `com.apple.developer.healthkit`: `true` | This app saves health data to track your fitness and wellness. |
| 17 | Health Clinical Records | `health_clinical_records` | `cross.case` | `NSHealthClinicalHealthRecordsShareUsageDescription` | `com.apple.developer.healthkit`: `true`, `com.apple.developer.healthkit.access`: `["health-records"]` | This app reads your clinical health records. |
| 18 | HomeKit | `homekit` | `apple.homekit` | `NSHomeKitUsageDescription` | `com.apple.developer.homekit`: `true` | This app accesses your home configuration to control smart home devices. |
| 19 | Local Network | `local_network` | `network` | `NSLocalNetworkUsageDescription` | -- | This app uses the local network to discover and communicate with nearby devices. |
| 20 | Nearby Interaction | `nearby_interaction` | `dot.radiowaves.left.and.right` | `NSNearbyInteractionUsageDescription` | -- | This app uses Nearby Interaction to determine the position of nearby devices. |
| 21 | NFC | `nfc` | `wave.3.right` | `NFCReaderUsageDescription` | `com.apple.developer.nfc.readersession.formats`: `["NDEF", "TAG"]` | This app uses NFC to read tags and interact with NFC-enabled devices. |
| 22 | Siri | `siri` | `siri` | `NSSiriUsageDescription` | `com.apple.developer.siri`: `true` | This app uses Siri to provide voice-activated features and shortcuts. |
| 23 | User Tracking | `user_tracking` | `person.badge.shield.checkmark` | `NSUserTrackingUsageDescription` | -- | This app uses tracking to provide personalized ads and measure ad effectiveness. |
| 24 | TV Provider | `tv_provider` | `tv` | `NSVideoSubscriberAccountUsageDescription` | -- | This app uses your TV provider account to unlock premium content. |
| 25 | Game Center Friends | `game_center_friends` | `gamecontroller` | `NSGKFriendListUsageDescription` | -- | This app accesses your Game Center friends to enable multiplayer features. |
| 26 | Fall Detection | `fall_detection` | `figure.fall` | `NSFallDetectionUsageDescription` | -- | This app accesses fall detection data to monitor your safety. |
| 27 | Wallet Identity | `wallet_identity` | `wallet.pass` | `NSIdentityUsageDescription` | -- | This app reads your identity information from Wallet for verification. |
| 28 | Financial Data | `financial_data` | `creditcard` | `NSFinancialDataUsageDescription` | -- | This app accesses your financial data from Wallet. |
| 29 | World Sensing | `world_sensing` | `arkit` | `NSWorldSensingUsageDescription` | -- | This app uses augmented reality to detect surfaces and track objects in your environment. |
| 30 | Hand Tracking | `hand_tracking` | `hand.raised.fingers.spread.fill` | `NSHandsTrackingUsageDescription` | -- | This app tracks your hand movements to enable gesture-based interactions. |
| 31 | Accessory Tracking | `accessory_tracking` | `headphones` | `NSAccessoryTrackingUsageDescription` | -- | This app tracks the position of your accessories. |
| 32 | Sensor Kit | `sensor_kit` | `waveform.path.ecg` | `NSSensorKitUsageDescription` | -- | This app collects sensor data as part of a research study. |

## Quick Lookup by Info.plist Key

| Info.plist Key | Capability |
|---------------|-----------|
| `NSAccessoryTrackingUsageDescription` | Accessory Tracking |
| `NSAppleMusicUsageDescription` | Media Library |
| `NSBluetoothAlwaysUsageDescription` | Bluetooth |
| `NSCalendarsFullAccessUsageDescription` | Calendar |
| `NSCalendarsWriteOnlyAccessUsageDescription` | Calendar (Write Only) |
| `NSCameraUsageDescription` | Camera |
| `NSContactsUsageDescription` | Contacts |
| `NSFaceIDUsageDescription` | Face ID |
| `NSFallDetectionUsageDescription` | Fall Detection |
| `NSFinancialDataUsageDescription` | Financial Data |
| `NSGKFriendListUsageDescription` | Game Center Friends |
| `NSHandsTrackingUsageDescription` | Hand Tracking |
| `NSHealthClinicalHealthRecordsShareUsageDescription` | Health Clinical Records |
| `NSHealthShareUsageDescription` | Health (Read) |
| `NSHealthUpdateUsageDescription` | Health (Write) |
| `NSHomeKitUsageDescription` | HomeKit |
| `NSIdentityUsageDescription` | Wallet Identity |
| `NSLocalNetworkUsageDescription` | Local Network |
| `NSLocationAlwaysAndWhenInUseUsageDescription` | Location |
| `NSLocationWhenInUseUsageDescription` | Location |
| `NSMicrophoneUsageDescription` | Microphone |
| `NSMotionUsageDescription` | Motion |
| `NSNearbyInteractionUsageDescription` | Nearby Interaction |
| `NSPhotoLibraryAddUsageDescription` | Photo Library (Add Only) |
| `NSPhotoLibraryUsageDescription` | Photo Library |
| `NSRemindersFullAccessUsageDescription` | Reminders |
| `NSSensorKitUsageDescription` | Sensor Kit |
| `NSSiriUsageDescription` | Siri |
| `NSSpeechRecognitionUsageDescription` | Speech Recognition |
| `NSUserTrackingUsageDescription` | User Tracking |
| `NSVideoSubscriberAccountUsageDescription` | TV Provider |
| `NSWorldSensingUsageDescription` | World Sensing |
| `NFCReaderUsageDescription` | NFC |

## Entitlements Summary

Only these capabilities require entitlements in addition to Info.plist keys:

| Capability | Entitlement Key | Value |
|-----------|----------------|-------|
| Health (Read) | `com.apple.developer.healthkit` | `true` |
| Health (Write) | `com.apple.developer.healthkit` | `true` |
| Health Clinical Records | `com.apple.developer.healthkit` | `true` |
| Health Clinical Records | `com.apple.developer.healthkit.access` | `["health-records"]` |
| HomeKit | `com.apple.developer.homekit` | `true` |
| NFC | `com.apple.developer.nfc.readersession.formats` | `["NDEF", "TAG"]` |
| Siri | `com.apple.developer.siri` | `true` |
