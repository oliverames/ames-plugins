---
name: draft-comms
description: >-
  Use when the user provides meeting notes, transcripts, emails, or a list of
  action items that require outreach. Triggers for "draft follow-ups", "write
  these emails", "draft comms from my notes", "help me follow up on this
  meeting", or "draft messages from this transcript".
---

# Draft Communications

Reads source material, identifies every action item requiring outreach, drafts each message in the user's personal voice using the humanizer skill, and saves drafts to ~/Documents/drafts/.

## Steps

1. **Read the source material** — Read the transcript, notes, or text provided. If no file or text is given, ask for it before proceeding.

2. **Identify action items** — Extract every item requiring outreach: follow-ups, confirmations, introductions, thank-yous, proposals. List them for the user before drafting.

3. **Draft each message** — For each action item, invoke the `ames-standalone-skills:humanizer` skill to write the draft. Never output corporate or AI-sounding prose. The tone should already reflect the user's voice in the first draft.

4. **Save each draft** — Write each message to `~/Documents/drafts/` as a markdown file named descriptively (e.g., `2026-04-10-followup-beth-roberts.md`). Create the directory if it doesn't exist.

5. **Present and copy** — Show each draft to the user one at a time. After the user approves, copy the final text to the clipboard using `pbcopy`.

## Notes

- Do not send any messages. Draft only.
- If the user has a preferred sign-off or signature, ask once and apply to all drafts.
- Flag any action items that are ambiguous about recipient or intent before drafting.
