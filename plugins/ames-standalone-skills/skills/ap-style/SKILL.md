---
name: ap-style
description: >-
  Applies Associated Press (AP) Stylebook conventions to news writing,
  press releases, headlines, blog posts, and general editorial copy —
  numbers, dates, titles, attribution, quotation, capitalization, and
  common word choices. Paraphrased from the AP Stylebook; defers to
  bcbs-brand for BCBS VT work where house style overrides AP.
when_to_use: >-
  Writing or editing news articles, press releases, media advisories,
  blog posts, social copy, or any general-audience editorial content
  where AP Style is the expected register. Triggers for "apply AP
  style", "AP-style this", "is this AP style", "AP numerals", "AP
  dates", "AP titles", "newsroom style", "press release", "media
  advisory", "wire copy", or "house style vs AP". Skip for BCBS VT
  content — bcbs-brand owns that voice.
version: 1.0.0
---

# Associated Press Style

Apply the Associated Press Stylebook conventions to general editorial writing. This skill paraphrases established AP rules and current usage updates; it does not reproduce Stylebook entries. For the authoritative ruling on any specific entry, consult Oliver's licensed copy of the AP Stylebook (print + online subscription at apstylebook.com).

## Authoritative sources

| Source | What it covers | Where |
|--------|---------------|-------|
| AP Stylebook (print + online) | The canonical entries. Always defer to current Stylebook on contested calls | Oliver owns a licensed copy; check apstylebook.com first when unsure |
| `data/ap/` (this skill, gitignored) | Oliver's personal notes, excerpts, and house-specific rulings from his copy. Not redistributed | `plugins/ames-standalone-skills/skills/ap-style/data/ap/` |
| `bcbs-brand` skill | Overrides AP for Blue Cross VT work (healthcare vs. health care, etc.) | Sibling skill in this plugin |

**Legal posture:** The AP Stylebook is proprietary. This skill paraphrases well-established rules and explains *how* to apply them with original examples. Verbatim Stylebook entries belong in Oliver's gitignored `data/ap/` notes, never in this SKILL.md or anywhere that ships publicly.

## Quick reference card

The rules most worth getting right on the first pass:

- **Numbers:** spell out one through nine, numerals for 10 and up. Exceptions: ages, percentages, money, addresses, dimensions, times — always numerals.
- **Never start a sentence with a numeral.** Rewrite or spell out (years are the lone exception: "2026 was a leap year.").
- **Attribution verb:** `said`. Past tense. After the quote.
- **Dates:** abbreviate Jan., Feb., Aug., Sept., Oct., Nov., Dec. only with a specific day. Spell out March, April, May, June, July always. Spell every month when there is no day.
- **Times:** `9 a.m.`, `5:30 p.m.`, `noon`, `midnight`. Never `9:00 a.m.` or `12 p.m.`.
- **States:** spell out in story body; AP abbreviations (`Calif.`, `N.Y.`, `Mass.`) in datelines, photo captions, lists; postal codes (`CA`, `NY`) only with full mailing addresses.
- **Oxford comma:** no, unless removing it creates ambiguity.
- **Quotation:** periods and commas inside; colons and semicolons outside.
- **Percent symbol:** `5%` (numeral + `%`) — AP accepted this in 2019.
- **`website`, `email`, `internet`, `online`:** one word each, lowercase. `Internet` was lowercased in 2016.

## Numbers

| Rule | Right | Wrong |
|------|-------|-------|
| Spell out one through nine | "three witnesses" | "3 witnesses" |
| Use numerals for 10 and up | "15 people attended" | "fifteen people attended" |
| Numerals for ages always | "a 5-year-old girl"; "Marsha, 47" | "a five-year-old" |
| Numerals for percentages always | "5%" or "5 percent" | "five percent" |
| Numerals for money always | "$5 million", "$1.2 billion" | "five million dollars" |
| Numerals for addresses | "123 Main St." | "One hundred twenty-three" |
| Spell out ordinals first through ninth | "first place" | "1st place" |
| Numerals for 10th and up | "10th anniversary" | "tenth anniversary" |
| Never start a sentence with a numeral | "Twenty people…" or rewrite | "20 people…" |
| Year exception at sentence start | "2026 brought changes." | (Year is allowed.) |

