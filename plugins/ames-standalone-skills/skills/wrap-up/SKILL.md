---
name: wrap-up
version: 4.4.0
description: >
  Use when Oliver says "wrap up", "close session", "end session", "wrap
  things up", "close out this task", "done for the day", "session complete",
  or invokes /wrap-up. Runs a host-aware end-of-session closeout for Claude
  Code and Codex: verification, commits, worklogs, memory or notes follow-up,
  config drift checks, backups, and a concise final report.
---

# Session Wrap-Up

End the session in a way that leaves Oliver's work trustworthy and easy to
resume. This skill is intentionally host-aware: Claude Code and Codex share
the same standards, but not the same settings files, memory systems, MCP
tools, or backup commands.

## Prime Directive

Run a deterministic preflight first, then execute only the phases that are
valid for the current host and repo state. Missing optional tools are not
failures. Skip them, say why, and keep closing the session.

Use bundled helper:

```bash
python3 scripts/wrap-up-preflight.py --host auto --json
```

If the helper path is not obvious, resolve it relative to this `SKILL.md`.
If the helper is missing from an installed cache, continue manually using the
same checks listed below and report that the helper was unavailable.

## Safety Rules

- Never read or print secret values. For `~/.claude/settings.json`, read only
  targeted non-secret fields such as `enabledPlugins`, `extraKnownMarketplaces`,
  `permissions`, `hooks`, and top-level behavior keys. Do not read `env`.
- For Codex, treat `~/.codex/config.toml` as the live config file. Inspect keys
  and structure only; do not dump credentials or token-like values.
- Do not blindly run destructive or catch-all commands. `commit-push-all` is a
  final safety net only when preflight and git status show expected repos and
  no unrelated dirty work.
- Before editing skills, configs, or user documents during wrap-up, back up the
  original file or make an explicit rename first.
- Preserve user changes. If a repo already has unrelated dirty files, work
  around them and mention the residual state instead of staging everything.
- Use subagents only when the active host policy allows it. In Codex, follow the
  current system and developer instructions even if Oliver's general workflow
  says to use subagents liberally.

## Phase 0: Preflight

1. Run `wrap-up-preflight.py`.
2. Identify the active host:
   - **Claude Code**: likely uses `~/.claude/settings.json`, Claude session
     artifacts under `~/.claude/projects`, Claude memory, and Claude MCP tools.
   - **Codex**: likely uses `~/.codex/config.toml`, Codex memories under
     `~/.codex/memories`, Codex sessions under `~/.codex/sessions`, and
     available Codex app/tool surfaces.
   - If ambiguous, infer from current tool names and session context, then say
     which host was assumed.
3. Identify touched repos:
   - Start with the current git root.
   - Add any repo paths clearly modified or discussed in the session.
   - For recent Claude Code sessions, prefer fresh `WORKLOG.md` entries and
     `~/.claude/projects/*/*.jsonl` summaries over old memories.
   - For Codex sessions, prefer the current conversation, current cwd, and
     recent `~/.codex/sessions` entries.
4. Classify scope:
   - **Trivial**: one small config/docs/code change and no new decisions.
   - **Standard**: one repo with meaningful implementation or documentation.
   - **Deep**: multiple repos, plugin/config changes, audits, architecture,
     automation, credentials, or significant decisions.

Stop and re-plan if preflight finds a real contradiction, such as a missing
repo, malformed manifest, failed required verification, or dirty files that
would be unsafe to stage.

## Phase 1: Verify And Ship

For each touched repo:

1. Run `git status --short --branch`.
2. Review the diff for accidental secrets, debug leftovers, unrelated files,
   generated cache files, or changes made by someone else.
3. Run verification appropriate to the change:
   - **Web app**: typecheck, lint, build, and hit relevant local routes when a
     server is practical.
   - **CLI/script**: invoke the changed entry point with representative input.
   - **Skill/plugin**: run `validate-skill` when available, run repo `./sync`
     when marketplace manifests depend on it, and validate changed JSON.
   - **Docs only**: re-read the modified files and check links/paths/counts.
4. Commit only intended changes in each repo. Use a clear message with the
   local convention (`fix:`, `docs:`, `chore:`, `worklog:`, etc.).
5. Push only after verification passes. If push fails, report the exact failure
   and leave the local commit in place.

### ames-claude Plugin Special Case

When the session changed `~/Developer/Projects/ames-claude` or its iCloud
resolved path:

