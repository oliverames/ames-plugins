# Complete Working Examples

Copy-paste ready examples that can be signed and imported.

## Missing Actions (Real Syntax)

Use these identifiers/keys when generating Measurement + Send Email actions.

```xml
<!-- Create Measurement (outputs Measurement) -->
<dict>
  <key>WFWorkflowActionIdentifier</key>
  <string>is.workflow.actions.measurement.create</string>
  <key>WFWorkflowActionParameters</key>
  <dict>
    <key>UUID</key>
    <string>4C78651D-90D9-4ED5-99A3-DE37FEA319C2</string>
  </dict>
</dict>

<!-- Convert Measurement (wire WFInput to Measurement output) -->
<dict>
  <key>WFWorkflowActionIdentifier</key>
  <string>is.workflow.actions.measurement.convert</string>
  <key>WFWorkflowActionParameters</key>
  <dict>
    <key>UUID</key>
    <string>CC570E80-93E1-4BE6-B9E5-BC192E35E691</string>
    <key>WFInput</key>
    <dict>
      <key>Value</key>
      <dict>
        <key>OutputName</key>
        <string>Measurement</string>
        <key>OutputUUID</key>
        <string>4C78651D-90D9-4ED5-99A3-DE37FEA319C2</string>
        <key>Type</key>
        <string>ActionOutput</string>
      </dict>
      <key>WFSerializationType</key>
      <string>WFTextTokenAttachment</string>
    </dict>
  </dict>
</dict>

<!-- Send Email (attach Text output via WFSendEmailActionInputAttachments) -->
<dict>
  <key>WFWorkflowActionIdentifier</key>
  <string>is.workflow.actions.sendemail</string>
  <key>WFWorkflowActionParameters</key>
  <dict>
    <key>UUID</key>
    <string>B7FE8569-7458-48BF-B8DA-90EA47CDED1E</string>
    <key>WFSendEmailActionInputAttachments</key>
    <dict>
      <key>Value</key>
      <dict>
        <key>attachmentsByRange</key>
        <dict>
          <key>{0, 1}</key>
          <dict>
            <key>OutputName</key>
            <string>Text</string>
            <key>OutputUUID</key>
            <string>8A6EBE5D-D6C6-41AD-9A94-52A8EAAD5E5D</string>
            <key>Type</key>
            <string>ActionOutput</string>
          </dict>
        </dict>
        <key>string</key>
        <string>￼</string>
      </dict>
      <key>WFSerializationType</key>
      <string>WFTextTokenString</string>
    </dict>
  </dict>
</dict>
```

## Example 1: Hello World

