# cmux Browser Automation — Full Reference

Complete reference for `cmux browser` commands. Read this when doing anything
beyond basic navigate/snapshot/click in the cmux browser.

## Table of Contents

- [Targeting](#targeting)
- [Navigation](#navigation)
- [Waiting](#waiting)
- [DOM Interaction](#dom-interaction)
- [Inspection](#inspection)
- [Finding Elements](#finding-elements)
- [JavaScript](#javascript)
- [Tabs](#tabs)
- [Frames](#frames)
- [Dialogs](#dialogs)
- [Downloads](#downloads)
- [Cookies & Storage](#cookies--storage)
- [State Snapshots](#state-snapshots)
- [Console & Errors](#console--errors)
- [Patterns](#patterns)

## Targeting

Most subcommands need a target surface. Positional and flag forms are equivalent:

```bash
cmux browser surface:2 url              # positional
cmux browser --surface surface:2 url    # flag (before subcommand)
```

Discover browser metadata:
```bash
cmux browser identify
cmux browser identify --surface surface:2
```

## Navigation

```bash
cmux browser open https://example.com           # new browser pane
cmux browser open-split https://example.com      # new browser as a split

cmux browser surface:2 navigate https://example.org --snapshot-after
cmux browser surface:2 back
cmux browser surface:2 forward
cmux browser surface:2 reload --snapshot-after
cmux browser surface:2 url                       # get current URL

cmux browser surface:2 focus-webview             # focus the web content
cmux browser surface:2 is-webview-focused        # check if web content focused
```

## Waiting

Block until a condition is met. Essential for SPAs and dynamic pages.

```bash
cmux browser surface:2 wait --load-state complete --timeout-ms 15000
cmux browser surface:2 wait --selector "#checkout" --timeout-ms 10000
cmux browser surface:2 wait --text "Order confirmed"
cmux browser surface:2 wait --url-contains "/dashboard"
cmux browser surface:2 wait --function "window.__appReady === true"
```

## DOM Interaction

Mutating actions support `--snapshot-after` for fast verification.

```bash
# Click and mouse
cmux browser surface:2 click "button[type='submit']" --snapshot-after
cmux browser surface:2 dblclick ".item-row"
cmux browser surface:2 hover "#menu"
cmux browser surface:2 focus "#email"
cmux browser surface:2 scroll-into-view "#pricing"

# Checkboxes
cmux browser surface:2 check "#terms"
cmux browser surface:2 uncheck "#newsletter"

# Text input
cmux browser surface:2 type "#search" "query text"         # appends
cmux browser surface:2 fill "#email" --text "user@test.com" # clears first
cmux browser surface:2 fill "#email" --text ""              # clear field

# Keyboard
cmux browser surface:2 press Enter
cmux browser surface:2 keydown Shift
cmux browser surface:2 keyup Shift

# Selection and scroll
cmux browser surface:2 select "#region" "us-east"
cmux browser surface:2 scroll --dy 800 --snapshot-after
cmux browser surface:2 scroll --selector "#log-view" --dx 0 --dy 400
```

## Inspection

### Snapshots (DOM tree)

```bash
cmux browser surface:2 snapshot                              # full DOM tree
cmux browser surface:2 snapshot --interactive                # interactive elements only
cmux browser surface:2 snapshot --interactive --compact      # compact interactive
cmux browser surface:2 snapshot --interactive --cursor       # include cursor position
cmux browser surface:2 snapshot --selector "main" --max-depth 5  # scoped
```

Snapshots return `[ref=eN]` handles for clicking/interacting.

### Screenshots

```bash
cmux browser surface:2 screenshot --out /tmp/page.png
```

### Getters

```bash
cmux browser surface:2 get title
cmux browser surface:2 get url
cmux browser surface:2 get text "h1"                         # text of selector
cmux browser surface:2 get html "main"                       # innerHTML
cmux browser surface:2 get value "#email"                    # input value
cmux browser surface:2 get attr "a.primary" --attr href      # attribute
cmux browser surface:2 get count ".row"                      # element count
cmux browser surface:2 get box "#checkout"                   # bounding box
cmux browser surface:2 get styles "#total" --property color  # computed style
```

### State checks

```bash
cmux browser surface:2 is visible "#checkout"
cmux browser surface:2 is enabled "button[type='submit']"
cmux browser surface:2 is checked "#terms"
```

## Finding Elements

Find elements by semantic role, text, label, and more:

```bash
cmux browser surface:2 find role button --name "Continue"
cmux browser surface:2 find text "Order confirmed"
cmux browser surface:2 find label "Email"
cmux browser surface:2 find placeholder "Search"
cmux browser surface:2 find alt "Product image"
cmux browser surface:2 find title "Open settings"
cmux browser surface:2 find testid "save-btn"
cmux browser surface:2 find first ".row"
cmux browser surface:2 find last ".row"
cmux browser surface:2 find nth 2 ".row"
```

### Highlight

```bash
cmux browser surface:2 highlight "#checkout"   # visual highlight for debugging
```

## JavaScript

```bash
cmux browser surface:2 eval "document.title"
cmux browser surface:2 eval --script "window.location.href"

# Inject scripts/styles (persist across navigations with addinitscript)
cmux browser surface:2 addinitscript "window.__cmuxReady = true;"
cmux browser surface:2 addscript "document.querySelector('#name')?.focus()"
cmux browser surface:2 addstyle "#debug-banner { display: none !important; }"
```

## Tabs

Browser tab operations within a browser surface:

```bash
cmux browser surface:2 tab list
cmux browser surface:2 tab new https://example.com/pricing
cmux browser surface:2 tab switch 1              # by index
cmux browser surface:2 tab switch surface:7       # by surface ref
cmux browser surface:2 tab close                  # current tab
cmux browser surface:2 tab close surface:7        # specific tab
```

## Frames

Navigate into iframes:

```bash
cmux browser surface:2 frame "iframe[name='checkout']"
cmux browser surface:2 click "#pay-now"           # clicks inside the iframe
cmux browser surface:2 frame main                 # return to top-level
```

## Dialogs

Handle JavaScript alert/confirm/prompt dialogs:

```bash
cmux browser surface:2 dialog accept
cmux browser surface:2 dialog accept "Confirmed by automation"
cmux browser surface:2 dialog dismiss
```

## Downloads

```bash
cmux browser surface:2 click "a#download-report"
cmux browser surface:2 download --path /tmp/report.csv --timeout-ms 30000
```

## Cookies & Storage

```bash
# Cookies
cmux browser surface:2 cookies get
cmux browser surface:2 cookies get --name session_id
cmux browser surface:2 cookies set session_id abc123 --domain example.com --path /
cmux browser surface:2 cookies clear --name session_id
cmux browser surface:2 cookies clear --all

# Local storage
cmux browser surface:2 storage local set theme dark
cmux browser surface:2 storage local get theme             # returns "OK"; to read the value:
cmux browser surface:2 eval "localStorage.getItem('theme')" # → "dark"
cmux browser surface:2 storage local clear

# Session storage
cmux browser surface:2 storage session set flow onboarding
cmux browser surface:2 eval "sessionStorage.getItem('flow')" # → "onboarding"
```

## State Snapshots

Save and restore full browser state (cookies + storage + more):

```bash
cmux browser surface:2 state save /tmp/browser-state.json
# ...later...
cmux browser surface:2 state load /tmp/browser-state.json
cmux browser surface:2 reload
```

## Console & Errors

```bash
cmux browser surface:2 console list
cmux browser surface:2 console clear

cmux browser surface:2 errors list
cmux browser surface:2 errors clear
```

## Patterns

### Navigate, wait, inspect

```bash
cmux browser open https://example.com/login
cmux browser surface:2 wait --load-state complete --timeout-ms 15000
cmux browser surface:2 snapshot --interactive --compact
```

### Fill a form and verify

```bash
cmux browser surface:2 fill "#email" --text "user@example.com"
cmux browser surface:2 fill "#password" --text "$PASSWORD"
cmux browser surface:2 click "button[type='submit']" --snapshot-after
cmux browser surface:2 wait --text "Welcome"
cmux browser surface:2 is visible "#dashboard"
```

### Debug on failure

```bash
cmux browser surface:2 console list
cmux browser surface:2 errors list
cmux browser surface:2 screenshot --out /tmp/failure.png
cmux browser surface:2 snapshot --interactive --compact
```
