# Chat Workspace Full-Screen Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the chat workspace fill the full browser viewport (edge-to-edge, internal thread scroll, top bar visible) using CSS only.

**Architecture:** Scope layout changes to the chat page with `body:has(.chat-layout)` so other pages are untouched. The body becomes a column-flex shell on the chat page; `<main>` flex-fills below the top bar; the chat panel is a column flex whose thread flex-fills and scrolls internally. On screens below 900px, the stacked layout restores page scrolling and gives the thread a bounded height.

**Tech Stack:** Plain CSS. No template, JS, or Python changes. No test framework for CSS — verification is manual.

**Environment notes:**
- Work from `C:\My Stuff\Python Projects\Task 1`.
- `Task 1` is NOT a git repo → skip all commit steps.
- Python is not on PATH. Use `& "$env:LOCALAPPDATA\Python\bin\python.exe"`.
- The dev server may already be running on http://127.0.0.1:5000 (Flask debug mode auto-reloads CSS, but restart anyway to be safe after edits).
- Test login: `tester@example.com` / `password123`.

---

### Task 1: Desktop full-screen layout

**Files:**
- Modify: `static/css/style.css` — append a "Full-screen chat workspace" section at the end of the file.

- [ ] **Step 1: Read the current CSS**

Read `static/css/style.css` fully. Confirm the existing rules: `.chat-layout` (`grid-template-columns: 280px 1fr`), `.chat-thread` (`min-height: 340px; max-height: 50vh`), and the media query at `@media (max-width: 900px)` switching the grid to one column.

- [ ] **Step 2: Append the desktop full-screen rules**

Append this exact block to the END of `static/css/style.css`:

```css
/* Full-screen chat workspace */
body:has(.chat-layout) {
    height: 100dvh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

body:has(.chat-layout) main {
    flex: 1;
    min-height: 0;
    padding: 0;
    display: flex;
}

.chat-layout {
    flex: 1;
    min-height: 0;
}

.chat-panel {
    display: flex;
    flex-direction: column;
    min-height: 0;
}

.chat-thread {
    flex: 1;
    min-height: 0;
    max-height: none;
}

.history-panel {
    min-height: 0;
    overflow-y: auto;
}
```

Rationale:
- `body:has(.chat-layout)` scopes everything to the chat page only.
- The top bar (and any flash messages) take their natural height; `main` flex-fills the rest, so no top-bar height is hardcoded.
- `.chat-thread` overrides the earlier `min-height: 340px; max-height: 50vh` so the thread flex-fills and scrolls internally.
- `.history-panel` scrolls internally if sidebar content is taller than the viewport.
- Existing grid columns (`280px 1fr`), the `1rem` gap, and the `.chat-form` layout are untouched; the form keeps its natural height pinned at the bottom of the panel.

- [ ] **Step 3: Verify the CSS is served**

Run: `Invoke-WebRequest -Uri "http://127.0.0.1:5000/static/css/style.css" -UseBasicParsing`
Expected: HTTP 200, and the response body contains `body:has(.chat-layout)`. If the server is not running, start it:

```powershell
Start-Process -FilePath "$env:LOCALAPPDATA\Python\bin\python.exe" -ArgumentList "app.py" -WorkingDirectory "C:\My Stuff\Python Projects\Task 1" -PassThru
```

---

### Task 2: Responsive stacking (< 900px)

**Files:**
- Modify: `static/css/style.css` — append a responsive media query after the Task 1 block.

- [ ] **Step 1: Append the responsive rules**

Append this exact block to the END of `static/css/style.css`:

```css
@media (max-width: 900px) {
    body:has(.chat-layout) {
        overflow-y: auto;
    }

    .chat-thread {
        min-height: 55vh;
        max-height: 70vh;
    }
}
```

Rationale:
- Below 900px the existing media query collapses the grid to one column, so the sidebar stacks above the thread. The fixed-height shell would squeeze the thread, so restore page scrolling (`overflow-y: auto`) and give the thread a bounded share of the viewport.
- This block is appended after all other rules, so it overrides the Task 1 desktop values at small widths.

- [ ] **Step 2: Verify CSS is served and order is correct**

Run: `Invoke-WebRequest -Uri "http://127.0.0.1:5000/static/css/style.css" -UseBasicParsing`
Expected: HTTP 200; the body ends with the `@media (max-width: 900px)` block appended after the `body:has(.chat-layout)` rules.

---

### Task 3: End-to-end manual verification

- [ ] **Step 1: Confirm the app runs and login works**

Run: `Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -UseBasicParsing`
Expected: HTTP 200. Then in a browser, log in as `tester@example.com` / `password123`.

- [ ] **Step 2: Verify desktop layout**

In a desktop-width browser window, open `/chat`:
- The workspace fills the entire viewport (no outer padding, no page scrollbar).
- The top bar is visible at the top.
- The chat thread scrolls internally when it overflows.
- The chat input row is pinned at the bottom of the chat panel.
- The sidebar (history + personality + theme) spans the full viewport height and scrolls internally if its content is tall.
- The page does NOT scroll at desktop width.

- [ ] **Step 3: Verify responsive layout**

Narrow the browser window below 900px:
- The sidebar stacks above the thread.
- The page scrolls again.
- The thread keeps a usable height (roughly 55vh–70vh).

- [ ] **Step 4: Verify other pages are unaffected**

Check `/` (home), `/login`, and `/signup` in a browser: layouts look the same as before (padded, card-based). If Flask debug reload already served the new CSS, no restart is needed; otherwise restart the server and re-check.

- [ ] **Step 5: Run the regression suites**

Run: `& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pytest -q`
Expected: 17 passed (CSS change must not affect Python tests).

Run: `node --test tests/formatter.test.js`
Expected: 11 passed.

---

## Self-Review Summary

- **Spec coverage:** Task 1 covers the layout shell, workspace rules, and thread/sidebar internal scroll; Task 2 covers the <900px responsive behavior; Task 3 covers manual verification and regression suites. All spec requirements mapped.
- **No placeholders:** every CSS block is provided verbatim.
- **Consistency:** property names match the existing stylesheet (`chat-layout`, `chat-thread`, `chat-panel`, `history-panel`); appended blocks override earlier declarations via cascade order.