The simplest shortcut - displays "Hello World!".

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.gettext</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>11111111-1111-1111-1111-111111111111</string>
                <key>WFTextActionText</key>
                <string>Hello World!</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{0, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Text</string>
                                <key>OutputUUID</key>
                                <string>11111111-1111-1111-1111-111111111111</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>￼</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
    </array>
    <key>WFWorkflowClientVersion</key>
    <string>2700.0.4</string>
    <key>WFWorkflowHasOutputFallback</key>
    <false/>
    <key>WFWorkflowIcon</key>
    <dict>
        <key>WFWorkflowIconGlyphNumber</key>
        <integer>59511</integer>
        <key>WFWorkflowIconStartColor</key>
        <integer>4282601983</integer>
    </dict>
    <key>WFWorkflowImportQuestions</key>
    <array/>
    <key>WFWorkflowMinimumClientVersion</key>
    <integer>900</integer>
    <key>WFWorkflowMinimumClientVersionString</key>
    <string>900</string>
    <key>WFWorkflowName</key>
    <string>Hello World</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## Example 2: Ask User for Input

Asks user for their name and displays a greeting.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.ask</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA</string>
                <key>WFAskActionPrompt</key>
                <string>What is your name?</string>
                <key>WFInputType</key>
                <string>Text</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{7, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Provided Input</string>
                                <key>OutputUUID</key>
                                <string>AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>Hello, ￼!</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
    </array>
    <key>WFWorkflowClientVersion</key>
    <string>2700.0.4</string>
    <key>WFWorkflowHasOutputFallback</key>
    <false/>
    <key>WFWorkflowIcon</key>
    <dict>
        <key>WFWorkflowIconGlyphNumber</key>
        <integer>59511</integer>
        <key>WFWorkflowIconStartColor</key>
        <integer>4282601983</integer>
    </dict>
    <key>WFWorkflowImportQuestions</key>
    <array/>
    <key>WFWorkflowMinimumClientVersion</key>
    <integer>900</integer>
    <key>WFWorkflowMinimumClientVersionString</key>
    <string>900</string>
    <key>WFWorkflowName</key>
    <string>Greeting</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## Example 3: AI Query

Asks user for a question, sends it to Apple Intelligence, and displays the response.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.ask</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB</string>
                <key>WFAskActionPrompt</key>
                <string>What would you like to ask?</string>
                <key>WFInputType</key>
                <string>Text</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.askllm</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>CCCCCCCC-CCCC-CCCC-CCCC-CCCCCCCCCCCC</string>
                <key>WFLLMModel</key>
                <string>Apple Intelligence</string>
                <key>WFGenerativeResultType</key>
                <string>Text</string>
                <key>WFLLMPrompt</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{0, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Provided Input</string>
                                <key>OutputUUID</key>
                                <string>BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>￼</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{0, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Response</string>
                                <key>OutputUUID</key>
                                <string>CCCCCCCC-CCCC-CCCC-CCCC-CCCCCCCCCCCC</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>￼</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
    </array>
    <key>WFWorkflowClientVersion</key>
    <string>2700.0.4</string>
    <key>WFWorkflowHasOutputFallback</key>
    <false/>
    <key>WFWorkflowIcon</key>
    <dict>
        <key>WFWorkflowIconGlyphNumber</key>
        <integer>59511</integer>
        <key>WFWorkflowIconStartColor</key>
        <integer>4282601983</integer>
    </dict>
    <key>WFWorkflowImportQuestions</key>
    <array/>
    <key>WFWorkflowMinimumClientVersion</key>
    <integer>900</integer>
    <key>WFWorkflowMinimumClientVersionString</key>
    <string>900</string>
    <key>WFWorkflowName</key>
    <string>Ask AI</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## Example 4: Menu Demo

Presents a menu with three options, each displaying different text.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <!-- Menu Start -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>0</integer>
                <key>WFMenuPrompt</key>
                <string>What would you like to do?</string>
                <key>WFMenuItems</key>
                <array>
                    <string>Say Hello</string>
                    <string>Say Goodbye</string>
                    <string>Tell a Joke</string>
                </array>
            </dict>
        </dict>
        <!-- Case 1 -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>1</integer>
                <key>WFMenuItemTitle</key>
                <string>Say Hello</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <string>Hello there! Nice to meet you.</string>
            </dict>
        </dict>
        <!-- Case 2 -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>1</integer>
                <key>WFMenuItemTitle</key>
                <string>Say Goodbye</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <string>Goodbye! See you next time.</string>
            </dict>
        </dict>
        <!-- Case 3 -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>1</integer>
                <key>WFMenuItemTitle</key>
                <string>Tell a Joke</string>
            </dict>
        </dict>
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <string>Why do programmers prefer dark mode? Because light attracts bugs!</string>
            </dict>
        </dict>
        <!-- Menu End -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.choosefrommenu</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>GroupingIdentifier</key>
                <string>DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD</string>
                <key>WFControlFlowMode</key>
                <integer>2</integer>
            </dict>
        </dict>
    </array>
    <key>WFWorkflowClientVersion</key>
    <string>2700.0.4</string>
    <key>WFWorkflowHasOutputFallback</key>
    <false/>
    <key>WFWorkflowIcon</key>
    <dict>
        <key>WFWorkflowIconGlyphNumber</key>
        <integer>59511</integer>
        <key>WFWorkflowIconStartColor</key>
        <integer>4282601983</integer>
    </dict>
    <key>WFWorkflowImportQuestions</key>
    <array/>
    <key>WFWorkflowMinimumClientVersion</key>
    <integer>900</integer>
    <key>WFWorkflowMinimumClientVersionString</key>
    <string>900</string>
    <key>WFWorkflowName</key>
    <string>Menu Demo</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## Example 5: Weather + AI Report

Gets current weather and uses AI to generate a friendly report.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>WFWorkflowActions</key>
    <array>
        <!-- Get Weather -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.weather.currentconditions</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>EEEEEEEE-EEEE-EEEE-EEEE-EEEEEEEEEEEE</string>
            </dict>
        </dict>
        <!-- Build Prompt -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.gettext</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF</string>
                <key>WFTextActionText</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{56, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Weather Conditions</string>
                                <key>OutputUUID</key>
                                <string>EEEEEEEE-EEEE-EEEE-EEEE-EEEEEEEEEEEE</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>Generate a friendly weather report based on this data:
￼

Keep it brief and include clothing recommendations.</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
        <!-- Ask AI -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.askllm</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>UUID</key>
                <string>GGGGGGGG-GGGG-GGGG-GGGG-GGGGGGGGGGGG</string>
                <key>WFLLMModel</key>
                <string>Apple Intelligence</string>
                <key>WFGenerativeResultType</key>
                <string>Text</string>
                <key>WFLLMPrompt</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{0, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Text</string>
                                <key>OutputUUID</key>
                                <string>FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>￼</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
        <!-- Show Result -->
        <dict>
            <key>WFWorkflowActionIdentifier</key>
            <string>is.workflow.actions.showresult</string>
            <key>WFWorkflowActionParameters</key>
            <dict>
                <key>Text</key>
                <dict>
                    <key>Value</key>
                    <dict>
                        <key>attachmentsByRange</key>
                        <dict>
                            <key>{0, 1}</key>
                            <dict>
                                <key>OutputName</key>
                                <string>Response</string>
                                <key>OutputUUID</key>
                                <string>GGGGGGGG-GGGG-GGGG-GGGG-GGGGGGGGGGGG</string>
                                <key>Type</key>
                                <string>ActionOutput</string>
                            </dict>
                        </dict>
                        <key>string</key>
                        <string>￼</string>
                    </dict>
                    <key>WFSerializationType</key>
                    <string>WFTextTokenString</string>
                </dict>
            </dict>
        </dict>
    </array>
    <key>WFWorkflowClientVersion</key>
    <string>2700.0.4</string>
    <key>WFWorkflowHasOutputFallback</key>
    <false/>
    <key>WFWorkflowIcon</key>
    <dict>
        <key>WFWorkflowIconGlyphNumber</key>
        <integer>59511</integer>
        <key>WFWorkflowIconStartColor</key>
        <integer>4282601983</integer>
    </dict>
    <key>WFWorkflowImportQuestions</key>
    <array/>
    <key>WFWorkflowMinimumClientVersion</key>
    <integer>900</integer>
    <key>WFWorkflowMinimumClientVersionString</key>
    <string>900</string>
    <key>WFWorkflowName</key>
    <string>Weather Report</string>
    <key>WFWorkflowOutputContentItemClasses</key>
    <array/>
    <key>WFWorkflowTypes</key>
    <array/>
</dict>
</plist>
```

---

## How to Use These Examples

1. **Copy** the XML content
2. **Save** to a file with `.shortcut` extension (e.g., `HelloWorld.shortcut`)
3. **Sign** using the shortcuts CLI:
   ```bash
   shortcuts sign --mode anyone --input HelloWorld.shortcut --output HelloWorld.shortcut
   ```
4. **Import** by double-clicking the signed file or dragging to Shortcuts.app

---

## Python-Generated Raw Plist Examples

These examples use the Python binary plist approach. They are production-tested patterns.

### DOCX from Markdown via SSH (Tailscale + Base64 Transfer)

Demonstrates: Tailscale device picker, IPv4 aggrandizement, SSH + base64 binary transfer, LLM filename generation, document save+rename.

```python
import plistlib, uuid

def new_uuid():
    return str(uuid.uuid4()).upper()

def action_ref(output_uuid, output_name):
    return {
        "Value": {"OutputUUID": output_uuid, "Type": "ActionOutput", "OutputName": output_name},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def var_ref(name):
    return {
        "Value": {"VariableName": name, "Type": "Variable"},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def text_with_var(var_name):
    return {
        "Value": {
            "string": "\ufffc",
            "attachmentsByRange": {"{0, 1}": {"VariableName": var_name, "Type": "Variable"}}
        },
        "WFSerializationType": "WFTextTokenString"
    }

U_tailscale = new_uuid()
U_choose    = new_uuid()
U_clipboard = new_uuid()
U_llm       = new_uuid()
U_ip_var    = new_uuid()   # placeholder (setvariable has no output UUID for aggrandizement)
U_ssh       = new_uuid()
U_b64       = new_uuid()
U_save      = new_uuid()

REFERENCE_DOCX = "~/Documents/reference-template.docx"  # adjust to your path

actions = [
    # 1. Get Tailscale devices
    {
        "WFWorkflowActionIdentifier": "io.tailscale.ipn.ios.DeviceAppEntity",
        "WFWorkflowActionParameters": {
            "UUID": U_tailscale,
            "AppIntentDescriptor": {
                "TeamIdentifier": "W5364U7YZB",
                "BundleIdentifier": "io.tailscale.ipn.ios",
                "Name": "Tailscale",
                "AppIntentIdentifier": "DeviceAppEntity",
                "ActionRequiresAppInstallation": True
            }
        }
    },
    # 2. Choose a device
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.choosefromlist",
        "WFWorkflowActionParameters": {
            "UUID": U_choose,
            "WFInput": action_ref(U_tailscale, "Devices"),
            "WFChooseFromListActionPrompt": "Select Mac"
        }
    },
    # 3. Store clipboard as Markdown variable
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
        "WFWorkflowActionParameters": {
            "UUID": U_clipboard,
            "WFInput": {"Value": {"Type": "Clipboard"}, "WFSerializationType": "WFTextTokenAttachment"},
            "WFVariableName": "Markdown"
        }
    },
    # 4. Generate filename with LLM
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.askllm",
        "WFWorkflowActionParameters": {
            "UUID": U_llm,
            "WFLLMModel": "Apple Intelligence",
            "WFGenerativeResultType": "Text",
            "WFLLMPrompt": {
                "Value": {
                    "string": "Generate a short filename (no extension, no spaces, use hyphens) for this document:\n\ufffc",
                    "attachmentsByRange": {"{74, 1}": {"VariableName": "Markdown", "Type": "Variable"}}
                },
                "WFSerializationType": "WFTextTokenString"
            }
        }
    },
    # 5. Store filename
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
        "WFWorkflowActionParameters": {
            "WFInput": action_ref(U_llm, "Response"),
            "WFVariableName": "Filename"
        }
    },
    # 6. SSH: pandoc convert and base64-encode result
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.runsshscript",
        "WFWorkflowActionParameters": {
            "UUID": U_ssh,
            "WFSSHScript": {
                "Value": {
                    "string": f"cat << 'MARKDOWN_EOF'\n\ufffc\nMARKDOWN_EOF\n\npandoc --from=markdown --to=docx --reference-doc={REFERENCE_DOCX} --syntax-highlighting=none --output=/dev/stdout | base64",
                    "attachmentsByRange": {"{18, 1}": {"VariableName": "Markdown", "Type": "Variable"}}
                },
                "WFSerializationType": "WFTextTokenString"
            },
            "WFSSHHost": {
                "Value": {
                    "OutputUUID": U_choose,
                    "Type": "ActionOutput",
                    "OutputName": "Selected Item",
                    "Aggrandizements": [{
                        "Type": "WFPropertyVariableAggrandizement",
                        "PropertyName": "ipv4Address",
                        "PropertyUserInfo": {
                            "WFLinkEntityContentPropertyUserInfoPropertyIdentifier": "ipv4Address"
                        }
                    }]
                },
                "WFSerializationType": "WFTextTokenAttachment"
            },
            "WFSSHUser": "your-username",  # replace with your SSH username
            "WFSSHAuthentication": "PrivateKey"
        }
    },
    # 7. Decode base64 → binary DOCX
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.base64encode",
        "WFWorkflowActionParameters": {
            "UUID": U_b64,
            "WFInput": action_ref(U_ssh, "Shell Script Result"),
            "WFEncoding": "Decode",
            "WFBase64LineBreakMode": "None"
        }
    },
    # 8. Preview
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.previewdocument",
        "WFWorkflowActionParameters": {
            "WFInput": action_ref(U_b64, "Base64 Encoded")
        }
    },
    # 9. Save to Files
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.documentpicker.save",
        "WFWorkflowActionParameters": {
            "UUID": U_save,
            "WFFileDestination": "iCloud Drive",
            "WFSaveFileOverwrite": False
        }
    },
    # 10. Rename with LLM-generated filename
    {
        "WFWorkflowActionIdentifier": "is.workflow.actions.file.rename",
        "WFWorkflowActionParameters": {
            "WFFile": action_ref(U_save, "File"),
            "WFNewFilename": text_with_var("Filename")
        }
    }
]

