# Best Practices (Required)

These guidelines are mandatory for every shortcut built with this skill. If guidance in other docs appears to conflict, this file is the source of truth.

## APIs

- Use your best available web search and page-fetch tools to research official API docs before building requests (for example, SerpAPI + Firecrawl when available).
- For complex or unfamiliar external APIs, verify auth, endpoints, parameters, and payload formats against the latest official docs before drafting request actions.
- Verify endpoints, parameters, and payload formats against the official documentation.
- If the URL is static, set it directly in **Get Contents of URL** (`WFURL`). If it needs variables or query parameters, build the URL in a **URL/Text** action with tokenized placeholders and pass it into **Get Contents of URL**.
- Store API tokens in Text actions; add a Comment with a link to the service's API key page before token use.
- Never hardcode real credentials/tokens in shell snippets, examples, logs, or transcripts. Use env vars or credential placeholders.
- Do not load API tokens from files unless the user explicitly asks. If you must read from a file, add a Comment containing `ALLOW_TOKEN_FILE` and explain why.
- For file uploads, use the API's official direct upload method. Do **not** upload to third-party CDNs unless the user explicitly asks.
- Do not add third-party services, extra import questions, or hidden dependencies unless the user explicitly requests them.
- For Notion uploads, use the `file_uploads` endpoints and `file_upload` block type by default; avoid `external` image blocks unless the user provides a URL.
- Sanity-check API strings for obvious gaps before output: no `//` in URLs beyond the protocol, and no empty JSON fields where variables are expected (e.g., `equals:""`, `id:""`, `url:""`, `filename:""`).
- For endpoints with path parameters (e.g., `/tasks/{id}`), ensure the variable placeholder is present immediately after the trailing slash.
- When a request URL includes user input, ensure the **Ask for Input** variable is inserted into the query string; never leave blank query parameters.
- For Authorization headers, use `Basic {base64(user:pass)}` or `Bearer {token}` as required by the API.
- After **Get Contents of URL**, parse structured responses with **Detect Dictionary** and **Get Dictionary Value** (dot notation for nested keys) instead of string parsing; guard optional parents before reading nested keys (for example, do not call `error.message` directly before checking `error` exists).
- JSON booleans extracted via **Detect Dictionary** + **Get Dictionary Value** are often coerced to numeric `1`/`0` in Shortcuts, not string `true`/`false`; do not use string checks like `Contains "true"` on those values.
- For API boolean branching, prefer numeric conditions (`Is Greater Than 0` or `Equals 1`) or normalize through a **Text** action and compare to `"1"`/`"0"`.
- JSON `null` values are coerced to empty/nothing in Shortcuts; do not compare to the string `"null"` and always guard optional fields before branching.
- For JSON API responses, keep `ShowHeaders` disabled unless explicitly needed; if enabled, account for changed output shape before dictionary extraction.
- For JSON request bodies, use `WFJSONValues` for flat key/value payloads so the body is preserved in the Shortcuts editor.
- If `WFJSONValues` renders as `Number 0`, empty rows, or otherwise mangles nested objects/arrays, fall back to a JSON Text action and connect it via `WFRequestVariable`.
- When using JSON Text + `WFRequestVariable`, set the request body type to **File** and keep `Content-Type: application/json` so the variable is visible (especially on iOS).
- Never leave orphan JSON/Text actions: every JSON Text must be the `WFRequestVariable` of a request, or be removed.
- Do not inject raw Dictionary/List action outputs directly into JSON Text templates (for example, API `content` arrays). Shortcuts can stringify them as newline-separated pseudo-JSON that fails `Detect Dictionary`.
- When appending to JSON arrays with **Replace Text** (`\]$`), always include the closing `]` in `WFReplaceTextReplace`; omitting it silently corrupts continuation payloads.
- When interpolating user/assistant freeform text into JSON Text templates, sanitize it first (replace backslashes, normalize/escape newlines and tabs, and handle `"` safely) before insertion.
- For multipart form uploads, file fields must use `WFTokenAttachmentParameterState` with an inner `WFTextTokenAttachment` so the file variable shows in the UI.
- When using **Get Name** for file uploads, append the proper extension in the JSON payload (e.g., `.png`) instead of relying on the base name alone.
- For file names, set **Get Web Page Title** to **Off** in **Get Name** so the action returns the file name, not a URL title.

