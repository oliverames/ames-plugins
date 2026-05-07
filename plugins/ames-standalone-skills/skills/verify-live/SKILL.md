---
name: verify-live
description: >-
  Verifies documentation against live system state before rewriting.
  Forces an SSH or API check against the actual system before any
  rewrite, so updates cite live evidence rather than perpetuating stale
  content.
when_to_use: >-
  Triggers when asked to "rewrite my notes about [system]", "update this
  doc", "audit these notes", "refresh the docs for [server]", "are these
  notes still accurate", "check if these notes match", "reformat this
  README", or any task that involves modifying documentation about a
  server, API, service, or configuration.
---

# Verify Live State Before Rewriting Documentation

## When to Trigger

Run this skill BEFORE editing any document that describes a real system:

- Notes about home servers, self-hosted services, or remote machines
- READMEs that describe live infrastructure (Cloudflare tunnels, DNS,
  Tailscale nodes, deployed services)
- Configuration docs (env files, MCP manifests, plugin manifests)
- Any file whose claims can be checked by SSH, API call, or `curl`

## The Four-Step Protocol

1. **Identify the system referenced** — server, API, service, container,
   tunnel, route, manifest, etc. Note the exact endpoint or hostname.

2. **Get the ACTUAL current state** — SSH in, hit the API, run `curl`,
   query the manifest, list the directory, whatever proves ground truth.
   Do NOT skip this step because the existing notes "look right".

3. **Diff against the existing notes** — line by line. Find every claim
   in the doc that the live state contradicts, supports, or doesn't cover.

4. **Only then propose rewrites, citing live evidence** — every change
   should reference what the live check showed (e.g., "removed mention of
   port 8080; `ss -tlnp` shows the service now binds 8443").

## When NOT to Verify Live

- Pure prose docs that don't describe a system (blog posts, letters)
- Documents about external services where you have no access
- When the user explicitly says "just rewrite from the existing content"

## Key Principle

**Stale notes are worse than no notes.** Rewriting from existing content
without a live check perpetuates errors and amplifies them. The user's
CLAUDE.md says: "Before rewriting documentation/notes about systems,
verify against the actual live state (SSH, API calls, etc.) — don't
trust existing notes." This skill enforces that rule mechanically.
