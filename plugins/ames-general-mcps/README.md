<h1 align="center">ames-general-mcps</h1>

<p align="center">
  <strong>Seven MCP servers for day-to-day productivity work</strong>
</p>

<p align="center">
  <code>Drafts</code> &bull;
  <code>Excel</code> &bull;
  <code>Google Workspace</code> &bull;
  <code>iMCP</code> &bull;
  <code>MarkItDown</code> &bull;
  <code>Pandoc</code> &bull;
  <code>Peekaboo</code>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-MIT-f5a542?style=flat-square" alt="License"></a>
  <a href="https://www.buymeacoffee.com/oliverames"><img src="https://img.shields.io/badge/Buy_Me_a_Coffee-support-f5a542?style=flat-square&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me a Coffee"></a>
</p>

---

A Claude Code plugin bundling seven MCP servers for the things you do *outside* of writing code: drafting in Drafts, editing spreadsheets, reading Gmail and Calendar, tapping local macOS data via iMCP, converting documents with MarkItDown and Pandoc, and taking screenshots with Peekaboo. Paired with [`ames-dev-mcps`](../ames-dev-mcps/), which covers iOS/macOS development tools.

## Why this exists

MCP servers compose, but always-loading *every* server makes the tool list noisy and burns tokens on tools that aren't in play. This bundle groups only the servers that matter in day-to-day productivity flow: note-taking, documents, calendar, email, screenshots. When you're heads-down building software, you can disable this plugin and keep [`ames-dev-mcps`](../ames-dev-mcps/) enabled on its own.

Split out of the older `ames-preferred-mcps` umbrella plugin alongside [`ames-dev-mcps`](../ames-dev-mcps/) so each half can be enabled, disabled, and versioned independently.

## Quick start

This plugin lives in the [`ames-plugins`](https://github.com/oliverames/ames-plugins) marketplace:

```bash
# In Claude Code
/plugin marketplace add oliverames/ames-plugins
/plugin install ames-general-mcps@ames-plugins
```

The `google-workspace` server requires OAuth credentials; see below.

## Servers

| Server | Purpose | Transport | Env |
|---|---|---|---|
| `drafts` | Read/write Drafts.app notes | `npx` | none |
| `excel` | Read and edit `.xlsx` workbooks | `uvx` | none |
| `google-workspace` | Gmail, Calendar, Drive, Docs, Sheets | `npx` | `GOOGLE_WORKSPACE_OAUTH_CLIENT_ID`, `GOOGLE_WORKSPACE_OAUTH_CLIENT_SECRET` |
| `iMCP` | Calendar, Contacts, Messages, Location, Reminders | local binary | none |
| `markitdown` | Convert HTML/PDF/Word/images to Markdown | `uvx` | none |
| `pandoc` | Convert between 40+ document formats | `uvx` | none |
| `peekaboo` | Screenshots plus vision-based UI analysis | `npx` | none |

See [.mcp.json](.mcp.json) for exact invocations.

### Google Workspace OAuth

Credentials resolve from your host's local runtime config (`settings.json` `env` block or a plugin-local `.env`) and are never committed to the repo. See the [Google Workspace MCP docs](https://github.com/aaronsb/google-workspace-mcp) for setup.

## Related

- [`ames-dev-mcps`](../ames-dev-mcps/), the sibling bundle for iOS/macOS development
- [`ames-plugins` marketplace](https://github.com/oliverames/ames-plugins), the full set of six plugins

---

<p align="center">
  <sub>
    Built by <a href="https://ames.consulting">Oliver Ames</a> in Vermont
    &bull; <a href="https://github.com/oliverames">GitHub</a>
    &bull; <a href="https://linkedin.com/in/oliverames">LinkedIn</a>
    &bull; <a href="https://bsky.app/profile/oliverames.bsky.social">Bluesky</a>
  </sub>
</p>