## Actions

- Prefer default, first-party Apple actions unless the user explicitly requests third-party actions.
- Use modern, non-deprecated Shortcuts actions.
- Always set shortcut icon metadata using `scripts/select_shortcut_icon_color.py` and write both `WFWorkflowIconGlyphNumber` + `WFWorkflowIconStartColor`.
- If the user explicitly requests an icon/color, honor it (name, synonym, glyph number, integer value, or hex); if not requested, infer from the prompt.
- Add Comment actions before major blocks, loops, and functional sections to explain intent.
- **Comment discipline is mandatory**: always include the first two Comment actions, plus section comments. For any control‑flow start (Repeat/If/Menu), the immediately preceding action must be a Comment with a short bulleted wiring list (lines starting with `-` or `•`). Do not skip descriptive comments.
- Never use vCard/VCF list formatting unless the user explicitly requests it. Prefer dictionaries + **Choose from List** or plain lists. If vCard is required, add a Comment containing `ALLOW_VCARD`.
- If a parameter cannot be filled confidently, leave it empty **only if safe**, add a Comment explaining the gap, and tell the user in your response.
- Before final output, validate every `WFTextTokenString`: each `attachmentsByRange` key must point to a `￼` placeholder and the counts must match.
- When editing text templates, re-check `attachmentsByRange` offsets; a single character change can break variable insertion.
- Before final output, scan for actions that **require input** and ensure required input keys are wired to a variable/action output (not an empty string). Common offenders: **Get URLs from Input** (`is.workflow.actions.detect.link`), **Open URL**, **Choose from List**, **Get Dictionary Value**, **Convert Image**, **Base64 Encode/Decode**, **Get Detail of Weather Conditions**, **Get Time Between Dates**, **Extract Text from Image**, and **Replace Text**.
- For **Get URLs from Input** (`is.workflow.actions.detect.link`), set `WFInput` as a `WFTextTokenString` with a `￼` placeholder (not a bare `WFTextTokenAttachment`) to keep the editor field visible.
- For **Convert Image** (`is.workflow.actions.image.convert`), always set explicit `WFInput` to the image/media output.
- For **Base64 Encode/Decode** (`is.workflow.actions.base64encode`), always set an explicit `WFInput`; do not rely on implicit previous-action input.
- For **Get Detail of Weather Conditions** (`is.workflow.actions.properties.weather.conditions`), set both `WFInput` and `WFContentItemPropertyName` (for example, `Sunrise Date`).
- For **Get Time Between Dates** (`is.workflow.actions.gettimebetweendates`), set `WFInput` and **exactly one** non-empty date operand (`WFDate` or `WFTimeUntilCustomDate` or `WFTimeUntilFromDate`). Prefer `WFTimeUntilFromDate` for date-vs-date deltas. `WFTimeUntilUnit` can be omitted only when relying on the action default; never emit unused empty date keys.
- For **Extract Text from Image** (`is.workflow.actions.extracttextfromimage`), set exactly one non-empty image input key: prefer `WFImage` (fallback `WFInput` only when explicitly required by an existing pattern). Do not include an empty second image-input key.
- For API error handling with **Get Dictionary Value**, avoid direct optional key paths such as `error.message` on raw responses; extract `error` first, guard with **If Has Any Value**, then read nested keys inside that branch.
- Do not output placeholder actions with empty parameters. If a Text/Ask action would be blank, remove it or replace with a Comment. Omit `WFAskActionDefaultAnswer` entirely when there is no default.
- Never leave **If** actions with empty conditions. For `is.workflow.actions.conditional` **start blocks** (`WFControlFlowMode = 0`), always set `WFInput` and `WFCondition` (and `WFConditionalActionString` when the condition type requires a comparator). Modes 1/2 do not require these fields.
- Avoid `WFConditions`/content-predicate tables for simple text equality. For text comparisons, always set `WFInput` + `WFCondition` and use a named-variable path so the editor shows a stable input chip.
- For **If** inputs, always wrap in the editor-friendly structure: `WFInput = { Type: Variable, Variable: { Value: <token attachment>, WFSerializationType: WFTextTokenAttachment } }`.
- For **If** actions, do not set `WFInput` to a bare `WFTextTokenAttachment`; that frequently imports as blank/empty on iOS.
- For **If** actions, wrapping an **ActionOutput** is valid and often required for runtime stability.
- Prefer integer `WFCondition` codes for conditionals (`100` for Has Any Value, `2` for Is Greater Than) instead of condition name strings.
- `is.workflow.actions.input` should not be emitted as a runtime action. Reference shortcut input via an `ExtensionInput` attachment instead.
- For “Clipboard or Ask for Input” patterns, avoid numeric **Count → If**. Use a single **If** that checks whether the clipboard **has any value** (set `WFCondition` to integer `100` and point `WFInput` to the Clipboard variable).
- Avoid generating **Unknown Action** blocks. AppIntent/action identifiers must exist in the bundled ToolKit snapshot (`data/toolkit-v63-tool-ids.json`) and references (`APPINTENTS.md`, `ACTIONS.md`); local ToolKit DB checks are optional and additive. Do not invent identifiers. If an action is unavailable on the target OS/version, replace it with a supported fallback and note it in a Comment.
- Only use AppIntent actions when their **parameter keys are verified** (from `APPINTENTS.md` or a golden example). If unsure, prefer WF actions. For Apple Music search/play, favor `is.workflow.actions.filter.music` + `is.workflow.actions.playmusic` over `PlayMusicTopHitAction`.
- For unit conversions, prefer built‑in **Convert Measurement** (`measurement.create` + `measurement.convert`) instead of manual math. Use math only for unsupported units or custom formulas.
- Common identifier gotchas:
  - **Text** action is `is.workflow.actions.gettext` (never `is.workflow.actions.text`).
  - Avoid emitting the **Shortcut Input** action (`is.workflow.actions.input`) in generated shortcuts; use `ExtensionInput` token attachments where input is needed.
  - **Translate Text** is `is.workflow.actions.text.translate` (not `is.workflow.actions.translate`).
  - **Send Email** is `is.workflow.actions.sendemail` (never `sendmail`).
  - **Run Script** actions are `runapplescript`, `runshellscript`, `runsshscript`, `runjavascriptforautomation`, or `runjavascriptonwebpage` (there is no `runscript`).
  - **Podcast details** use `is.workflow.actions.properties.podcast` or `is.workflow.actions.properties.podcastshow` (there is no `properties.podcastepisode`).
  - **Find Notes** is `is.workflow.actions.filter.notes` — **never** `is.workflow.actions.findnotes` (does not exist). Output name is `"Note"` (singular).
  - **Repeat Each end** uses the **same identifier** `is.workflow.actions.repeat.each` with `WFControlFlowMode: 2` — **never** `is.workflow.actions.repeat.each.end` (does not exist). Both start and end share the same `GroupingIdentifier` UUID.
  - **Get Dictionary Value** is `is.workflow.actions.getvalueforkey` — **never** `is.workflow.actions.getdictionaryvalue` (old name, shows as Unknown Action on macOS 15+). Params: `WFDictionaryKey` (string), `WFInput` (dict reference). Output name: `"Dictionary Value"`.
