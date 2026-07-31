# Chat Workspace Full-Screen Layout — Design

**Date:** 2026-07-31
**Project:** Task 1 — Flask AI chatbot

## Problem

The chat page currently renders inside a padded `<main>` with a fixed-height thread
(`max-height: 50vh`, `min-height: 340px`), so the workspace scrolls with the page and
wastes viewport space. The user wants the chat workspace to fill the entire browser
window.

## Goals

- The chat workspace fills the full viewport height.
- The top bar stays visible.
- Edge-to-edge, full-bleed layout (no outer padding, no rounded-card gaps around the workspace).
- The chat thread scrolls internally; the page itself never scrolls on desktop.
- No template, JS, or test changes — CSS only.

## Approach

Pure CSS scoped via `body:has(.chat-layout)` so only the chat page is affected.
No hardcoded top-bar height: flexbox gives the top bar its natural height and lets
`<main>` flex-fill the remainder.

## Implementation

All changes in `static/css/style.css`.

### Layout shell

```css
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
```

The top bar (and any flash messages) take their natural height; `<main>` fills the rest.
`100dvh` handles mobile URL-bar resize; graceful degradation on older browsers is the
current padded layout (acceptable).

### Workspace

```css
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

- Grid columns (`280px 1fr`) and the `1rem` gap are unchanged.
- The thread flex-fills the panel and scrolls internally (the existing `50vh` cap and
  `340px` min are overridden).
- The chat form keeps its natural height, pinned at the bottom of the panel.
- The sidebar scrolls internally if its content is taller than the viewport.

### Responsive (< 900px, stacked layout)

The existing `@media (max-width: 900px)` rule switches the grid to a single column.
On small screens the sidebar stacks above the thread, so full-bleed fixed height would
squeeze the thread. Restore page scrolling and give the thread a bounded share:

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

## Browser Support

`body:has(.chat-layout)` requires `:has()`: Chrome 105+, Edge 105+, Firefox 121+,
Safari 15.4+ (all released by 2023). Older browsers fall back to the current layout.

## Testing

- No automated tests for CSS.
- Manual verification:
  1. Log in as `tester@example.com` / `password123`.
  2. Open `/chat` on a desktop window: the workspace fills the viewport, no page
     scrollbar, the thread scrolls internally, the chat form is pinned at the bottom,
     and the top bar is visible.
  3. Narrow the window below 900px: page scrolls again and the thread keeps a usable
     height.
  4. Confirm other pages (home, login, signup) are visually unchanged.
