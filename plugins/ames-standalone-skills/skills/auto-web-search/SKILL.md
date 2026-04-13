---
name: auto-web-search
description: >-
  Behavioral skill that triggers automatic web searches when stuck on a problem.
  Activates when Claude encounters an error it cannot resolve, an unfamiliar API,
  a deprecation warning, a version mismatch, or any situation where general
  knowledge is insufficient. Also triggers for "search for a fix", "look this up",
  "find the docs", "why is this failing", or when the user asks Claude to be more
  resourceful about finding answers. This skill should run in the background of
  every coding session.
---

# Auto Web Search on Stuck Problems

## When to Search Automatically

Search the web WITHOUT being asked when any of these conditions are met:

### Error Resolution
- An error message you haven't seen before or can't resolve in 2 attempts
- A stack trace pointing to a third-party library
- A build/compile error related to version incompatibility
- A deprecation warning with no obvious replacement

### API and Library Questions
- Using an API or library you're not confident about (check docs first)
- SDK method signatures that might have changed since your training data
- Framework-specific patterns that vary by version (e.g., SwiftUI on iOS 26 vs 18)
- Configuration syntax you're guessing at rather than knowing

### Environment and Tooling
- CLI tool flags or options you're unsure about
- Package manager errors (npm, pip, brew, cargo)
- CI/CD configuration syntax
- Platform-specific behavior differences

### When NOT to Search
- Problems you can solve by reading existing code in the project
- Errors with obvious fixes (typos, missing imports, syntax errors)
- Questions fully answered by files already in context
- General programming concepts you know well

## Search Strategy

### Tier 1: Official Documentation (preferred)
Use context7 MCP (`resolve-library-id` then `query-docs`) for any library,
framework, or SDK question. This returns current, authoritative documentation.

### Tier 2: Web Search
Use `WebSearch` for:
- Error messages (paste the exact error string)
- "How to [specific task] in [framework] [version]"
- Compatibility questions between tools/versions
- Recent changes or announcements

### Tier 3: Deep Research
Use `gemini -m gemini-3-flash-preview -p "..." --yolo` via Bash for:
- Complex multi-source research questions
- Architectural decisions needing broad context
- Comparing multiple approaches with tradeoffs

### Tier 4: Direct Fetch
Use `WebFetch` to read a specific URL when you already know where the answer is
(GitHub issue, documentation page, Stack Overflow thread).

## Reporting

When you search automatically, briefly note what triggered it:

```
Searched: [what you looked for]
Found: [one-line summary of the answer]
```

Do NOT ask permission to search. Do NOT announce you're about to search. Just
search, find the answer, and apply it. Report what you found inline.

## Key Principle

**Searching is not a sign of weakness; guessing is.** A wrong answer delivered
confidently wastes more time than a 5-second web search. When in doubt, look
it up. The user's CLAUDE.md explicitly says: "When unsure if an API or tool
supports a capability, always test it before declaring it impossible."