- **`appendnote` WFInput must be `WFTextTokenString`** (not `WFTextTokenAttachment`) — confirmed from real shortcuts in the DB. Use `{"Value": {"string": "\ufffc", "attachmentsByRange": {"{0, 1}": {"OutputUUID": ..., "Type": "ActionOutput", "OutputName": "..."}}}, "WFSerializationType": "WFTextTokenString"}`.
- **`notification` WFNotificationActionBody must be `WFTextTokenString`** (not `WFTextTokenAttachment`) — same pattern as above.
- **`runjavascriptonwebpage` in share sheet shortcuts**: Requires `WFInput: {Value: {Type: "ExtensionInput"}, WFSerializationType: WFTextTokenAttachment}` and `WFWorkflowTypes: ["ActionExtension", "SafariWebPage"]`. Without `ExtensionInput`, JS runs without page context (or fails with "Unable to Run JavaScript on Web Page"). macOS also requires Automation permission (Shortcuts → Safari) in System Settings — if missing, add TCC entries for `com.apple.shortcuts`, `com.apple.WorkflowKit.ShortcutsViewService`, and `com.apple.WorkflowKit.BackgroundShortcutRunner` in `~/Library/Application Support/com.apple.TCC/TCC.db`, then restart.
- **`runjavascriptonwebpage` returns a JSON string, not a dict**: `completion({...})` serialises to a JSON text string. Always follow with `detect.dictionary` before calling `getvalueforkey`. Without this, all `getvalueforkey` values will be blank.
- **URL/text fields inside Repeat loops must use `WFTextTokenString`**: Using `WFTextTokenAttachment` for `WFURL` (or similar fields) inside a `repeat.each` produces blank values. Use `{"Value": {"string": "\ufffc", "attachmentsByRange": {"{0, 1}": {"VariableName": "Repeat Item", "Type": "Variable"}}}, "WFSerializationType": "WFTextTokenString"}`.
- **Visual thumbnail image picker pattern**: To show image thumbnails in `choosefromlist`, first download all images in Loop 1 (outputs become `Repeat Results` = Image list), then pass the loop END's `"Repeat Results"` output to `choosefromlist`. Passing URL strings instead of Image items shows text, not thumbnails.
- **Apple Notes actions require `AppIntentDescriptor`**: Both `filter.notes` and `appendnote` will show as "Unknown Action" without the descriptor. Use these exact values:
  ```python
  # For filter.notes:
  {"TeamIdentifier": "0000000000", "BundleIdentifier": "com.apple.mobilenotes",
   "Name": "Notes", "AppIntentIdentifier": "NoteEntity", "ActionRequiresAppInstallation": True}
  # For appendnote:
  {"TeamIdentifier": "0000000000", "BundleIdentifier": "com.apple.mobilenotes",
   "Name": "Notes", "AppIntentIdentifier": "AppendToNoteLinkAction"}
  ```
