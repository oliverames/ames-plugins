---
name: jelly
description: Jelly language compiler for Apple Shortcuts — used by the create-shortcut skill router for Jelly-compilable actions. Also use directly when the user mentions "Jelly", "jelly file", "compile a shortcut", or wants to write Shortcuts using a text-based DSL rather than raw plist XML.
allowed-tools: Write, Bash, Read
---

# Jelly — Shortcuts via Jelly Language

Write `.jelly` files and compile them to signed `.shortcut` files using the `jelly` CLI (at `jelly`).

**Goal: deliver a real, signed `.shortcut` file every time.** Jelly is the primary approach — readable, reliable, no manual UUID wiring. When Jelly can't handle an action, fall back to the raw-plist skill (`the **raw-plist** skill`) for that piece.

---

## Workflow

1. Write `.jelly` file
2. Compile: `jelly MyShortcut.jelly --export --out MyShortcut.shortcut`
3. Read compiler output — fix any errors (the compiler is very literal about missing params)
4. Sign: `shortcuts sign --mode anyone --input MyShortcut.shortcut --output MyShortcut.shortcut`
5. Deliver the signed `.shortcut` to the user

**The compile → fix → recompile loop is normal.** The compiler tells you exactly which params are missing. Look them up in the Core Action Reference below and add them.

---

## Jelly Language Syntax

### File Header (required)

```jelly
import Shortcuts
#Color: red, #Icon: star
```

Colors: `red`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `gray`, `teal`
Icons: SF Symbol names in camelCase — confirmed working: `star`, `globe`, `envelope`. Many names (e.g. `bolt`, `doc`) are rejected by the CLI; if unsure, omit `#Icon` entirely.

### Output Capture (`>>`)

Every action that produces output can be captured with `>> variableName`:

```jelly
text(text: "Hello World") >> greeting
showResult(text: "${greeting}")
```

### String Interpolation vs Bare Variable References — CRITICAL

This is the most common source of compile errors. Jelly has two distinct parameter types:

**JellyString** — accepts `${varName}` interpolation. Used by text-like actions:
```jelly
text(text: "Hello ${name}!")
showResult(text: "${greeting}")
url(url: "${apiURL}")
```

**JellyVariableReference** — requires a **bare variable name** (no `${}` wrapper). Used by actions that receive data objects, not strings. Common examples:
```jelly
getDictionaryFrom(input: response)       // NOT "${response}"
valuesFrom(dictionary: profile, key: "name")   // NOT "${profile}"
count(input: pageContent, type: Characters)    // NOT "${pageContent}"
runShellScript(input: pageText, ...)     // NOT "${pageText}"
setClipboard(variable: myVar, ...)       // NOT "${myVar}"
getTextFrom(input: fileContents)         // NOT "${fileContents}"
getItemFromList(list: myList)            // NOT "${myList}"
```

**Rule of thumb:** If the action receives a variable to process (not embed in a string), use a bare ref. If you're building a text string, use `${}`.

### Magic Variables

Built-in variables available in specific contexts — use directly in interpolation:

| Name | Available in |
|---|---|
| `ShortcutInput` | Anywhere — input passed to the shortcut |
| `CurrentDate` | Anywhere — current date/time (use in `adjustDate(date: ${CurrentDate}, ...)`) |
| `Repeat Item` | Inside `repeatEach` block |
| `Repeat Index` | Inside `repeat(count:)` block |
| `Chosen Item` | After `choose()` |
| `Provided Input` | After `askForInput()` |
| `If Result` | After an `if` block |
| `Menu Result` | After a `menu` block |

**Always use `>> varName` capture instead of `var x = Magic Name`** — names with spaces can't be used as `var` assignment targets and will cause syntax errors.

### Comments

```jelly
// Single line comment
/* Multi-line
   comment */
```

### Control Flow ("Blocks")

These correspond to what Apple calls "blocks" in the Shortcuts UI:

**If / Else:**
```jelly
if(Variable == "something") {
    showResult(text: "Matched")
} else {
    showResult(text: "No match")
}
```