1. Keep `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and the
   regenerated marketplace entries in version parity.
2. Run `./sync` from the repo root after plugin version changes.
3. Validate both host manifests:
   ```bash
   python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
   python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
   ```
4. Do not hand-edit generated marketplace JSON except to recover from a failed
   sync.

## Phase 2: Documentation Drift

Update documentation only when the session changed behavior, setup, public
commands, plugin layout, API surface, or config.

Check in this order:

1. `README.md`: user-facing capabilities, setup commands, tool counts, paths,
   examples, env var names, and plugin or MCP inventories.
2. `CLAUDE.md`: Claude Code workflow conventions, plugin hygiene, settings
   expectations, and host-specific notes.
3. `AGENTS.md`: Codex workflow conventions, plugin manifests, Codex settings,
   and host-specific notes.
4. Project-specific docs: only the section made stale by this session.

For config-record drift:

- **Claude Code**: if `~/.claude/settings.json`, Claude plugins, MCPs,
  marketplaces, hooks, permissions, model defaults, or UI behavior changed,
  update the repo's Claude Code config reference. Use targeted reads and do not
  expose `env` values. If Apple Notes tools are available, also consider the
  `💻 Claude Code Setup` note or related `💻 Tech` notes.
- **Codex**: if `~/.codex/config.toml`, Codex plugins, marketplaces, app
  automations, or Codex-only manifests changed, update Codex-facing docs such
  as `AGENTS.md`, `.agents/plugins/marketplace.json` source docs, or the
  relevant README section. Do not rewrite Claude-only config records.
- If a docs target is intentionally duplicated in README and Apple Notes,
  update both only when the required tool is available. Otherwise update the
  repo source of truth and report the skipped note update.

## Phase 3: Worklog

Write a `WORKLOG.md` entry for every project repo with meaningful work. Skip
for one-off config-only sessions unless the config lives in a project repo and
future context would otherwise be lost.

Before writing:

1. Read the latest existing entry.
2. Check whether carried items were resolved, still open, or obsolete.
3. Use `git log --oneline -10`, `git diff --stat`, and the session context to
   avoid inventing a narrative.

Entry format:

```markdown
## YYYY-MM-DD - Brief summary

**What changed**: ...

**Decisions made**: ...

**Left off at**: ...

**Open questions**: ...

---
```

Rules:

- Put concrete verification in the entry when the project changed code.
- Distinguish `NEW`, `Still open`, and `Resolved this session`.
- Carry forward unresolved prior items explicitly, do not silently drop them.
- For multi-repo sessions, write one entry per repo and mention the related
  repos in prose.
- Prefer concise, factual entries over blow-by-blow logs.

## Phase 4: Memory, Notes, And Self-Improvement

Persist only knowledge that will matter in future sessions.

Scan for:

- user corrections or durable preferences,
- project setup quirks,
- commands that failed and their working replacements,
- new external URLs or dashboard locations,
- host-specific tool limitations or capabilities,
- validated approaches that should be repeated.

Apply by host:

- **Claude Code**: use the available project/global memory mechanism, local
  `CLAUDE.local.md`, project `CLAUDE.md`, or `.claude/rules/` as appropriate.
- **Codex**: do not edit Codex memory files unless current instructions allow
  it. Report memory candidates in the final summary. Use existing Codex memory
  only as read context with required citations.
- **Apple Notes**: before declaring the tool unavailable, discover the current
  tool surface. In Codex, use ToolSearch. In Claude Code, inspect the available
  MCP tools. If Apple Notes write tools exist, route content through
  `apple-notes-formatting` first. If not, skip with a clear reason.

When a skill's documented command failed in practice, update the skill source
during the session if it is safe and in scope. The skill is canonical; memory is
only a recall cache.

## Phase 5: Backups And Final Sweep

Run only available and relevant commands:

1. `backup-claude`: run when Claude Code memory/config changed and the command
   exists.
2. `commit-push-all`: use only after verifying the repos it would touch are
   expected. If the script supports a dry run, run that first. If it does not,
   prefer explicit repo commits unless this was a deep multi-repo cleanup.

Then run a final status pass for every touched repo and note any residual dirty
files that are unrelated or intentionally left open.

## Final Report

Keep the report short and concrete. Include only lines that apply:

```text
Session complete

Verified: <commands and observed results>
Shipped: <commits/pushes or "local changes only">
Worklog: <repos updated or skipped>
Docs: <files/notes updated or skipped>
Memory: <saved, candidates, or nothing new>
Backup: <commands run or skipped reason>
Residual: <known dirty files or blockers>
```

If the session was trivial:

```text
Committed and pushed. Backup complete.
```

After the report, stop. Do not run an exit command.