- Do not simplify or omit user requirements on your own. If the scope feels too large or uncertain, ask for clarification or propose a reduced version and wait for approval.
- If you extract multiple fields from a dictionary/API response, make sure **each** value is reused in later output or remove the unused extraction.
- For nested dictionary responses, use dot notation (including array indexes) in **Get Dictionary Value** keys (e.g., `results.tracks.items`, `artists.1.name`), but guard optional branches first (especially `error.*`).
- When composing display strings with multiple variables (e.g., `Track – Artist`), include a placeholder for each variable and update `attachmentsByRange` positions accordingly.
- For **Set Dictionary Value**, always connect the target dictionary via `WFDictionary`; do not rely on implicit input.
- Do not leave **Text**, **Number**, **URL**, **Math**, **Count**, or **Format Date** outputs unused. Wire them explicitly into the next action or a **Set Variable**.
- For **Adjust Date**, always wire the source date explicitly via `WFDate` (and optionally mirror it in `WFInput`), plus a non-empty `WFDuration`. `WFAdjustOperation` may be omitted when using the default Add behavior, but include it when you need explicit Add/Subtract control. Offset-picker-only payloads can import as `Add 0 seconds` on iOS and are not reliable.
- For **Format Date**, always set `WFDate` (not `WFInput`) with a `WFTextTokenString` placeholder. When using custom formats, set `WFDateFormatStyle=Custom`.
- For **Measurement** conversions, use the built‑ins:
  - **Create Measurement**: `is.workflow.actions.measurement.create` (outputs `Measurement`)
  - **Convert Measurement**: `is.workflow.actions.measurement.convert` with `WFInput` wired to the Measurement output
  - Do **not** do manual math unless the unit is unsupported. If you must, add a Comment containing `ALLOW_MANUAL_UNIT_CONVERSION` and explain why.
