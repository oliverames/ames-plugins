---
name: raw-plist
description: Build Apple Shortcuts as raw plist XML for actions Jelly can't compile — photo filters with predicates, Tailscale AppIntents, complex variable aggrandizements, base64, file save/rename, and any action needing exact WF parameter control. Use when the create-shortcut skill routes here, or when the user needs a shortcut with third-party AppIntents or fine-grained plist wiring.
allowed-tools: Write, Bash, Read
---

# Apple Shortcuts — Raw Plist Approach

Generate valid `.shortcut` files as binary plist (written via Python) and sign them.

**Mandatory**: Follow all rules in `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/BEST_PRACTICES.md`.

## Recommended Reading Order

1. `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/BEST_PRACTICES.md` — mandatory rules and validation
2. `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/PLIST_FORMAT.md` — plist structure and serialization
3. `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/ACTIONS.md` — action identifiers and parameters
4. `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/APPINTENTS.md` — AppIntent actions (Tailscale, etc.)
5. `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/VARIABLES.md` — variable wiring patterns
6. `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/CONTROL_FLOW.md` — repeat, conditional, menu patterns
7. `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/FILTERS.md` — photo/file filter predicates
8. `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/EXAMPLES.md` — complete working examples

## Reading Installed Shortcuts for Reference

When you need to understand an existing shortcut's exact plist structure, read it directly from
the SQLite database. `ZACTIONS` in the `ZSHORTCUT` table is binary plist data containing
`WFWorkflowActions`. This is the canonical way to verify unknown action structures — always
prefer this over guessing parameter names.

```python
import sqlite3, plistlib, json, os

db = sqlite3.connect(os.path.expanduser('~/Library/Shortcuts/Shortcuts.sqlite'))

# Find all shortcuts matching a name pattern
rows = db.execute(
    "SELECT ZNAME, ZACTIONS FROM ZSHORTCUT WHERE ZNAME LIKE ?", ("%Shortcut Name%",)
).fetchall()

for name, data in rows:
    if not data:
        continue
    sc = plistlib.loads(data)
    actions = sc.get('WFWorkflowActions', sc)  # some rows wrap in WFWorkflowActions
    print(f"\n=== {name} ===")
    for i, a in enumerate(actions):
        ident = a.get('WFWorkflowActionIdentifier', '')
        params = a.get('WFWorkflowActionParameters', {})
        print(f"  [{i}] {ident}")
        print(f"      {json.dumps(params, default=str)[:200]}")

db.close()
```

To inspect a specific action fully:
```python
import sqlite3, plistlib, json, os

db = sqlite3.connect(os.path.expanduser('~/Library/Shortcuts/Shortcuts.sqlite'))
name, data = db.execute(
    "SELECT ZNAME, ZACTIONS FROM ZSHORTCUT WHERE ZNAME = ?", ("Exact Shortcut Name",)
).fetchone()
sc = plistlib.loads(data)
actions = sc.get('WFWorkflowActions', sc)
print(json.dumps(actions, indent=2, default=str))
db.close()
```

> **Tip**: If you're unsure about a Notes, Calendar, Reminders, or third-party action's
> parameter names, always read a real installed shortcut before generating. The SQLite DB
> is the ground truth; toolkit data may be incomplete for AppIntents-based actions.

## Building Shortcuts with Python

Prefer writing shortcuts as Python-generated binary plist (cleaner than XML, no encoding issues):

```python
import plistlib, uuid

def new_uuid():
    return str(uuid.uuid4()).upper()

def var_ref(name):
    """Reference a named variable"""
    return {
        "Value": {"VariableName": name, "Type": "Variable"},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def action_ref(output_uuid, output_name):
    """Reference output from a previous action by UUID"""
    return {
        "Value": {"OutputUUID": output_uuid, "Type": "ActionOutput", "OutputName": output_name},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def text_with_var(var_name):
    """Embed a variable in a text string"""
    return {
        "Value": {
            "string": "\ufffc",
            "attachmentsByRange": {"{0, 1}": {"VariableName": var_name, "Type": "Variable"}}
        },
        "WFSerializationType": "WFTextTokenString"
    }

shortcut = {
    "WFWorkflowActions": [...],
    "WFWorkflowClientVersion": "1343.4",
    "WFWorkflowHasOutputFallback": False,
    "WFWorkflowIcon": {
        "WFWorkflowIconStartColor": 4071891967,
        "WFWorkflowIconGlyphNumber": 59511
    },
    "WFWorkflowImportQuestions": [],
    "WFWorkflowInputContentItemClasses": [],
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowName": "My Shortcut",
    "WFWorkflowNoInputBehavior": {"Name": "WFWorkflowNoInputBehaviorAskForInput", "Parameters": {}},
    "WFWorkflowOutputContentItemClasses": [],
    "WFWorkflowTypes": []
}

with open("/path/to/output.shortcut", "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)
```

