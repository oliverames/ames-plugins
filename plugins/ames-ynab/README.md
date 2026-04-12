# ames-ynab

YNAB (You Need A Budget) MCP connector, authored by Oliver Ames and published through the marketplace. Also carried here as a portable source snapshot.

Source-of-truth files:

- `.mcp.json` — runtime connector definition for Claude Code
- `update-sources.json` — package/update metadata plus local project mapping
- `sync-sources` — refreshes `sources/` from the sibling development repo
- `sources/ynab-mcp-server/` — trimmed snapshot of the authoritative connector repo

## History

This plugin was previously named `ames-original-connectors` and bundled five MCP connectors (meta, sprout-social, ynab-mcp-server, imagerelay, unifi). In v2.0.0 it was scoped down to YNAB only and renamed to `ames-ynab`. The other four connectors continue to live in their own repos and can still be installed independently via npm; they're no longer bundled here because they weren't in active use.