- For **Send Email**, use `is.workflow.actions.sendemail` and attach content using `WFSendEmailActionInputAttachments` with a `WFTextTokenString` placeholder.
- For **Translate Text** (`is.workflow.actions.text.translate`), use `WFInputText` (not `WFInput`), and set `WFSelectedFromLanguage` / `WFSelectedLanguage` to **display names** (e.g., “Spanish”, “French”, “Japanese”, “Chinese (Simplified)”) or a variable that outputs those names (avoid ISO codes like `es`, `fr`, `zh-Hans`).
- Never use **Repeat Results** inside a **Repeat with Each** loop; only use it after the loop ends.
- Inside **Repeat (count)** loops, use the **Repeat Index** named variable (Type=Variable) and never reference **Repeat Results** or ActionOutput from the repeat end inside the loop.
- If you reference **Shortcut Input**, set `WFWorkflowInputContentItemClasses` to non-empty input types. Do not use Shortcut Input when the shortcut receives no input (avoids “Stop and Respond”).
- If you do **not** reference Shortcut Input, keep `WFWorkflowInputContentItemClasses` empty.
- Notes create actions must include both a **title/name** parameter and a **content/markdown** parameter; do not leave them empty.

## Preflight Validation (Required)

After generating a shortcut, run the local validator and loop until it passes. This is a lightweight generate → validate → fix/regenerate loop.