shortcut = {
    "WFWorkflowActions": actions,
    "WFWorkflowClientVersion": "1343.4",
    "WFWorkflowHasOutputFallback": False,
    "WFWorkflowIcon": {"WFWorkflowIconStartColor": 4071891967, "WFWorkflowIconGlyphNumber": 59511},
    "WFWorkflowImportQuestions": [],
    "WFWorkflowInputContentItemClasses": [],
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowName": "DOCX from Markdown via SSH",
    "WFWorkflowNoInputBehavior": {"Name": "WFWorkflowNoInputBehaviorAskForInput", "Parameters": {}},
    "WFWorkflowOutputContentItemClasses": [],
    "WFWorkflowTypes": []
}

with open("/tmp/DOCX_from_Markdown_via_SSH.shortcut", "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)
```

Then sign: `shortcuts sign --mode anyone --input /tmp/DOCX_from_Markdown_via_SSH.shortcut --output ~/Desktop/DOCX\ from\ Markdown\ via\ SSH.shortcut`

---

### Save Page Images to Note (JavaScript Web Scraping + Multi-Select + Notes AppIntents)

Demonstrates: `runjavascriptonwebpage`, `WFSafariWebPageContentItem` input, multi-select `choosefromlist`,
`filter.notes` (correct identifier — NOT `findnotes`), `repeat.each` with `GroupingIdentifier`,
`image.convert`, `appendnote` — all with required `AppIntentDescriptor` for Notes actions.

> **CRITICAL — Notes actions require `AppIntentDescriptor`**
>
> Both `filter.notes` and `appendnote` will show as "Unknown Action" without `AppIntentDescriptor`.
> Use these exact values:
> ```python
> NOTES_FILTER_INTENT = {
>     "TeamIdentifier": "0000000000",
>     "BundleIdentifier": "com.apple.mobilenotes",
>     "Name": "Notes",
>     "AppIntentIdentifier": "NoteEntity",
>     "ActionRequiresAppInstallation": True
> }
> NOTES_APPEND_INTENT = {
>     "TeamIdentifier": "0000000000",
>     "BundleIdentifier": "com.apple.mobilenotes",
>     "Name": "Notes",
>     "AppIntentIdentifier": "AppendToNoteLinkAction"
> }
> ```
> The output name from `filter.notes` is `"Note"` (singular), not `"Notes"`.

> **CRITICAL — repeat.each structure**
>
> The end of a `repeat.each` loop uses the **same identifier** `is.workflow.actions.repeat.each`
> with `WFControlFlowMode: 2` — there is NO separate `repeat.each.end` action.
> Both start (mode 0) and end (mode 2) must share the same `GroupingIdentifier` UUID.

```python
import plistlib, uuid, subprocess, os

def new_uuid():
    return str(uuid.uuid4()).upper()

def action_ref(output_uuid, output_name):
    return {
        "Value": {"OutputUUID": output_uuid, "Type": "ActionOutput", "OutputName": output_name},
        "WFSerializationType": "WFTextTokenAttachment"
    }

def var_ref(name):
    return {
        "Value": {"VariableName": name, "Type": "Variable"},
        "WFSerializationType": "WFTextTokenAttachment"
    }

U_js          = new_uuid()
U_choose_imgs = new_uuid()
U_find_notes  = new_uuid()
U_choose_note = new_uuid()
U_download    = new_uuid()
U_convert     = new_uuid()
REPEAT_GUID   = new_uuid()   # shared GroupingIdentifier for repeat start/end

# AppIntentDescriptor values for Apple Notes — required for filter.notes and appendnote
NOTES_FILTER_INTENT = {
    "TeamIdentifier": "0000000000",
    "BundleIdentifier": "com.apple.mobilenotes",
    "Name": "Notes",
    "AppIntentIdentifier": "NoteEntity",
    "ActionRequiresAppInstallation": True
}
NOTES_APPEND_INTENT = {
    "TeamIdentifier": "0000000000",
    "BundleIdentifier": "com.apple.mobilenotes",
    "Name": "Notes",
    "AppIntentIdentifier": "AppendToNoteLinkAction"
}

JS = r"""
(function() {
  var urls = new Set();

  // 1. Performance API — captures ALL loaded resources (img, CSS bg, lazy, preload)
  if (window.performance && window.performance.getEntriesByType) {
    window.performance.getEntriesByType('resource').forEach(function(e) {
      var u = e.name;
      if (u && (u.match(/\.(jpg|jpeg|png|webp|avif|gif)(\?|$)/i) || e.initiatorType === 'img')) {
        urls.add(u);
      }
    });
  }

  // 2. DOM img tags — Cloudinary-safe srcset split (commas in transform params)
  function parseSrcset(srcset) {
    var results = [];
    var parts = srcset.split(/,\s*(?=https?:\/\/|\/\/)/);
    parts.forEach(function(part) {
      part = part.trim();
      var tokens = part.split(/\s+/);
      if (tokens[0] && (tokens[0].startsWith('http') || tokens[0].startsWith('//'))) {
        results.push({ url: tokens[0], w: tokens[1] ? parseFloat(tokens[1]) : 0 });
      }
    });
    results.sort(function(a, b) { return b.w - a.w; });
    return results.length > 0 ? results[0].url : null;
  }
  document.querySelectorAll('img').forEach(function(img) {
    var srcset = img.srcset || img.getAttribute('data-srcset');
    if (srcset) { var best = parseSrcset(srcset); if (best) { urls.add(best); return; } }
    var src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src')
           || img.getAttribute('data-original') || img.getAttribute('data-image');
    if (src && !src.startsWith('data:')) urls.add(src);
  });

  // 3. picture source elements
  document.querySelectorAll('picture source').forEach(function(s) {
    var srcset = s.srcset || s.getAttribute('data-srcset');
    if (!srcset) return;
    var best = parseSrcset(srcset);
    if (best) urls.add(best);
  });

  // 4. CSS background-image (hero carousels, banners, sliders)
  function extractBgUrl(bg) {
    if (!bg || bg === 'none') return null;
    var m = bg.match(/url\(['"']?([^'")\s]+)['"']?\)/);
    return m ? m[1] : null;
  }
  var bgSelectors = 'section,header,figure,article,[class*="hero"],[class*="banner"],[class*="slide"],[class*="carousel"],[class*="promo"],[class*="cover"],[class*="featured"],div[style*="background"]';
  document.querySelectorAll(bgSelectors).forEach(function(el) {
    var u = extractBgUrl(el.style.backgroundImage);
    if (!u) { try { u = extractBgUrl(window.getComputedStyle(el).backgroundImage); } catch(e){} }
    if (u && !u.startsWith('data:') && !u.startsWith('blob:')) urls.add(u);
  });

  // 5. Resolution upgrade — request max from each CDN
  function upgradeResolution(u) {
    u = u.replace(/\/upload\/([^/]*,)?w_\d+([^/]*)\//g, function(m,pre,post){ return '/upload/'+(pre||'')+'w_9999'+post+'/'; });
    u = u.replace(/_(\d{2,4}x\d{0,4}|small|medium|compact|grande)(\.[a-z]+)(\?|$)/gi, '$2$3');
    u = u.replace(/-\d{2,4}x\d{2,4}(\.[a-z]+)(\?|$)/i, '$1$2');
    u = u.replace(/([?&])w=\d+(&?)/g, function(m,sep,trail){ return trail ? sep : ''; });
    u = u.replace(/([?&])width=\d+(&?)/g, function(m,sep,trail){ return trail ? sep : ''; });
    return u.replace(/[?&]$/, '');
  }

  // 6. Filter: require image extension + remove icons/swatches/flags/spinners
  var imageExt = /\.(jpg|jpeg|png|webp|avif|gif)(\?|$)/i;
  var junkPattern = /favicon|sprite|arrow|chevron|close-btn|\.ico$|\.svg$|1x1|pixel|blank|spacer|loading|spinner|placeholder|\/flags\/|-flag\.|swatch|50x50|care-icon|\/icons\//i;
  var results = Array.from(urls).filter(function(u) {
    if (!u || u.startsWith('data:') || u.startsWith('blob:')) return false;
    var path = u.split('?')[0];
    if (!imageExt.test(path)) return false;   // must have image extension
    return !junkPattern.test(path);
  }).map(upgradeResolution);

  var seen = new Set();
  completion(results.filter(function(u){ if(seen.has(u)) return false; seen.add(u); return true; }).slice(0,100));
})();
"""

actions = [
    {"WFWorkflowActionIdentifier": "is.workflow.actions.comment",
     "WFWorkflowActionParameters": {"WFCommentActionText": "Save Page Images to Note\n\nRun from Safari share sheet. JS extracts images via:\n- Performance API (lazy/CSS/preload)\n- img/picture/srcset (Cloudinary-safe comma split)\n- CSS background-image (hero carousels)\n- Max-resolution CDN upgrade\nDownloads each image, converts to HEIF (lossless), appends to chosen Apple Note."}},

    # 1. Run JavaScript on the Safari webpage
    {"WFWorkflowActionIdentifier": "is.workflow.actions.runjavascriptonwebpage",
     "WFWorkflowActionParameters": {"UUID": U_js, "WFJavaScript": JS}},

    # 2. Multi-select images
    {"WFWorkflowActionIdentifier": "is.workflow.actions.choosefromlist",
     "WFWorkflowActionParameters": {
         "UUID": U_choose_imgs,
         "WFChooseFromListActionPrompt": "Select images to save",
         "WFChooseFromListActionSelectMultiple": True,
         "WFInput": action_ref(U_js, "JavaScript Result")
     }},

    # 3. Find all notes — identifier is filter.notes (NOT findnotes), requires AppIntentDescriptor
    #    Output name is "Note" (singular)
    {"WFWorkflowActionIdentifier": "is.workflow.actions.filter.notes",
     "WFWorkflowActionParameters": {
         "UUID": U_find_notes,
         "WFContentItemFilter": {
             "Value": {
                 "WFActionParameterFilterPrefix": 1,
                 "WFActionParameterFilterTemplates": [],
                 "WFContentItemSortProperty": "Title",
                 "WFContentItemSortOrder": "Ascending"
             },
             "WFSerializationType": "WFContentPredicateTableTemplate"
         },
         "AppIntentDescriptor": NOTES_FILTER_INTENT
     }},

    # 4. Choose destination note (output of filter.notes is "Note", not "Notes")
    {"WFWorkflowActionIdentifier": "is.workflow.actions.choosefromlist",
     "WFWorkflowActionParameters": {
         "UUID": U_choose_note,
         "WFInput": action_ref(U_find_notes, "Note"),
         "WFChooseFromListActionPrompt": "Append images to which note?"
     }},

    # 5. Store chosen note as variable
    {"WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
     "WFWorkflowActionParameters": {
         "WFInput": action_ref(U_choose_note, "Chosen Item"),
         "WFVariableName": "DestNote"
     }},

    # 6. Repeat each — start (mode 0). GroupingIdentifier links start to end.
    {"WFWorkflowActionIdentifier": "is.workflow.actions.repeat.each",
     "WFWorkflowActionParameters": {
         "WFInput": action_ref(U_choose_imgs, "Chosen Item"),
         "GroupingIdentifier": REPEAT_GUID,
         "WFControlFlowMode": 0
     }},

    # 7. Download image ("Repeat Item" is a Variable, not ActionOutput)
    {"WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
     "WFWorkflowActionParameters": {
         "UUID": U_download,
         "WFURL": var_ref("Repeat Item")
     }},

    # 8. Convert to HEIF (lossless, preserves metadata)
    {"WFWorkflowActionIdentifier": "is.workflow.actions.image.convert",
     "WFWorkflowActionParameters": {
         "UUID": U_convert,
         "WFImageFormat": "HEIF",
         "WFImagePreserveMetadata": True,
         "WFInput": action_ref(U_download, "Contents of URL")
     }},

    # 9. Append HEIF image to note — requires AppIntentDescriptor
    {"WFWorkflowActionIdentifier": "is.workflow.actions.appendnote",
     "WFWorkflowActionParameters": {
         "WFInput": action_ref(U_convert, "Converted Image"),
         "WFNote": var_ref("DestNote"),
         "AppIntentDescriptor": NOTES_APPEND_INTENT
     }},

    # 10. Repeat each — end. SAME identifier as start, mode 2, SAME GroupingIdentifier.
    #     There is NO separate repeat.each.end action.
    {"WFWorkflowActionIdentifier": "is.workflow.actions.repeat.each",
     "WFWorkflowActionParameters": {
         "WFControlFlowMode": 2,
         "GroupingIdentifier": REPEAT_GUID
     }}
]

shortcut = {
    "WFWorkflowActions": actions,
    "WFWorkflowClientVersion": "1343.4",
    "WFWorkflowHasOutputFallback": False,
    "WFWorkflowIcon": {"WFWorkflowIconStartColor": 3031607807, "WFWorkflowIconGlyphNumber": 61459},
    "WFWorkflowImportQuestions": [],
    "WFWorkflowInputContentItemClasses": ["WFSafariWebPageContentItem"],
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowName": "Save Page Images to Note",
    "WFWorkflowNoInputBehavior": {"Name": "WFWorkflowNoInputBehaviorAskForInput", "Parameters": {}},
    "WFWorkflowOutputContentItemClasses": [],
    "WFWorkflowTypes": []
}

tmp = "/tmp/Save_Page_Images_to_Note.shortcut"
out = os.path.expanduser("~/Desktop/Save Page Images to Note.shortcut")
with open(tmp, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)
subprocess.run(["shortcuts", "sign", "--mode", "anyone", "--input", tmp, "--output", out])
```
