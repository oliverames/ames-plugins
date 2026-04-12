#!/usr/bin/env python3
"""Build the Smart Transcribe shortcut plist.

Creates an unsigned XML .shortcut file that:
- Prompts for AssemblyAI + Mistral keys on import
- Transcribes audio via AssemblyAI + Mistral
- Merges with built-in Use Model action (Apple Intelligence)
- Saves transcript + audio copy into a chosen folder
"""

from __future__ import annotations

import argparse
import plistlib
import uuid
from pathlib import Path

PLACEHOLDER = "\uFFFC"


def u() -> str:
    return str(uuid.uuid4()).upper()


def attach_variable(name: str) -> dict:
    return {
        "Type": "Variable",
        "VariableName": name,
    }


def attach_output(action_uuid: str, output_name: str) -> dict:
    return {
        "Type": "ActionOutput",
        "OutputUUID": action_uuid,
        "OutputName": output_name,
    }


def wf_text_token_attachment(attachment: dict) -> dict:
    return {
        "Value": attachment,
        "WFSerializationType": "WFTextTokenAttachment",
    }


def wf_text_token_string_from_parts(parts: list[object]) -> dict:
    """Build a WFTextTokenString from string + attachment parts.

    Each non-string part must be a token attachment dict.
    """
    text = ""
    attachments: dict[str, dict] = {}

    for part in parts:
        if isinstance(part, str):
            text += part
        elif isinstance(part, dict):
            idx = len(text)
            text += PLACEHOLDER
            attachments[f"{{{idx}, 1}}"] = part
        else:
            raise TypeError(f"Unsupported part type: {type(part)!r}")

    return {
        "Value": {
            "attachmentsByRange": attachments,
            "string": text,
        },
        "WFSerializationType": "WFTextTokenString",
    }


def wf_tts_from_text(text: str) -> dict:
    return wf_text_token_string_from_parts([text])


def condition_input_from_variable(variable_name: str) -> dict:
    """Editor-friendly If input wrapper required for conditional start actions."""
    return {
        "Type": "Variable",
        "Variable": {
            "Value": {
                "Type": "Variable",
                "VariableName": variable_name,
            },
            "WFSerializationType": "WFTextTokenAttachment",
        },
    }


def dict_field_value(items: list[dict]) -> dict:
    return {
        "Value": {
            "WFDictionaryFieldValueItems": items,
        },
        "WFSerializationType": "WFDictionaryFieldValue",
    }


def dict_item_text(key: str, value_state: dict) -> dict:
    return {
        "WFItemType": 0,
        "WFKey": wf_tts_from_text(key),
        "WFValue": value_state,
    }


def dict_item_file(key: str, variable_name: str) -> dict:
    return {
        "WFItemType": 5,
        "WFKey": wf_tts_from_text(key),
        "WFValue": {
            "Value": {
                "Value": {
                    "Type": "Variable",
                    "VariableName": variable_name,
                },
                "WFSerializationType": "WFTextTokenAttachment",
            },
            "WFSerializationType": "WFTokenAttachmentParameterState",
        },
    }


def action(identifier: str, parameters: dict | None = None) -> dict:
    return {
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": parameters or {},
    }


def comment(text: str) -> dict:
    return action(
        "is.workflow.actions.comment",
        {
            "WFCommentActionText": text,
        },
    )