**Checklist (must pass):**
- No empty parameters for **If**, **Ask**, **Text**, **Choose from Menu**, and other required fields.
- No empty `WFInput` where explicitly set.
- No missing `WFInput` for required-input actions (e.g., **Open URL**, **Get URLs from Input**, **Choose from List**, **Set Clipboard**, **Convert Image**, **Get Detail of Weather Conditions**, **Get Time Between Dates**).
- For **Adjust Date**, require a non-empty date source (`WFDate` or `WFInput`) and non-empty `WFDuration`; reject empty date keys when present.
- For **Get Time Between Dates**, require exactly one non-empty date operand and reject empty `WFDate` / `WFTimeUntilCustomDate` / `WFTimeUntilFromDate` keys when present.
- For **Extract Text from Image**, require exactly one non-empty image input key (`WFImage` preferred; `WFInput` allowed when intentionally used) and reject empty image-input keys.
- For **Change Case** and **Split Text**, input must be in the `text` parameter (not `WFInput`).
- For **Replace Text**, input must be in `WFInput` (not `text`).
- For **Split Text** with `WFTextSeparator=Custom`, `WFTextCustomSeparator` must be present; a single space (`" "`) is a valid separator.
- For **Find Notes**, `WFContentItemFilter` must be `WFContentPredicateTableTemplate` with non-empty templates; Name uses `Values.String` (`WFTextTokenString`), Folder uses `Values.Enumeration` (`WFLinkDynamicOptionSubstitutableState`).
- No Unknown Action identifiers (must exist in `ACTIONS.md` / `APPINTENTS.md` / `THIRD_PARTY_ACTIONS.md`).
- No mismatched text token placeholders.
- No unused outputs from **Text**, **Number**, **URL**, **Math**, **Count**, or **Format Date** actions.
- No `WFInput` values that wrap **ActionOutput** inside a `Type=Variable` wrapper for non-conditional actions. For **If** starts, wrapped ActionOutput is expected.
- Confirm API date formats. If an API/user requires a specific date format, use **Format Date → Custom** and set the exact format string (e.g., `yyyy-MM-dd`). Avoid hard‑coding `00:00:00` or `23:59:59`; use date‑only strings for start/end parameters. Only add `ALLOW_DATETIME_FORMAT` if the user explicitly requests a date‑time format.
- When using **Format Date** with a custom format string, set **Format Style = Custom** (i.e., include `WFDateFormatStyle=Custom`). Leaving it unset can display as “Short” in the UI.
- Keep a **raw Date variable** for calculations. Use **Adjust Date** on the raw date, then **Format Date** into strings for API parameters.
- For nested repeats, ensure the correct **Repeat Item N** and **Repeat Index N** are used (inner loop uses Repeat Item 2, etc.).
- Inside Repeat loops, **reference Repeat Item/Index as Variables** (Type=Variable with `VariableName: "Repeat Item"` or `"Repeat Item 2"`). Do not use ActionOutput references for Repeat Item/Index; they can show as Repeat Results in the UI.
- Avoid **Get Variable** actions unless their output is used immediately. Prefer inserting variables directly into action parameters.
- For result summaries, ensure **Text** actions interleave variables with placeholders (don’t leave them as plain text).
- Two required Comment blocks at the top, plus section comments for longer shortcuts.
- Comment density: for shortcuts with 8+ actions, require at least 3 comments; 16+ actions require 4; 24+ actions require 5. Every control‑flow start must be preceded by a Comment with a short bulleted wiring list.
- No vCard/VCF content unless explicitly allowed (`ALLOW_VCARD` comment).
- No API token loaded from file unless explicitly allowed (`ALLOW_TOKEN_FILE` comment).
- For Todoist updates, ensure `/rest/v2/tasks/` includes the task ID placeholder.
- For If conditions, `WFInput` must be a proper token attachment (`WFTextTokenAttachment` / `WFTextTokenString`), not an empty or raw variable dict.
- For Set Dictionary Value, `WFDictionary` must be populated with the target dictionary variable.
- For Set Variable, `WFInput` must be present and a token attachment (never leave it blank).
- For Set Variable, if the source is a constant (string/number), use **Text**/**Number** then wire its output into `WFInput` (do not leave the Set Variable action unconnected).
- For unit conversions, require `measurement.create` + `measurement.convert` unless a Comment includes `ALLOW_MANUAL_UNIT_CONVERSION`.

**Command (must run):**
```
python3 scripts/validate_shortcut.py /path/to/Shortcut.xml
```

If validation fails, fix the issue or regenerate the shortcut and re-run the validator until it passes. Only allow empty parameters for user-configurable fields (e.g., HomeKit accessories or user contacts), and document those with a Comment.
The validator is mandatory. Do **not** skip it or claim it is optional; if it fails to run, fix the validator or the environment and re-run.

## Comment Guidance (Manual Fix Hints)

Because some variable wiring may require manual correction, **insert a concise Comment before each major block** with a short **bulleted list** describing the expected variable wiring. Keep it brief, action-oriented, and specific.

Example:
- Set **Start Date Raw** from **Adjust Date** output
- Format **Start Date** with `yyyy-MM-dd`
- Use **Repeat Item 2** for inner loop dictionary values

## Control Flow & Menus

- Keep `GroupingIdentifier` consistent across the start/middle/end actions of **If**, **Repeat**, and **Choose from Menu** blocks; always close control-flow groups.
- Add an **Otherwise** branch when you need explicit false handling; use **Nothing** as a placeholder output if a branch should intentionally return no result.
- Guard empty lists with **Count → If** before **Choose from List** or **Repeat with Each**.
- Inside **Repeat with Each**, use **Repeat Item** for per-item extraction (**Get Dictionary Value**, **Get Name**, file uploads); avoid **Repeat Results** inside the loop.
- For **Count**, include both `WFInput` and `Input` pointing to the same variable so the UI shows the selected list.
- For **Choose from Menu**, ensure the number of menu item actions matches `WFMenuItems`, and keep titles consistent between the menu list and each case.
- For confirmations (Yes/No), use **Choose from Menu** or **Choose from List** with explicit options; **Show Alert does not return a choice** and should be used only for informational messages or if the user explicitly wants OK/Cancel.
- When the user asks for manual date entry with a date picker, default **Ask for Input** to **Date and Time** (not just Date) unless they explicitly request date-only.
- For string comparisons in **If**, especially after **Get Dictionary Value → Text**, set a named variable first (e.g., **Set Variable: Project Name Text**) instead of referencing a raw action output.
- For string comparisons in **If**, prefer **Get Dictionary Value → Text → Set Variable → If** and insert the named variable directly in the If input field. Do not add a redundant **Get Variable** hop unless you need a specific aggrandizement.
- If validator rules still conflict for a string comparison, replace the string If with `Match Text` + `Count` + numeric If (e.g., Count > 0) to avoid wrapper conflicts.
- For nested **Repeat with Each**, use **Repeat Item 2** (and **Repeat Index 2**) inside the inner loop; deeper nesting uses 3, 4, etc.

## Lists & Dictionaries

- Initialize a list before **Append to Variable**; use **Append Variable** inside **Repeat with Each** to build lists.
- After building a list, use **Combine Text** or **Choose from List** for output/selection.
- If JSON arrives as text, run **Detect Dictionary** before **Get Dictionary Value**.
- Use dot-notation keys (and tokenized keys when dynamic) in **Get Dictionary Value** to access nested data, but avoid direct optional paths like `error.message` before guarding the parent key.
- When constructing **Dictionary** actions, use `WFDictionaryFieldValue` wrappers (not raw arrays) and the correct item types for strings, nested dictionaries, and booleans.
- Shortcuts bug: when comparing a **Dictionary Value** (text) in an **If** condition, you must first pass it through a **Text** action, then compare the Text variable. Direct comparisons against Dictionary Value often appear blank and fail.

## Messages & Mixed Content

- When sending **both text and files** via **Send Message**, do **not** wrap everything in a single Text action.
- Use **Add to Variable** (`is.workflow.actions.appendvariable`) to build a multi-item variable:
  - Append the audio/file variable.
  - Append the text (and location text).
  - Do **not** initialize the variable first; just keep appending.
- Pass the named variable to **Send Message** as the message content. All appended items (different types) will be sent together.
- For Send Message content, prefer `WFTextTokenString` with a variable placeholder (not `WFTextTokenAttachment`), otherwise the message field can appear blank in the editor.

## Text & Parsing

- Use **Match Text → Get Group** to extract values with regex; follow with **Replace Text**/**Split Text**/**Combine Text** to normalize output.
- For **Match Text** (`is.workflow.actions.text.match`), wire source text using the `text` parameter (typically a `WFTextTokenString` placeholder), not `WFInput`.
- For **Replace Text** (`is.workflow.actions.text.replace`), use `WFInput` for source text. Do not use a `text` key for this action.
- For **Replace Text** (`is.workflow.actions.text.replace`), wire `WFInput` using a `WFTextTokenString` placeholder (or wrapped variable form), not a bare `WFTextTokenAttachment`, to avoid empty-looking inputs on iOS.
- For **Change Case** (`is.workflow.actions.text.changecase`), wire source text via the `text` parameter. Do not use `WFInput`.
- For **Split Text** (`is.workflow.actions.text.split`), wire source text via the `text` parameter. Do not use `WFInput`. If `WFTextSeparator` is `Custom`, you must also set `WFTextCustomSeparator` (space is valid).
- For Replace Text delete-match operations, prefer omitting `WFReplaceTextReplace`; explicit empty replacement is allowed, but omission is cleaner.
- For **Find Notes** (`is.workflow.actions.filter.notes`), keep `WFContentItemFilter` as `WFContentPredicateTableTemplate` with non-empty `WFActionParameterFilterTemplates`.
- For **Find Notes** name filters, use `Values.String` as a `WFTextTokenString` state so variable text remains visible in the editor.
- For **Find Notes** folder filters, use `Values.Enumeration` with `WFLinkDynamicOptionSubstitutableState`, wrapping an inner `WFTextTokenAttachment` variable value.
- Use **Get Rich Text from Markdown** or **Get Markdown from Rich Text** when moving between plain text and rich-text apps.
- When presenting results with **Text**, interleave literals and variables in one Text action using placeholders and correct `attachmentsByRange` for each variable.

## Files & Output

- Prefer **Select File** (`is.workflow.actions.file.select`) for user file input; use **Document Picker Open/Save** when you need explicit Files UI flows.
- Use **Set Item Name** before saving files to ensure predictable filenames.
- For file outputs, preview with **Quick Look** before **Save/Share** when appropriate.
- For PDFs, a common pattern is **Make PDF → Preview Document → Save/Share**.
- For **Notes** output, use the supported Notes action for the target OS (AppIntent on iOS/iPadOS). If Notes isn’t available, fall back to **Share** or **Save File** and add a Comment explaining the fallback.

## Signing & Install Naming

- Sign using a canonical filename that matches the intended shortcut name; do not append `_signed`.
- If `shortcuts sign` says `The file doesn't exist` for an existing file, retry from a clean XML copy to a `.shortcut` path (for example, `cp source.xml /tmp/MyShortcut.shortcut`), then sign again.
- `shortcuts` automation should rely only on supported subcommands: `run`, `list`, `view`, and `sign`.
- During install verification, treat a `_signed` library name as failure and reinstall using a canonical filename.

## Numbers & Accumulators

- Inside a **Repeat with Each**, do not **Set Variable** directly to a running total each pass. Use a temp variable for the current value, then **Math** (add/subtract) into a master total variable, and **Set Variable** to the master total.
- To convert cents to dollars, divide by **100** first, then round to hundredths if needed (do not “round to hundredths” as a substitute for division).
- If a **Math** action uses operand **100** on a cents value, the operator must be **÷** (not + or −).
- Prefer **com.apple.Notes.CreateNoteFromMarkdownLinkAction** for markdown output and a plain Create Note AppIntent for rich/plain text. Avoid `com.apple.mobilenotes.SharingExtension` unless you’ve verified it exists on the target OS.

## Shortcut Building Techniques

- Start every shortcut with:
  1) A detailed Comment describing what the shortcut does.
  2) A second Comment with the original user prompt in this exact format:

```
Shortcuts generated by Shortcuts Playground. May contain mistakes. Always check the shortcut's actions first.

This shortcut was created via the following user prompt:

> {User Prompt}
```
- For any shortcut longer than ~20 actions, add section headers as Comment blocks (e.g., `--- FETCH TASKS ---`, `--- BUILD LIST ---`, `--- UPDATE TASKS ---`).

- Use variable names with spaces (e.g., `PDF Pages`).
- Prefer actions that work on both iOS and macOS unless the user explicitly wants macOS-only behavior.
  - Example: Instead of **Get Parent Folder** (macOS-only), use **Get Details of File** and extract the path.
- To get PDF pages, use **Split PDF Into Pages**, then **Count** the resulting items.
- For selecting videos, default to **Select Photos** configured for videos. If both Photos and Files are requested, use **Choose from Menu** with both pickers.