## Sign After Writing

```bash
shortcuts sign --mode anyone --input output.shortcut --output output.shortcut
```

## Tailscale Device Picker Pattern

```python
U_tailscale = new_uuid()
U_choose = new_uuid()

# 1. Get all Tailscale devices
{"WFWorkflowActionIdentifier": "io.tailscale.ipn.ios.DeviceAppEntity",
 "WFWorkflowActionParameters": {
     "UUID": U_tailscale,
     "AppIntentDescriptor": {
         "TeamIdentifier": "W5364U7YZB",
         "BundleIdentifier": "io.tailscale.ipn.ios",
         "Name": "Tailscale",
         "AppIntentIdentifier": "DeviceAppEntity",
         "ActionRequiresAppInstallation": True
     }
 }}

# 2. Let user choose a device
{"WFWorkflowActionIdentifier": "is.workflow.actions.choosefromlist",
 "WFWorkflowActionParameters": {
     "WFInput": action_ref(U_tailscale, "Devices"),
     "UUID": U_choose
 }}

# 3. Extract IP address from selected device
{"WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
 "WFWorkflowActionParameters": {
     "WFInput": {
         "Value": {
             "Type": "ActionOutput",
             "OutputName": "Selected Item",
             "OutputUUID": U_choose,
             "Aggrandizements": [{
                 "PropertyUserInfo": {
                     "WFLinkEntityContentPropertyUserInfoPropertyIdentifier": "ipv4Address"
                 },
                 "Type": "WFPropertyVariableAggrandizement",
                 "PropertyName": "ipv4Address"
             }]
         },
         "WFSerializationType": "WFTextTokenAttachment"
     },
     "WFVariableName": "Remote Mac IP"
 }}
```

## Photo Filtering with Predicates

For filtering by resolution/dimensions (requires raw plist — Jelly can't do this):

```python
# Filter photos wider than 2000px
{"WFWorkflowActionIdentifier": "is.workflow.actions.filter.photos",
 "WFWorkflowActionParameters": {
     "UUID": U_filter,
     "WFContentItemFilter": {
         "Value": {
             "WFActionParameterFilterPrefix": 1,
             "WFActionParameterFilterTemplates": [{
                 "Operator": 6,   # GreaterThan
                 "LeftHandExpression": {"WFItemContentPropertyName": "Width"},
                 "RightHandExpression": {"WFValue": {"Value": 2000, "WFSerializationType": "WFNumberSubstitutableState"}}
             }]
         },
         "WFSerializationType": "WFContentPredicateTableTemplate"
     },
     "WFContentItemLimit": 50
 }}
```

See `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/FILTERS.md` for full filter predicate reference.

## Run JavaScript on Web Page

For extracting images from web pages:

```python
{"WFWorkflowActionIdentifier": "is.workflow.actions.runjavascriptonwebpage",
 "WFWorkflowActionParameters": {
     "UUID": U_js,
     "WFJavaScript": """
completion(
  Array.from(document.querySelectorAll('img'))
    .map(img => img.src || img.dataset.src)
    .filter(src => src && (src.endsWith('.jpg') || src.endsWith('.png') || src.endsWith('.webp')))
);
"""
 }}
```

## Icon & Color Resolver

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/scripts/select_shortcut_icon_color.py --prompt "your shortcut description"
```

## Validator

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/scripts/validate_shortcut.py /path/to/Shortcut.xml
```

## Golden Examples

Read `${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/golden-shortcuts/index.jsonl` to find relevant examples, then load only the matching XML:
`${CLAUDE_PLUGIN_ROOT}/skills/raw-plist/references/golden-shortcuts/xml/<id>.xml`