Variables assigned inside `if`/`else` branches are accessible after the block ends — both branches should assign the same variable name.

Conditions: `==`, `!=`, `.contains`, `.beginsWith`, `.endsWith`, `>`, `<`, `>=`, `<=`, `== nil`, `!= nil`

**Repeat N times:**
```jelly
repeat(count: 5) {
    showResult(text: "${Repeat Index}")
}
```

**Repeat Each:**
```jelly
repeatEach(myList) {
    showResult(text: "${Repeat Item}")
}
```

**Menu:**
```jelly
menu "What do you want to do?" {
    case("Option A"):
        showResult(text: "You chose A")
    case("Option B"):
        showResult(text: "You chose B")
    case("Cancel"):
        exit(var: ShortcutInput)
}
```

Note: The prompt string goes directly after `menu` with a **space, not parens** — `menu "prompt" {` compiles; `menu("prompt") {` does not. The 3 "Unable to get core node - :" warnings from `case:` labels are benign and don't block compilation.

### Functions and Macros

**Function** (reusable block):
```jelly
function greet(name) {
    text(text: "Hello, ${name}!") >> result
    return result
}
greet(name: "Oliver") >> greeting
```

**Macro** (inlined at call site):
```jelly
macro logStep(message) {
    comment(text: "[LOG] ${message}")
}
logStep(message: "Starting process")
```

---

## Core Action Reference

All params listed. Most are technically required — missing ones cause compile warnings but usually still succeed. Supply them all for clean compilation.

### Action Table

