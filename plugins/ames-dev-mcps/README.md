<h1 align="center">ames-dev-mcps</h1>

<p align="center">
  <strong>Six MCP servers for iOS and macOS development work</strong>
</p>

<p align="center">
  <code>Apple Docs</code> &bull;
  <code>Apple Notifier</code> &bull;
  <code>macOS Automator</code> &bull;
  <code>XcodeBuild</code> &bull;
  <code>Sim Genie</code> &bull;
  <code>Sosumi</code>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-MIT-f5a542?style=flat-square" alt="License"></a>
  <a href="https://www.buymeacoffee.com/oliverames"><img src="https://img.shields.io/badge/Buy_Me_a_Coffee-support-f5a542?style=flat-square&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me a Coffee"></a>
</p>

---

A Claude Code plugin bundling six MCP servers that matter while you're *building software*: reading Apple's developer docs, sending build notifications, driving macOS via AppleScript, running `xcodebuild` from inside Claude, managing simulators, and fetching Apple platform reference content. Paired with [`ames-general-mcps`](../ames-general-mcps/), which covers day-to-day productivity tools.

## Why this exists

MCP servers compose. Any client (Claude Code, Codex, Cursor) can load multiple at once, but if you enable *everything*, the tool list gets noisy and the model wastes tokens narrowing it down each turn. This plugin groups only the servers that matter during active iOS/macOS development: doc lookups, simulator management, build-and-log plumbing. When you're not building software, none of these are in scope, so they come out of the mix the moment the plugin is disabled.

Split out of the older `ames-preferred-mcps` umbrella plugin alongside [`ames-general-mcps`](../ames-general-mcps/) so "when do I reach for this?" becomes legible: dev-time versus day-to-day.

## Quick start

This plugin lives in the [`ames-claude`](https://github.com/oliverames/ames-claude) marketplace:

```bash
# In Claude Code
/plugin marketplace add oliverames/ames-claude
/plugin install ames-dev-mcps@ames-claude
```

No environment variables are required. Every server uses public or local resources.

## Servers

| Server | Purpose | Transport |
|---|---|---|
| `apple-docs` | Query Apple developer documentation | `npx` |
| `apple-notifier` | Send native macOS notifications from tool calls | `npx` |
| `macos-automator` | Drive macOS via AppleScript / JXA | `npx` |
| `XcodeBuildMCP` | Run `xcodebuild`, manage simulators, capture logs | `npx` |
| `SimGenie` | Companion tooling for the Sim Genie simulator app | local binary |
| `sosumi` | Apple platform reference via `sosumi.ai` | `http` |

See [.mcp.json](.mcp.json) for exact invocations.

## Related

- [`ames-general-mcps`](../ames-general-mcps/), the sibling bundle for day-to-day productivity servers
- [`ames-claude` marketplace](https://github.com/oliverames/ames-claude), the full set of six plugins

---

<p align="center">
  <sub>
    Built by <a href="https://ames.consulting">Oliver Ames</a> in Vermont
    &bull; <a href="https://github.com/oliverames">GitHub</a>
    &bull; <a href="https://linkedin.com/in/oliverames">LinkedIn</a>
    &bull; <a href="https://bsky.app/profile/oliverames.bsky.social">Bluesky</a>
  </sub>
</p>
