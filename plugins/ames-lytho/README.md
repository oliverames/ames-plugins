# ames-lytho

Lytho Workflow MCP connector for Oliver's Claude plugin marketplace.

The source of truth for this plugin is three files:

- **`.mcp.json`** — the MCP server launch config (command, args, env vars)
- **`update-sources.json`** — package metadata for syncing the sources snapshot
- **`sources/lytho-mcp-server/`** — trimmed snapshot of the authoritative connector repo

The connector is published to npm as [`@oliverames/lytho-mcp-server`](https://www.npmjs.com/package/@oliverames/lytho-mcp-server). The development project lives at `lytho-mcp-server` and its GitHub repo is at [oliverames/lytho-mcp-server](https://github.com/oliverames/lytho-mcp-server).

## Required Environment Variables

Set these in your Claude Code environment before installing this plugin:

| Variable | Description |
|----------|-------------|
| `LYTHO_CLIENT_ID` | OAuth 2.0 client ID from Lytho Open API settings |
| `LYTHO_CLIENT_SECRET` | OAuth 2.0 client secret from Lytho Open API settings |
| `LYTHO_TOKEN_URL` | Keycloak token endpoint URL (tenant-specific) |