| Jelly function | What it does | Params |
|---|---|---|
| `text(text:)` | Text action | `text` |
| `showResult(text:)` | Show Result | `text` |
| `alert(alert:, title:, cancel:)` | Alert dialog | `alert` (message), `title`, `cancel` (bool) |
| `askForInput(prompt:, type:, default:, allowDecimal:, allowNegative:)` | Ask for Input | `prompt`, `type` (Text/Number/Date/Email/URL), `default`, `allowDecimal` (bool), `allowNegative` (bool) |
| `number(value:)` | Number | `value` |
| `list(items:)` | List | `items: (item1, item2, ...)` |
| `dictionary({})` | Dictionary | inline `{key: value}` |
| `getItemFromList(list:, type:, index:)` | Get Item from List | `list` (bare ref), `type` (First/Last/Random/Item At Index), `index` |
| `choose(list:, prompt:)` | Choose from List | `list` (bare ref), `prompt`, `multiple` (bool) |
| `count(input:, type:)` | Count | `input` (bare ref), `type` (Items/Characters) |
| `comment(text:)` | Comment | `text` |
| `nothing()` | Nothing | — |
| `exit(var:)` | Exit Shortcut | `var` (bare variable ref for output, e.g. `exit(var: myResult)`) |
| `wait(seconds:)` | Wait | `seconds` |
| `url(url:)` | URL | `url` |
| `openURL(url:)` | Open URL | `url` |
| `downloadURL(url:, method:)` | Get Contents of URL | `url`, `method` (GET/POST/PUT/PATCH/DELETE) — omit optional params for basic GET; do NOT pass `{}` empty dicts (crashes parser) |
| `showWebPage(url:)` | Show Web Page | `url` |
| `getDictionaryFrom(input:)` | Get Dictionary from Input | `input` (**bare ref**) |
| `valuesFrom(dictionary:, key:)` | Get Dictionary Value | `dictionary` (**bare ref**), `key` |
| `setValue(key:, value:, dictionary:)` | Set Dictionary Value | `key`, `value`, `dictionary` (bare ref) |
| `getTextFrom(input:)` | Get Text from Input | `input` (**bare ref**) |
| `replaceText(input:, find:, replace:)` | Replace Text | `input`, `find`, `replace`, `isRegex` (bool), `caseSensitive` (bool) |
| `changeCase(text:, case:)` | Change Case | `text` (must be Text type — wrap through `text()` if needed), `case` (uppercase/lowercase/everyword/titlecase/sentencecase/spongebob/alternating) |
| `splitText(text:, separator:)` | Split Text | `text`, `separator` (NewLines/Spaces/EveryCharacter/Custom) |
| `matchText(text:, regex:)` | Match Text | `text`, `regex` |
| `combineText(text:, separator:)` | Combine Text | `text`, `separator` |
| `base64(input:, encode:)` | Base64 Encode/Decode | `input`, `encode` (bool) |
| `encodeURL(url:)` | URL Encode | `url` |
| `expandURL(url:)` | Expand URL | `url` |
| `hash(input:, type:)` | Hash | `input`, `type` (MD5/SHA1/SHA256/SHA512) |
| `formatDate(date:, dStyle:, tStyle:, custom:, isoTime:)` | Format Date | `date`, `dStyle` (None/Short/Medium/Long/Relative/RFC 2822/ISO 8601/Custom), `tStyle` (None/Short/Medium/Long), `custom` (string), `isoTime` (bool) |
| `adjustDate(date:, operation:, duration:)` | Adjust Date | `date` (bare ref or `${CurrentDate}`), `operation` (Add/Subtract), `duration` (quoted string: `"30 Minutes"`, `"1 Hours"`) |
| `getTimeBetweenDates(date1:, date2:)` | Time Between Dates | `date1`, `date2` |
| `getLocation(input:)` | Get Location | `input` (e.g. `ShortcutInput` or a location variable) |
| `getCurrentConditions(location:)` | Get Current Weather | `location` (bare ref) |
| `conditionDetail(condition:, detail:)` | Weather Condition Detail | `condition` (bare ref), `detail` (Temperature/Condition/Humidity/WindSpeed/etc) — **see parser bug note below** |
| `sendNotification(body:, title:, sound:, attachment:)` | Show Notification | `body`, `title`, `sound` (bool), `attachment` (bare ref) |
| `setVariable(name:, value:)` | Set Variable | `name`, `value` |
| `getVariable(name:)` | Get Variable | `name` |
| `randomNumber(min:, max:)` | Random Number | `min`, `max` |
| `runShortcut(name:, input:, show:)` | Run Shortcut | `name`, `input`, `show` (bool) |
| `runAppleScript(script:)` | Run AppleScript | `script` |
| `runShellScript(input:, script:, shell:, inputMode:)` | Run Shell Script | `input` (**bare ref**), `script`, `shell` (binbash/binzsh/binsh/usrbinpython/usrbinruby/usrbinswift), `inputMode` (asarguments/tostdin) |
| `openApp(id:)` | Open App | `id` (bundle ID) |
| `getFile(path:, picker:, error:)` | Get File | `path`, `picker` (bool), `error` (bool) |
| `saveFile(input:, path:, ask:, overwrite:)` | Save File | `input`, `path`, `ask` (bool), `overwrite` (bool) |
| `deleteFile(input:, confirm:)` | Delete File | `input`, `confirm` (bool) |
| `getFolderContents(folder:)` | Get Folder Contents | `folder` |
| `quicklook(input:)` | Quick Look | `input` |
| `richTextFromMarkdown(markdown:)` | Rich Text from Markdown | `markdown` |
| `shortcutInput()` | Shortcut Input | — |
| `getClipboard()` | Get Clipboard | — |
| `setClipboard(variable:, local:, expiration:)` | Set Clipboard | `variable` (**bare ref**), `local` (bool), `expiration` (number) |

---

## Working Examples

### Clipboard Uppercase

```jelly
import Shortcuts
#Color: blue, #Icon: star

getClipboard() >> clipRaw
text(text: "${clipRaw}") >> clipText
changeCase(text: "${clipText}", case: uppercase) >> upperText
setClipboard(variable: upperText, local: false, expiration: 3)
```

Note: `changeCase` requires Text type. Wrapping through `text()` coerces the clipboard output to Text.

### HTTP Request + Parse JSON