### Big numbers
- `1 million`, `2.5 billion`, `$1.4 trillion` — numerals plus the word.
- Hyphenate compound modifiers: `a 5-year-old child`, `a 10-mile race`, `a $50-million budget` (some publications drop the hyphen with `$`; AP keeps it).

## Dates and times

### Months
- **Abbreviate with a specific date:** `Sept. 15`, `Oct. 3, 2025`, `Jan. 1`.
- **Spell out always:** March, April, May, June, July (the five-letter-or-shorter rule).
- **Spell out without a day:** `September 2025`, `last August`.

### Days of the week
- Capitalize. Don't abbreviate in running copy.
- Use the day name, not `on Tuesday` (drop the `on`).
- For events more than seven days out or past, use the date instead: "the meeting on Sept. 15" rather than "the meeting on Tuesday three weeks from now."

### Times
- `9 a.m.`, `5:30 p.m.`, lowercase with periods.
- `noon` and `midnight`, never `12 p.m.` or `12 a.m.`.
- Drop `:00` for top-of-hour times.
- Time ranges: `9 a.m. to 5 p.m.` or `9-11 a.m.` (no space around the hyphen).

### Years and decades
- `2026`, `the 2020s` (no apostrophe), `the '90s` (apostrophe replaces dropped digits).
- Don't write `2026's`; write `of 2026`.

## Titles and names

| Rule | Example |
|------|---------|
| Capitalize formal titles before a name | "Mayor Jane Smith said…" |
| Lowercase titles after a name | "Jane Smith, the mayor, said…" |
| Lowercase titles standing alone | "The mayor said…" |
| Full name on first reference | "Jane Smith" |
| Last name only on second reference | "Smith said…" |
| No courtesy titles in news copy | Not "Ms. Smith" or "Mr. Smith" |
| Use courtesy titles in obituaries | Established AP exception |
| Job descriptions ≠ formal titles | `astronaut Mae Jemison` (lowercase) vs. `Sen. John Smith` (capitalized) |

**The formal title test:** if the title is conferred by election, appointment, or organizational hierarchy (`Sen.`, `Gov.`, `Chief`, `Mayor`, `Director`), it's formal and capitalizes before the name. If it's a description (`astronaut`, `author`, `attorney`, `coach`, `actor`), it's lowercase even directly before the name.

## Attribution

- **Verb:** `said`. Past tense. Avoid `stated`, `remarked`, `noted`, `expressed`, `claimed` (which implies doubt), `admitted` (which implies wrongdoing).
- **Position:** attribution after the quote, at the first natural pause.
- **Word order:** `Smith said` is preferred over `said Smith` in most contexts. Use `said + full name + descriptor` when the descriptor is long: `"…," said Jane Smith, who has led the agency for 12 years.`
- **Avoid bracketing speakers:** don't break a single sentence with attribution mid-clause unless the pause is natural.

**Right:**
> "We are committed to this project," Smith said.

**Wrong:**
> Smith stated, "We are committed to this project."

## Quotation and punctuation

### Quotation marks
- Periods and commas: **always inside** the closing quote, even when logically odd.
- Colons and semicolons: **always outside**.
- Question marks and exclamation points: **inside** if part of the quoted material, **outside** if part of the surrounding sentence.
- Single quotes are for quotes within quotes: `"She said 'yes,' and we moved on," he recalled.`
- Headlines: AP allows single quotes throughout.

### Hyphens, en dashes, em dashes
- **Hyphen:** compound modifiers (`small-business owner`, `well-known author`). No hyphen with `-ly` adverbs (`recently elected official`, not `recently-elected official`).
- **En dash (–):** AP doesn't use en dashes in body copy. Use a hyphen for ranges (`pages 32-37`) and a word for spans of time (`9 a.m. to 5 p.m.`).
- **Em dash (—):** AP uses em dashes sparingly. Spaces on both sides. Don't use as a substitute for commas, colons, or parentheses out of habit; reserve for sharp breaks in thought.

### Oxford comma
- AP: **no** Oxford comma in simple lists. `red, white and blue.`
- Use it only when omission creates ambiguity: `the gifts were from her parents, John and Marsha` is ambiguous; rewrite or add the serial comma.

## Capitalization

- **Job titles:** see Titles section above.
- **Proper nouns:** capitalize.
- **Compass directions:** lowercase as direction (`drive south`), capitalize as region (`the South`, `the Northeast`).
- **Seasons:** lowercase. `winter`, `summer`, `spring`, `fall` — except when part of a formal name (`Winter Olympics`).
- **Brands:** match the brand's own capitalization where reasonable. AP allows `iPhone` but not all-caps brand stylings (`adidas` → `Adidas` in AP).
- **Headlines:** sentence case (capitalize only the first word and proper nouns), not title case.

### Identity terms (2020+ AP updates)
- **`Black`** capitalized as a racial, ethnic, or cultural identifier.
- **`Indigenous`** capitalized when referring to original inhabitants.
- **`white`** lowercase as a racial identifier (AP retained this distinction in 2020).
- **`African American`**: no hyphen.
- **`Asian American`, `Hispanic`, `Latino/Latina/Latinx`**: capitalized; use the term the subject prefers.

## Common word choices

| Use | Instead of | Why |
|-----|-----------|-----|
| `more than` *or* `over` | (either) | AP relaxed this rule in 2014; both are acceptable for quantities |
| `fewer` | `less` | For countable items (`fewer cars`, `fewer than 10`) |
| `less` | `fewer` | For mass nouns (`less water`, `less time`) |
| `that` | `which` | For restrictive clauses (essential to meaning, no commas) |
| `which` | `that` | For nonrestrictive clauses (extra info, set off with commas) |
| `said` | `stated`, `noted`, `claimed` | Default attribution verb |
| `because` | `due to the fact that` | Wordiness |
| `about` | `approximately` | Wordiness |
| `health care` (two words) | `healthcare` | AP keeps two words; **BCBS VT house style differs — see bcbs-brand** |
| `email` | `e-mail` | Hyphen dropped in 2011 |
| `website` | `web site`, `Web site` | One word, lowercase since 2010 |
| `internet` | `Internet` | Lowercased in 2016 |
| `online` | `on-line` | One word, no hyphen |
| `smartphone` | `smart phone` | One word |

### Restrictive vs. nonrestrictive
- **Restrictive (use `that`, no commas):** `The bill that passed yesterday includes tax cuts.` (Which bill? The one that passed.)
- **Nonrestrictive (use `which`, set off with commas):** `The bill, which passed yesterday, includes tax cuts.` (We already know which bill.)

## State names

The 2014 update is worth memorizing because it surprises people who learned older AP:

- **In story body:** spell out state names. `She lives in Vermont.`
- **In datelines, photo captions, lists, tables:** use AP abbreviations (not postal codes): `Calif.`, `N.Y.`, `Mass.`, `Conn.`, `Vt.`, `N.H.`
- **With full mailing addresses:** postal codes (`Burlington, VT 05401`).
- **Eight states are never abbreviated:** Alaska, Hawaii, Idaho, Iowa, Maine, Ohio, Texas, Utah.

## Headlines

- **Sentence case**, not title case: `Council approves zoning change`.
- **Present tense** for past events: `Council approves` (not `approved`).
- **Infinitive** for future events: `Mayor to announce plan`.
- **Numerals** are acceptable in headlines even when AP would spell them out in body (`3 arrested in protest`).
- **No periods** at the end. **No exclamation points** in hard news.
- **Single quotes** for any quoted material in a headline.
- Active voice. Specific verbs. Avoid `is`, `are`, `was`, `were` as the main verb where another verb is available.

## Press releases and announcements

- **First sentence:** who, what, when, where — in that order when possible.
- **Dateline:** `BURLINGTON, Vt., May 15, 2026 —` (city in caps, state in AP abbreviation, full date, em dash).
- **Boilerplate "about" paragraph** at the end (lowercase about): one paragraph, no fluff, links if appropriate.
- **Contact line** at the very top right or very bottom: name, title, phone, email.
- **Quotes:** at least one, attributed to a named, titled spokesperson. Avoid generic corporate quotes; use language a real human would say.

## Ledes (opening paragraphs)

- **Hard news lede:** the most important fact first. Aim for 35 words or fewer.
- **One sentence is ideal.** If you need two, make them both short.
- **Inverted pyramid:** most important info → next most important → background → context.
- **The five Ws:** who, what, when, where, why (and how when relevant). Not all five must appear in the lede, but the most newsworthy must.

**Too long:**
> The city council, which has been debating the issue for several months and heard from dozens of residents at multiple public meetings, voted Tuesday night to approve a controversial new zoning ordinance that would allow high-rise buildings in the downtown area.

**Right:**
> The city council approved a zoning ordinance Tuesday that allows high-rise buildings downtown, ending months of debate.

## Pre-publish checklist

Run through this before declaring an AP-style draft done:

- [ ] Numbers follow AP rules (spelled out 1-9, numerals 10+, exceptions noted)
- [ ] No sentence starts with a numeral
- [ ] Dates use AP month abbreviations correctly (and only with a day)
- [ ] Times use `a.m.`/`p.m.` lowercase with periods; `noon`/`midnight` spelled out
- [ ] State names spelled out in body, AP abbreviations in lists/captions
- [ ] Attribution uses `said` past tense, after the quote
- [ ] Names verified spelling on first reference; last name only after
- [ ] Formal titles capitalized only directly before a name
- [ ] No Oxford comma unless ambiguity demands it
- [ ] Periods and commas inside quotes; colons and semicolons outside
- [ ] `that`/`which` used correctly with restrictive/nonrestrictive distinction
- [ ] `fewer`/`less` correct for countable/mass nouns
- [ ] No unattributed opinion in news copy
- [ ] No editorializing adjectives (`controversial`, `failed`, `notorious`) unless attributed
- [ ] Headline in sentence case, no period, active voice, present tense
- [ ] Lede under 35 words, leads with the news

## Red flags

If any of these appear in news copy, reconsider:

- `very`, `extremely`, `really`, `quite`, `rather` (intensifiers without substance)
- Exclamation points (almost never appropriate in news)
- First-person pronouns (`I`, `we`, `us`) unless first-person column
- `There is` / `There are` openers (weak; rewrite with a real verb)
- `In order to` (drop `in order`)
- `At this point in time` (now)
- `Due to the fact that` (because)
- Adjective stacks: `large, gleaming, modern, six-story building` — pick the one that matters
- Passive voice that hides the actor (`mistakes were made`)
- Editorializing verbs (`admitted`, `confessed`, `claimed`) when neutral verbs work

## House style overrides

AP is the default register, not the final word. Override when the audience demands it:

- **BCBS VT:** Use `bcbs-brand`. Key conflicts: `healthcare` (one word, BCBS) vs. `health care` (AP); approved organization names; brand voice mechanics.
- **Personal voice:** Use `oliver-tone` after AP for any prose Oliver puts his name on; AP gives the bones, Oliver's voice gives the cadence.
- **AI-tell removal:** Use `humanizer` to scrub AI-generated patterns. Apply *before* AP-checking, since the rewrite may introduce new AP issues.

## When you're not sure

1. **Look it up in Merriam-Webster Collegiate** (via the `merriam-webster` MCP server in `ames-general-mcps`). AP defers to Webster's Collegiate for spelling and word meaning, so `define`, `synonyms`, and `spell` from that server are the right first stop for word-level questions.
2. Check Oliver's `data/ap/` notes (this skill's gitignored folder) for Stylebook excerpts and house-specific rulings.
3. Check apstylebook.com (Oliver has a subscription).
4. If still unsure, flag it explicitly: `"I applied AP rule X here, but the Stylebook may have a more specific entry — worth a check."` Don't invent a rule.

## Recent AP updates worth knowing

These are recent enough that older drafts may not reflect them:

- **2014:** State names spelled out in story body (use AP abbreviations only in datelines, captions, lists, tables).
- **2014:** `more than` no longer mandatory over `over` for quantities; both acceptable.
- **2016:** `internet` lowercased.
- **2017:** Singular `they` acceptable for non-binary individuals and as a gender-neutral pronoun where rewriting is awkward.
- **2019:** `%` symbol allowed with numerals (`5%`); `5 percent` still acceptable.
- **2020:** `Black` capitalized as a racial identifier; `white` retained lowercase. `Indigenous` capitalized when referring to original inhabitants.

Verify any of the above against the current AP Stylebook if the writing will be public — AP guidance evolves.

---

*This skill paraphrases established AP Style rules with original examples. For authoritative rulings on specific entries, consult Oliver's licensed AP Stylebook subscription at [apstylebook.com](https://www.apstylebook.com/).*