def build_shortcut(icon_glyph: int, icon_color: int) -> dict:
    # UUIDs reused by references.
    KEY_ASSEMBLY_UUID = u()
    KEY_MISTRAL_UUID = u()

    AUDIO_SELECT_UUID = u()
    ASK_SPEAKERS_UUID = u()
    ASK_DESC_UUID = u()

    ASM_UPLOAD_REQ_UUID = u()
    ASM_UPLOAD_DICT_UUID = u()
    ASM_UPLOAD_URL_UUID = u()

    ASM_SUBMIT_REQ_UUID = u()
    ASM_SUBMIT_DICT_UUID = u()
    ASM_JOB_ID_UUID = u()

    ASM_POLL_REQ_UUID = u()
    ASM_POLL_DICT_UUID = u()
    ASM_POLL_STATUS_UUID = u()
    ASM_POLL_ERROR_UUID = u()
    ASM_TEXT_UUID = u()

    MISTRAL_REQ_UUID = u()
    MISTRAL_DICT_UUID = u()
    MISTRAL_TEXT_UUID = u()

    MERGE_PROMPT_UUID = u()
    MERGE_LLM_UUID = u()

    TITLE_PROMPT_UUID = u()
    TITLE_LLM_UUID = u()
    TITLE_TRIM_UUID = u()

    TITLE_SANITIZE_UUID = u()
    TITLE_SANITIZE_TRIM_UUID = u()

    DATE_NOW_UUID = u()
    DATE_FORMAT_UUID = u()
    BASENAME_UUID = u()
    MD_TEXT_UUID = u()
    TRANSCRIPT_NAME_UUID = u()
    AUDIO_NAME_UUID = u()
    DEFAULT_TITLE_UUID = u()

    OUTPUT_FOLDER_UUID = u()

    GROUP_REPEAT_POLL = u()
    GROUP_IF_POLL_SKIP = u()
    GROUP_IF_POLL_DONE = u()
    GROUP_IF_POLL_ERROR = u()
    GROUP_IF_DONE_FINAL = u()
    GROUP_IF_MISTRAL = u()
    GROUP_IF_TITLE_SOURCE = u()
    GROUP_IF_CLEAN_TITLE = u()

    actions: list[dict] = []

    # 0
    actions.append(
        comment(
            "Smart Transcribe: dual-engine transcription using AssemblyAI and Mistral, then a built-in Use Model merge.\n"
            "- Select one audio file\n"
            "- Poll AssemblyAI until complete\n"
            "- Merge with Apple Intelligence\n"
            "- Save Markdown transcript + renamed audio copy\n"
            "ALLOW_MANUAL_UNIT_CONVERSION"
        )
    )

    # 1
    actions.append(
        comment(
            "Shortcuts generated by Shortcuts Playground. May contain mistakes. Always check the shortcut's actions first.\n\n"
            "This shortcut was created via the following user prompt:\n\n"
            "> Please recreate the smart-transcribe skill into a Shortcut. "
            "We can use the built-in use model for the merge instead of Gemini. Should ask for API keys on import. "
            "This'll be a big one so go through carefully and ensure it'll work!"
        )
    )

    # 2
    actions.append(
        comment(
            "--- CONFIG ---\n"
            "- API keys are requested at import time from the two Text actions below.\n"
            "- Keep these values private."
        )
    )

    # 3: Assembly key text (import question target)
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": KEY_ASSEMBLY_UUID,
                "WFTextActionText": "PASTE_ASSEMBLYAI_API_KEY",
            },
        )
    )

    # 4: Mistral key text (import question target)
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": KEY_MISTRAL_UUID,
                "WFTextActionText": "PASTE_MISTRAL_API_KEY",
            },
        )
    )

    # 5
    actions.append(
        comment(
            "--- INPUTS ---\n"
            "- Select one audio file\n"
            "- Optional speaker hint list\n"
            "- Optional custom title override"
        )
    )

    # 6: select audio
    actions.append(
        action(
            "is.workflow.actions.file.select",
            {
                "UUID": AUDIO_SELECT_UUID,
                "CustomOutputName": "Selected Audio File",
                "SelectMultiple": False,
            },
        )
    )

    # 7: persist selected audio as named variable
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Selected Audio File",
                "WFInput": wf_text_token_attachment(
                    attach_output(AUDIO_SELECT_UUID, "Selected Audio File")
                ),
            },
        )
    )

    # 8: optional speaker hints
    actions.append(
        action(
            "is.workflow.actions.ask",
            {
                "UUID": ASK_SPEAKERS_UUID,
                "WFAskActionPrompt": "Known speakers (optional, comma-separated)",
                "WFInputType": "Text",
            },
        )
    )

    # 9
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Speaker Hints",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASK_SPEAKERS_UUID, "Provided Input")
                ),
            },
        )
    )

    # 10: optional user description override
    actions.append(
        action(
            "is.workflow.actions.ask",
            {
                "UUID": ASK_DESC_UUID,
                "WFAskActionPrompt": "Title override (optional). Leave blank for AI-generated title.",
                "WFInputType": "Text",
            },
        )
    )

    # 11
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "User Description",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASK_DESC_UUID, "Provided Input")
                ),
            },
        )
    )

    # 12
    actions.append(
        comment(
            "--- ASSEMBLYAI UPLOAD ---\n"
            "- Upload selected audio to AssemblyAI upload endpoint\n"
            "- Extract upload_url"
        )
    )

    # 13: Assembly upload request
    actions.append(
        action(
            "is.workflow.actions.downloadurl",
            {
                "UUID": ASM_UPLOAD_REQ_UUID,
                "Advanced": True,
                "ShowHeaders": False,
                "WFURL": "https://api.assemblyai.com/v2/upload",
                "WFHTTPMethod": "POST",
                "WFHTTPBodyType": "File",
                "WFHTTPHeaders": dict_field_value(
                    [
                        dict_item_text(
                            "authorization",
                            wf_text_token_string_from_parts(
                                [attach_output(KEY_ASSEMBLY_UUID, "Text")]
                            ),
                        )
                    ]
                ),
                "WFFormValues": dict_field_value([]),
                "WFRequestVariable": wf_text_token_string_from_parts(
                    [attach_variable("Selected Audio File")]
                ),
            },
        )
    )

    # 14
    actions.append(
        action(
            "is.workflow.actions.detect.dictionary",
            {
                "UUID": ASM_UPLOAD_DICT_UUID,
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_UPLOAD_REQ_UUID, "Contents of URL")
                ),
            },
        )
    )

    # 15
    actions.append(
        action(
            "is.workflow.actions.getvalueforkey",
            {
                "UUID": ASM_UPLOAD_URL_UUID,
                "WFDictionaryKey": "upload_url",
                "WFGetDictionaryValueType": "Value",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_UPLOAD_DICT_UUID, "Dictionary")
                ),
            },
        )
    )

    # 16
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Assembly Upload URL",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_UPLOAD_URL_UUID, "Dictionary Value")
                ),
            },
        )
    )

    # 17
    actions.append(
        comment(
            "--- ASSEMBLYAI SUBMIT JOB ---\n"
            "- Submit transcript request with uploaded audio URL\n"
            "- Extract transcript job id"
        )
    )

    # 18: submit transcript job (minimal required payload for reliability)
    actions.append(
        action(
            "is.workflow.actions.downloadurl",
            {
                "UUID": ASM_SUBMIT_REQ_UUID,
                "Advanced": True,
                "ShowHeaders": False,
                "WFURL": "https://api.assemblyai.com/v2/transcript",
                "WFHTTPMethod": "POST",
                "WFHTTPBodyType": "JSON",
                "WFHTTPHeaders": dict_field_value(
                    [
                        dict_item_text(
                            "authorization",
                            wf_text_token_string_from_parts(
                                [attach_output(KEY_ASSEMBLY_UUID, "Text")]
                            ),
                        ),
                        dict_item_text("content-type", wf_tts_from_text("application/json")),
                    ]
                ),
                "WFJSONValues": dict_field_value(
                    [
                        dict_item_text(
                            "audio_url",
                            wf_text_token_string_from_parts(
                                [attach_variable("Assembly Upload URL")]
                            ),
                        )
                    ]
                ),
            },
        )
    )

    # 19
    actions.append(
        action(
            "is.workflow.actions.detect.dictionary",
            {
                "UUID": ASM_SUBMIT_DICT_UUID,
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_SUBMIT_REQ_UUID, "Contents of URL")
                ),
            },
        )
    )

    # 20
    actions.append(
        action(
            "is.workflow.actions.getvalueforkey",
            {
                "UUID": ASM_JOB_ID_UUID,
                "WFDictionaryKey": "id",
                "WFGetDictionaryValueType": "Value",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_SUBMIT_DICT_UUID, "Dictionary")
                ),
            },
        )
    )

    # 21
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Assembly Transcript ID",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_JOB_ID_UUID, "Dictionary Value")
                ),
            },
        )
    )

    # 22
    actions.append(
        comment(
            "--- ASSEMBLYAI POLL LOOP ---\n"
            "- Repeat up to 90 attempts\n"
            "- Skip polling once Assembly Done has value\n"
            "- On completed: store response\n"
            "- On error: alert and stop"
        )
    )

    # 23: repeat start
    actions.append(
        action(
            "is.workflow.actions.repeat.count",
            {
                "GroupingIdentifier": GROUP_REPEAT_POLL,
                "WFControlFlowMode": 0,
                "WFRepeatCount": 90,
            },
        )
    )

    # 24
    actions.append(
        comment(
            "- If Assembly Done already has value, do nothing\n"
            "- Otherwise continue polling"
        )
    )

    # 25: if Assembly Done has any value
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_SKIP,
                "WFControlFlowMode": 0,
                "WFCondition": 100,
                "WFInput": condition_input_from_variable("Assembly Done"),
            },
        )
    )

    # 26
    actions.append(action("is.workflow.actions.nothing", {}))

    # 27: otherwise
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_SKIP,
                "WFControlFlowMode": 1,
            },
        )
    )

    # 28
    actions.append(
        comment(
            "- GET transcript status using Assembly Transcript ID\n"
            "- Persist response + status"
        )
    )

    # 29: poll request
    actions.append(
        action(
            "is.workflow.actions.downloadurl",
            {
                "UUID": ASM_POLL_REQ_UUID,
                "Advanced": True,
                "ShowHeaders": False,
                "WFHTTPMethod": "GET",
                "WFURL": wf_text_token_string_from_parts(
                    [
                        "https://api.assemblyai.com/v2/transcript/",
                        attach_variable("Assembly Transcript ID"),
                    ]
                ),
                "WFHTTPHeaders": dict_field_value(
                    [
                        dict_item_text(
                            "authorization",
                            wf_text_token_string_from_parts(
                                [attach_output(KEY_ASSEMBLY_UUID, "Text")]
                            ),
                        )
                    ]
                ),
            },
        )
    )

    # 30
    actions.append(
        action(
            "is.workflow.actions.detect.dictionary",
            {
                "UUID": ASM_POLL_DICT_UUID,
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_POLL_REQ_UUID, "Contents of URL")
                ),
            },
        )
    )

    # 31
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Assembly Poll Response",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_POLL_DICT_UUID, "Dictionary")
                ),
            },
        )
    )

    # 32
    actions.append(
        action(
            "is.workflow.actions.getvalueforkey",
            {
                "UUID": ASM_POLL_STATUS_UUID,
                "WFDictionaryKey": "status",
                "WFGetDictionaryValueType": "Value",
                "WFInput": wf_text_token_attachment(attach_variable("Assembly Poll Response")),
            },
        )
    )

    # 33
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Assembly Status",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_POLL_STATUS_UUID, "Dictionary Value")
                ),
            },
        )
    )

    # 34
    actions.append(
        comment(
            "- If Assembly Status == completed, mark Assembly Done\n"
            "- Otherwise branch to error check"
        )
    )

    # 35: if status == completed
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_DONE,
                "WFControlFlowMode": 0,
                "WFCondition": 4,
                "WFConditionalActionString": "completed",
                "WFInput": condition_input_from_variable("Assembly Status"),
            },
        )
    )

    # 36
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Assembly Done",
                "WFInput": wf_text_token_attachment(attach_variable("Assembly Status")),
            },
        )
    )

    # 37: else
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_DONE,
                "WFControlFlowMode": 1,
            },
        )
    )

    # 38
    actions.append(
        comment(
            "- If Assembly Status == error, stop and show error message\n"
            "- Else wait 4 seconds before next poll"
        )
    )

    # 39: if status == error
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_ERROR,
                "WFControlFlowMode": 0,
                "WFCondition": 4,
                "WFConditionalActionString": "error",
                "WFInput": condition_input_from_variable("Assembly Status"),
            },
        )
    )

    # 40
    actions.append(
        action(
            "is.workflow.actions.getvalueforkey",
            {
                "UUID": ASM_POLL_ERROR_UUID,
                "WFDictionaryKey": "error",
                "WFGetDictionaryValueType": "Value",
                "WFInput": wf_text_token_attachment(attach_variable("Assembly Poll Response")),
            },
        )
    )

    # 41
    actions.append(
        action(
            "is.workflow.actions.alert",
            {
                "WFAlertActionTitle": "AssemblyAI Error",
                "WFAlertActionMessage": wf_text_token_string_from_parts(
                    [attach_output(ASM_POLL_ERROR_UUID, "Dictionary Value")]
                ),
            },
        )
    )

    # 42
    actions.append(action("is.workflow.actions.exit", {}))

    # 43: else
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_ERROR,
                "WFControlFlowMode": 1,
            },
        )
    )

    # 44
    actions.append(
        action(
            "is.workflow.actions.delay",
            {
                "WFDelayTime": 4,
            },
        )
    )

    # 45 end error if
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_ERROR,
                "WFControlFlowMode": 2,
            },
        )
    )

    # 46 end done if
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_DONE,
                "WFControlFlowMode": 2,
            },
        )
    )

    # 47 end skip-if
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_POLL_SKIP,
                "WFControlFlowMode": 2,
            },
        )
    )

    # 48 repeat end
    actions.append(
        action(
            "is.workflow.actions.repeat.count",
            {
                "GroupingIdentifier": GROUP_REPEAT_POLL,
                "WFControlFlowMode": 2,
            },
        )
    )

    # 49
    actions.append(
        comment(
            "- Confirm poll completed before continuing\n"
            "- Stop with timeout error otherwise"
        )
    )

    # 50 if Assembly Done has value
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_DONE_FINAL,
                "WFControlFlowMode": 0,
                "WFCondition": 100,
                "WFInput": condition_input_from_variable("Assembly Done"),
            },
        )
    )

    # 51
    actions.append(action("is.workflow.actions.nothing", {}))

    # 52 else
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_DONE_FINAL,
                "WFControlFlowMode": 1,
            },
        )
    )

    # 53
    actions.append(
        action(
            "is.workflow.actions.alert",
            {
                "WFAlertActionTitle": "AssemblyAI Timeout",
                "WFAlertActionMessage": "Polling ended before completion. Try again with a shorter audio file or rerun.",
            },
        )
    )

    # 54
    actions.append(action("is.workflow.actions.exit", {}))

    # 55 end
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_DONE_FINAL,
                "WFControlFlowMode": 2,
            },
        )
    )

    # 56
    actions.append(
        comment(
            "--- EXTRACT ASSEMBLY TRANSCRIPT ---\n"
            "- Read `text` from final Assembly Poll Response"
        )
    )

    # 57
    actions.append(
        action(
            "is.workflow.actions.getvalueforkey",
            {
                "UUID": ASM_TEXT_UUID,
                "WFDictionaryKey": "text",
                "WFGetDictionaryValueType": "Value",
                "WFInput": wf_text_token_attachment(attach_variable("Assembly Poll Response")),
            },
        )
    )

    # 58
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Assembly Transcript",
                "WFInput": wf_text_token_attachment(
                    attach_output(ASM_TEXT_UUID, "Dictionary Value")
                ),
            },
        )
    )

    # 59
    actions.append(
        comment(
            "--- MISTRAL TRANSCRIPTION ---\n"
            "- Send file to Mistral audio transcription endpoint\n"
            "- Extract `text`"
        )
    )

    # 60
    actions.append(
        action(
            "is.workflow.actions.downloadurl",
            {
                "UUID": MISTRAL_REQ_UUID,
                "Advanced": True,
                "ShowHeaders": False,
                "WFURL": "https://api.mistral.ai/v1/audio/transcriptions",
                "WFHTTPMethod": "POST",
                "WFHTTPBodyType": "Form",
                "WFHTTPHeaders": dict_field_value(
                    [
                        dict_item_text(
                            "authorization",
                            wf_text_token_string_from_parts(
                                [
                                    "Bearer ",
                                    attach_output(KEY_MISTRAL_UUID, "Text"),
                                ]
                            ),
                        )
                    ]
                ),
                "WFFormValues": dict_field_value(
                    [
                        dict_item_text("model", wf_tts_from_text("voxtral-mini-latest")),
                        dict_item_text("language", wf_tts_from_text("en")),
                        dict_item_file("file", "Selected Audio File"),
                    ]
                ),
                "WFRequestVariable": wf_text_token_string_from_parts(
                    [attach_variable("Selected Audio File")]
                ),
            },
        )
    )

    # 61
    actions.append(
        action(
            "is.workflow.actions.detect.dictionary",
            {
                "UUID": MISTRAL_DICT_UUID,
                "WFInput": wf_text_token_attachment(
                    attach_output(MISTRAL_REQ_UUID, "Contents of URL")
                ),
            },
        )
    )

    # 62
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Mistral Response",
                "WFInput": wf_text_token_attachment(
                    attach_output(MISTRAL_DICT_UUID, "Dictionary")
                ),
            },
        )
    )

    # 63
    actions.append(
        action(
            "is.workflow.actions.getvalueforkey",
            {
                "UUID": MISTRAL_TEXT_UUID,
                "WFDictionaryKey": "text",
                "WFGetDictionaryValueType": "Value",
                "WFInput": wf_text_token_attachment(attach_variable("Mistral Response")),
            },
        )
    )

    # 64
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Mistral Transcript",
                "WFInput": wf_text_token_attachment(
                    attach_output(MISTRAL_TEXT_UUID, "Dictionary Value")
                ),
            },
        )
    )

    # 65
    actions.append(
        comment(
            "- Ensure Mistral transcript has content before merge\n"
            "- Stop early if empty"
        )
    )

    # 66
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_MISTRAL,
                "WFControlFlowMode": 0,
                "WFCondition": 100,
                "WFInput": condition_input_from_variable("Mistral Transcript"),
            },
        )
    )

    # 67
    actions.append(action("is.workflow.actions.nothing", {}))

    # 68
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_MISTRAL,
                "WFControlFlowMode": 1,
            },
        )
    )

    # 69
    actions.append(
        action(
            "is.workflow.actions.alert",
            {
                "WFAlertActionTitle": "Mistral Error",
                "WFAlertActionMessage": "Mistral transcription returned no text.",
            },
        )
    )

    # 70
    actions.append(action("is.workflow.actions.exit", {}))

    # 71
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_MISTRAL,
                "WFControlFlowMode": 2,
            },
        )
    )

    # 72
    actions.append(
        comment(
            "--- BUILT-IN MERGE (USE MODEL) ---\n"
            "- Use Apple Intelligence to merge AssemblyAI + Mistral transcripts\n"
            "- Prefer Assembly structure and Mistral word accuracy\n"
            "- Return ONLY merged Markdown transcript"
        )
    )

    # 73
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": MERGE_PROMPT_UUID,
                "WFTextActionText": wf_text_token_string_from_parts(
                    [
                        "You are an expert transcription editor. Merge these two transcripts into one final Markdown transcript.\\n\\n"
                        "Guidelines:\\n"
                        "- Prefer AssemblyAI for structure, punctuation, and speaker formatting.\\n"
                        "- Prefer Mistral for word-level accuracy and proper nouns when they conflict.\\n"
                        "- If speaker names can be inferred from hints, replace generic labels when confident.\\n"
                        "- Return ONLY the merged transcript, no commentary.\\n\\n"
                        "Speaker hints (optional): ",
                        attach_variable("Speaker Hints"),
                        "\\n\\n### AssemblyAI Transcript\\n",
                        attach_variable("Assembly Transcript"),
                        "\\n\\n### Mistral Transcript\\n",
                        attach_variable("Mistral Transcript"),
                    ]
                ),
            },
        )
    )

    # 74
    actions.append(
        action(
            "is.workflow.actions.askllm",
            {
                "UUID": MERGE_LLM_UUID,
                "WFLLMModel": "Apple Intelligence",
                "WFGenerativeResultType": "Text",
                "WFLLMPrompt": wf_text_token_string_from_parts(
                    [attach_output(MERGE_PROMPT_UUID, "Text")]
                ),
            },
        )
    )

    # 75
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Merged Transcript",
                "WFInput": wf_text_token_attachment(
                    attach_output(MERGE_LLM_UUID, "Response")
                ),
            },
        )
    )

    # 76
    actions.append(
        comment(
            "- If User Description has value, use it as title\n"
            "- Otherwise generate a short title with Use Model"
        )
    )

    # 77
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_TITLE_SOURCE,
                "WFControlFlowMode": 0,
                "WFCondition": 100,
                "WFInput": condition_input_from_variable("User Description"),
            },
        )
    )

    # 78
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Transcript Title",
                "WFInput": wf_text_token_attachment(attach_variable("User Description")),
            },
        )
    )

    # 79
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_TITLE_SOURCE,
                "WFControlFlowMode": 1,
            },
        )
    )

    # 80
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": TITLE_PROMPT_UUID,
                "WFTextActionText": wf_text_token_string_from_parts(
                    [
                        "Generate a short transcript title (3-6 words). Return ONLY the title, no punctuation at the end, no extra text.\\n\\nTranscript:\\n",
                        attach_variable("Merged Transcript"),
                    ]
                ),
            },
        )
    )

    # 81
    actions.append(
        action(
            "is.workflow.actions.askllm",
            {
                "UUID": TITLE_LLM_UUID,
                "WFLLMModel": "Apple Intelligence",
                "WFGenerativeResultType": "Text",
                "WFLLMPrompt": wf_text_token_string_from_parts(
                    [attach_output(TITLE_PROMPT_UUID, "Text")]
                ),
            },
        )
    )

    # 82
    actions.append(
        action(
            "is.workflow.actions.text.trimwhitespace",
            {
                "UUID": TITLE_TRIM_UUID,
                "WFInput": wf_text_token_attachment(attach_output(TITLE_LLM_UUID, "Response")),
            },
        )
    )

    # 83
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Transcript Title",
                "WFInput": wf_text_token_attachment(
                    attach_output(TITLE_TRIM_UUID, "Updated Text")
                ),
            },
        )
    )

    # 84
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_TITLE_SOURCE,
                "WFControlFlowMode": 2,
            },
        )
    )

    # 85
    actions.append(
        comment(
            "--- SANITIZE TITLE ---\n"
            "- Remove filesystem-invalid characters\n"
            "- Trim surrounding whitespace"
        )
    )

    # 86
    actions.append(
        action(
            "is.workflow.actions.text.replace",
            {
                "UUID": TITLE_SANITIZE_UUID,
                "WFInput": wf_text_token_string_from_parts(
                    [attach_variable("Transcript Title")]
                ),
                "WFReplaceTextFind": "[\\\\/:*?\"<>|]",
                "WFReplaceTextRegularExpression": True,
                "WFReplaceTextReplace": "",
            },
        )
    )

    # 87
    actions.append(
        action(
            "is.workflow.actions.text.trimwhitespace",
            {
                "UUID": TITLE_SANITIZE_TRIM_UUID,
                "WFInput": wf_text_token_attachment(
                    attach_output(TITLE_SANITIZE_UUID, "Updated Text")
                ),
            },
        )
    )

    # 88
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Clean Title",
                "WFInput": wf_text_token_attachment(
                    attach_output(TITLE_SANITIZE_TRIM_UUID, "Updated Text")
                ),
            },
        )
    )

    # 89
    actions.append(
        comment(
            "- If Clean Title is empty, use fallback `Transcript`"
        )
    )

    # 90
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_CLEAN_TITLE,
                "WFControlFlowMode": 0,
                "WFCondition": 100,
                "WFInput": condition_input_from_variable("Clean Title"),
            },
        )
    )

    # 91
    actions.append(action("is.workflow.actions.nothing", {}))

    # 92
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_CLEAN_TITLE,
                "WFControlFlowMode": 1,
            },
        )
    )

    # 93
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": DEFAULT_TITLE_UUID,
                "WFTextActionText": "Transcript",
            },
        )
    )

    # 94
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Clean Title",
                "WFInput": wf_text_token_attachment(
                    attach_output(DEFAULT_TITLE_UUID, "Text")
                ),
            },
        )
    )

    # 95
    actions.append(
        action(
            "is.workflow.actions.conditional",
            {
                "GroupingIdentifier": GROUP_IF_CLEAN_TITLE,
                "WFControlFlowMode": 2,
            },
        )
    )

    # 96
    actions.append(
        comment(
            "--- DATE + BASE NAME ---\n"
            "- Build filename base: YYYY-MM-DD + title"
        )
    )

    # 97
    actions.append(
        action(
            "is.workflow.actions.date",
            {
                "UUID": DATE_NOW_UUID,
            },
        )
    )

    # 98
    actions.append(
        action(
            "is.workflow.actions.format.date",
            {
                "UUID": DATE_FORMAT_UUID,
                "WFDate": wf_text_token_string_from_parts(
                    [attach_output(DATE_NOW_UUID, "Date")]
                ),
                "WFDateFormatStyle": "Custom",
                "WFDateFormat": "yyyy-MM-dd",
            },
        )
    )

    # 99
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "File Date",
                "WFInput": wf_text_token_attachment(
                    attach_output(DATE_FORMAT_UUID, "Formatted Date")
                ),
            },
        )
    )

    # 100
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": BASENAME_UUID,
                "WFTextActionText": wf_text_token_string_from_parts(
                    [
                        attach_variable("File Date"),
                        " ",
                        attach_variable("Clean Title"),
                    ]
                ),
            },
        )
    )

    # 101
    actions.append(
        action(
            "is.workflow.actions.setvariable",
            {
                "WFVariableName": "Base Name",
                "WFInput": wf_text_token_attachment(attach_output(BASENAME_UUID, "Text")),
            },
        )
    )

    # 102
    actions.append(
        comment(
            "--- OUTPUT FOLDER ---\n"
            "- Choose destination folder once\n"
            "- Save transcript and audio copy there"
        )
    )

    # 103
    actions.append(
        action(
            "is.workflow.actions.file.select",
            {
                "UUID": OUTPUT_FOLDER_UUID,
                "CustomOutputName": "Output Folder",
                "WFPickingMode": "Folders",
                "SelectMultiple": False,
            },
        )
    )

    # 104
    actions.append(
        comment(
            "--- BUILD MARKDOWN + SAVE ---\n"
            "- Create markdown report\n"
            "- Save as `<Base Name>.md`"
        )
    )

    # 105 markdown content
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": MD_TEXT_UUID,
                "WFTextActionText": wf_text_token_string_from_parts(
                    [
                        "# ",
                        attach_variable("Clean Title"),
                        "\\n\\n"
                        "**Date:** ",
                        attach_variable("File Date"),
                        "\\n"
                        "**Speakers Hint:** ",
                        attach_variable("Speaker Hints"),
                        "\\n"
                        "**Engines:** AssemblyAI (primary), Mistral (secondary)\\n"
                        "**Merge Model:** Apple Intelligence\\n\\n"
                        "---\\n\\n"
                        "## Transcript\\n\\n"
                        "---\\n\\n",
                        attach_variable("Merged Transcript"),
                        "\\n",
                    ]
                ),
            },
        )
    )

    # 106 transcript filename text
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": TRANSCRIPT_NAME_UUID,
                "WFTextActionText": wf_text_token_string_from_parts(
                    [attach_variable("Base Name"), ".md"]
                ),
            },
        )
    )

    # 107 set name on markdown
    setitem_md_uuid = u()
    actions.append(
        action(
            "is.workflow.actions.setitemname",
            {
                "UUID": setitem_md_uuid,
                "WFInput": wf_text_token_attachment(attach_output(MD_TEXT_UUID, "Text")),
                "WFName": wf_text_token_string_from_parts(
                    [attach_output(TRANSCRIPT_NAME_UUID, "Text")]
                ),
            },
        )
    )

    # 108 save markdown
    actions.append(
        action(
            "is.workflow.actions.documentpicker.save",
            {
                "WFInput": wf_text_token_attachment(
                    attach_output(setitem_md_uuid, "Renamed Item")
                ),
                "WFFolder": wf_text_token_attachment(
                    attach_output(OUTPUT_FOLDER_UUID, "Output Folder")
                ),
                "WFAskWhereToSave": False,
                "WFSaveFileOverwrite": True,
            },
        )
    )

    # 109 audio filename text
    actions.append(
        action(
            "is.workflow.actions.gettext",
            {
                "UUID": AUDIO_NAME_UUID,
                "WFTextActionText": wf_text_token_string_from_parts(
                    [attach_variable("Base Name"), " - Audio"]
                ),
            },
        )
    )

    # 110 set name on audio
    setitem_audio_uuid = u()
    actions.append(
        action(
            "is.workflow.actions.setitemname",
            {
                "UUID": setitem_audio_uuid,
                "WFInput": wf_text_token_attachment(attach_variable("Selected Audio File")),
                "WFName": wf_text_token_string_from_parts(
                    [attach_output(AUDIO_NAME_UUID, "Text")]
                ),
            },
        )
    )

    # 111 save audio copy
    actions.append(
        action(
            "is.workflow.actions.documentpicker.save",
            {
                "WFInput": wf_text_token_attachment(attach_output(setitem_audio_uuid, "Renamed Item")),
                "WFFolder": wf_text_token_attachment(attach_output(OUTPUT_FOLDER_UUID, "Output Folder")),
                "WFAskWhereToSave": False,
                "WFSaveFileOverwrite": True,
            },
        )
    )

    # 112
    actions.append(
        action(
            "is.workflow.actions.alert",
            {
                "WFAlertActionTitle": "Smart Transcribe Complete",
                "WFAlertActionMessage": "Transcript and audio copy were saved to the selected folder.",
            },
        )
    )

    # Import questions target action indexes (0-based).
    import_questions = [
        {
            "ActionIndex": 3,
            "Category": "Parameter",
            "ParameterKey": "WFTextActionText",
            "Text": "AssemblyAI API Key",
            "DefaultValue": "PASTE_ASSEMBLYAI_API_KEY",
        },
        {
            "ActionIndex": 4,
            "Category": "Parameter",
            "ParameterKey": "WFTextActionText",
            "Text": "Mistral API Key",
            "DefaultValue": "PASTE_MISTRAL_API_KEY",
        },
    ]

    workflow = {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "4407",
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowIcon": {
            "WFWorkflowIconGlyphNumber": icon_glyph,
            "WFWorkflowIconStartColor": icon_color,
        },
        "WFWorkflowImportQuestions": import_questions,
        "WFWorkflowInputContentItemClasses": [],
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowName": "Smart Transcribe",
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowTypes": [],
    }
    return workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Smart Transcribe shortcut plist")
    parser.add_argument(
        "--output",
        default=str(Path.home() / "Desktop" / "Smart Transcribe.shortcut"),
        help="Output .shortcut path",
    )
    parser.add_argument("--icon-glyph", type=int, default=62213)
    parser.add_argument("--icon-color", type=int, default=2071128575)
    args = parser.parse_args()

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    workflow = build_shortcut(icon_glyph=args.icon_glyph, icon_color=args.icon_color)
    with output_path.open("wb") as f:
        plistlib.dump(workflow, f, fmt=plistlib.FMT_XML, sort_keys=False)

    print(output_path)


if __name__ == "__main__":
    main()
