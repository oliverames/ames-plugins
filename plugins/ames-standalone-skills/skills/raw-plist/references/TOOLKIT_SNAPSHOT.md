# ToolKit Snapshot Package

This skill bundles a precomputed ToolKit metadata snapshot so it can be shared without requiring users to extract `~/Library/Shortcuts/ToolKit/*.sqlite` on their own machines.

## Bundled Files

- `data/toolkit-v63-summary.json`
- `data/toolkit-v63-tool-ids.json`
- `data/toolkit-v63-tools.json`
- `data/toolkit-v63-types.json`
- `data/toolkit-v63-triggers.json`

## Coverage

The bundled files include metadata from these ToolKit concepts:

- **Tools**: `id`, `toolType`, `flags`, `visibilityFlags`, `requirements` bytes + base64, auth policy, source provider/container attribution, output type instance bytes + base64, output type IDs, localized display/language-model strings
- **Parameters**: key, sort order, flags, `typeInstance` bytes + base64, `relationships` bytes + base64, localized names/descriptions/boolean aliases, parameter→type links
- **Types**: persistent ID, blob ID bytes + base64, source container, `kind`, `runtimeFlags`, `runtimeRequirements` bytes + base64, numeric format, synonyms byte length, coercion definitions (bytes + base64), UTType coercions
- **Triggers**: trigger IDs, flags, requirements bytes + base64, output type instance bytes + base64, output types, trigger parameters, trigger localizations

## Validator Behavior

`scripts/validate_shortcut.py` uses `data/toolkit-v63-tool-ids.json` as the primary allowlist source, then augments with markdown references and optional local ToolKit SQLite reads.

This keeps validation portable for distributed use while preserving optional local expansion when available.

## Regenerating the Snapshot

If ToolKit schema/content changes in a future OS release, refresh `data/toolkit-v63-*.json` outside the distributed skill package and then update the bundled JSON files.