```jelly
import Shortcuts
#Color: orange

askForInput(prompt: "Enter a GitHub username:", type: Text, default: "", allowDecimal: false, allowNegative: false) >> usernameInput
text(text: "https://api.github.com/users/${usernameInput}") >> apiURL
url(url: "${apiURL}") >> apiURLObj
downloadURL(url: "${apiURLObj}", method: GET) >> apiResponse
getDictionaryFrom(input: apiResponse) >> profile
valuesFrom(dictionary: profile, key: "name") >> userName
valuesFrom(dictionary: profile, key: "followers") >> followerCount
text(text: "Name: ${userName}\nFollowers: ${followerCount}") >> summary
showResult(text: "${summary}")
```

Key: `getDictionaryFrom` and `valuesFrom` take bare refs — no `${}` around the variable name.

See `references/jelly-examples.md` for more examples: menu-driven shortcuts, weather notifications, AppleScript date manipulation, and conditional content length.

---

## Fallback: Unsupported Actions

Jelly supports ~300 of Apple's 600+ Shortcuts actions. When you hit an action Jelly can't compile:

1. **Check the compiler error** — `Unable to get core node` or `Unable to get shortcuts action` means it's unsupported
2. **Use the raw-plist skill** (`the **raw-plist** skill`) to build that specific action, then splice it in
3. **Or use raw plist inline** — the compiler passes through WF plist blocks embedded in Jelly

---

## Compile & Sign Commands

```bash
# Compile (run from directory containing the .jelly file)
cd /path/to/output && jelly MyShortcut.jelly --export --out MyShortcut.shortcut

# Sign (required before Shortcuts.app will accept it)
shortcuts sign --mode anyone --input MyShortcut.shortcut --output MyShortcut.shortcut
```

---

## Looking Up Unknown Parameters

When you hit `Missing parameter X in functionName`, look up the parameter file on GitHub:

```
https://github.com/OpenJelly/Open-Jellycore/blob/main/Sources/Open-Jellycore/Core/Compiler/Lookup%20Tables/Apps/Shortcuts/Actions/<FunctionName>Parameter.swift
```

Or inspect the binary directly for undocumented function names:
```bash
strings jelly | grep -i "weather\|location\|condition"
```

Real-world `.jelly` examples: https://github.com/extratone/jellycuts

---

## Compiler Gotchas

- **Enum values use raw compact form** — `everyword` not `"every word"`, `titlecase` not `"title case"`, `binzsh` not `"/bin/zsh"`, `asarguments` not `"as arguments"`
- **All params are technically required** — missing ones produce warnings but compilation may still succeed; supply all for clean builds
- **`exit(var:)` not `exit()`** — pass a variable reference as the shortcut output
- **Nested loops** — inner `Repeat Item` is `Repeat Item 2` for the second level
- **Conditions with nil** — use `== nil` (not `== ""`) to check for missing values
- **`sendNotification` not `notification`** — use the full function name
- **No empty `{}` dict literals** — passing `{}` as a param value crashes the parser; omit optional dict params entirely
- **`conditionDetail` parser bug** — after a `conditionDetail(...)` call, always insert a `// comment` line before the next action, or the next action's first character gets dropped (causes compile error)
- **Unicode characters in string arguments** — avoid non-ASCII characters like `°` (degree), `—` (em-dash), `–` (en-dash) inside any string argument — they cause the next action's first character to be silently stripped. Write ASCII equivalents: "degrees", "-", "--"
- **`shareSheet` is not implemented** — use `openURL(url: "mailto:...")` or similar workarounds instead

---

## Complete Function List (300+)

Jelly supports 300+ functions across text, files, network, images, music, contacts, calendar, notes, device, apps, scripting, math, encoding, and utilities. See `references/jelly-functions.md` for the complete categorized list.

---

## Notes

- `jelly` CLI: `jelly` (v1.1.0)
- Source: https://github.com/OpenJelly/Open-Jellycore
- Real-world examples: https://github.com/extratone/jellycuts
- Objects/OOP not implemented; use dictionaries instead
- For actions Jelly can't handle, fall back to `raw-plist` skill
