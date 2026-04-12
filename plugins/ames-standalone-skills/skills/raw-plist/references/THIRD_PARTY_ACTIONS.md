# Third-Party Actions Reference

This file lists third-party actions discovered from:
- macOS Shortcuts ToolKit database (installed apps)
- Local shortcut backup exports

Installed third-party actions (ToolKit): 11

## Third-Party Actions (ToolKit)
- `io.tailscale.ipn.macsys.ConnectIntent`
- `io.tailscale.ipn.macsys.DeviceAppEntity`
- `io.tailscale.ipn.macsys.DisconnectIntent`
- `io.tailscale.ipn.macsys.PingAppIntent`
- `io.tailscale.ipn.macsys.ProfileAppEntity`
- `io.tailscale.ipn.macsys.SetDNSAppIntent`
- `io.tailscale.ipn.macsys.StopUsingExitNodeIntent`
- `io.tailscale.ipn.macsys.SwitchProfileIntent`
- `io.tailscale.ipn.macsys.TaildropAppIntent`
- `io.tailscale.ipn.macsys.ToggleAppIntent`
- `is.workflow.actions.lightroom.import`

Third-party actions referenced in backups: 49

## Third-Party Actions (Backups)
- `betamagic.News-Explorer.mobile.ArticleBySelection`
- `betamagic.News-Explorer.mobile.ArticleEntity`
- `co.montanafloss.Shareshot.FrameScreenshotsIntent`
- `co.zottmann.ActionsForObsidian.CreateNote`
- `co.zottmann.ActionsForObsidian.GetNoteLink`
- `co.zottmann.ActionsForObsidian.SetNoteProperties`
- `com.agiletortoise.Drafts-OSX.CaptureIntent`
- `com.alexhay.ToolboxProForShortcuts.FindAlbumsIntent`
- `com.alexhay.ToolboxProForShortcuts.FindSongsIntent`
- `com.alexhay.ToolboxProForShortcuts.PlayMusicIntent`
- `com.alexhay.nautomate.AddValuesToDatabaseIntent`
- `com.alexhay.nautomate.CreateBookmarkBlockIntent`
- `com.alexhay.nautomate.CreateDividerBlockIntent`
- `com.alexhay.nautomate.CreateListBlockIntent`
- `com.alexhay.nautomate.CreateSmartBlocksFromTextIntent`
- `com.alexhay.nautomate.CreateTextBlockIntent`
- `com.culturedcode.ThingsMac.TAIAddTodo2`
- `com.culturedcode.ThingsMac.TAIItemEntity`
- `com.finnvoorhees.ShortcutButtons.NewButtonForShortcutIntent`
- `com.google.gemini.TypeToGeminiIntent`
- `com.gtrigonakis.TextWorkflow.TransformTextIntent`
- `com.gtrigonakis.TextWorkflowIOS.TransformTextIntent`
- `com.joehribar.toggl.StopTimeEntryIntent`
- `com.lireapp.smilingAlpaca.LIREGetArticleIdentifiersIntent`
- `com.lireapp.smilingAlpaca.LIREGetArticlePropertyIntent`
- `com.lireapp.smilingAlpaca.LIREGetCurrentArticleIdentifierIntent`
- `com.ngocluu.goodlinks.AddLinkIntent`
- `com.ngocluu.goodlinks.AddTags`
- `com.ngocluu.goodlinks.GetCurrentLink`
- `com.ngocluu.goodlinks.GetCurrentSelection`
- `com.ngocluu.goodlinks.GetTagsIntent`
- `com.ngocluu.goodlinks.HighlightEntity`
- `com.ngocluu.goodlinks.LinkEntity`
- `com.ngocluu.goodlinks.OpenHighlight`
- `com.ngocluu.goodlinks.OpenLinkIntent`
- `com.openai.chat.OpenVoiceModeIntent`
- `com.sindresorhus.AI-Actions.AskClaudeIntent`
- `com.sindresorhus.Actions.GenerateUUIDIntent`
- `com.sindresorhus.Actions.GetAudioPlaybackDestinationIntent`
- `com.sindresorhus.Actions.GetFilePathIntent`
- `com.sindresorhus.Actions.GetTitleOfURLIntent`
- `com.sindresorhus.Actions.TruncateNumber`
- `com.sindresorhus.Shortcutie.SetDefaultSoundDevice`
- `com.todoist.ios.OpenRambleAppIntent`
- `dk.simonbs.Jayson.ViewJSONIntent`
- `net.matrixteo.app.Collections.IntentsAddArrayValue`
- `net.matrixteo.app.Collections.IntentsAddDocument`
- `net.matrixteo.app.Collections.IntentsDocumentEntity`
- `net.matrixteo.app.Collections.IntentsUpdateValue`

Notes:
- Backup-only entries may come from apps not installed on this Mac.
- WF-style third-party actions can still use the `is.workflow.actions.*` prefix (e.g., Lightroom).

## Tailscale Device Picker Pattern

Use `io.tailscale.ipn.ios.DeviceAppEntity` (iOS app) — NOT the `macsys` variant above (that's the macOS system extension). Confirmed working pattern from `Claude Code Remote` shortcut:

```python
# 1. Find Tailscale devices
{"WFWorkflowActionIdentifier": "io.tailscale.ipn.ios.DeviceAppEntity",
 "WFWorkflowActionParameters": {
   "UUID": U_ts,
   "AppIntentDescriptor": {
     "TeamIdentifier": "W5364U7YZB",
     "BundleIdentifier": "io.tailscale.ipn.ios",
     "Name": "Tailscale",
     "AppIntentIdentifier": "DeviceAppEntity",
     "ActionRequiresAppInstallation": True
   }
 }}

# 2. User picks a device
{"WFWorkflowActionIdentifier": "is.workflow.actions.choosefromlist",
 "WFWorkflowActionParameters": {"UUID": U_ts_pick, "WFInput": action_ref(U_ts, "Devices")}}

# 3. Extract IPv4 address via aggrandizement
{"WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
 "WFWorkflowActionParameters": {
   "WFInput": {
     "Value": {
       "OutputUUID": U_ts_pick, "Type": "ActionOutput", "OutputName": "Selected Item",
       "Aggrandizements": [{
         "PropertyUserInfo": {"WFLinkEntityContentPropertyUserInfoPropertyIdentifier": "ipv4Address"},
         "Type": "WFPropertyVariableAggrandizement",
         "PropertyName": "ipv4Address"
       }]
     },
     "WFSerializationType": "WFTextTokenAttachment"
   },
   "WFVariableName": "Remote Mac IP"
 }}
```

Then use `var_ref("Remote Mac IP")` / `text_with_var("\ufffc", "{0, 1}", var_name="Remote Mac IP")` for `WFSSHHost` in `is.workflow.actions.runsshscript`.
