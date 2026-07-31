# Chat Workspace Glass UI — Design

**Date:** 2026-07-31
**Project:** Task 1 — Flask AI chatbot

## Problem

The chat page is functional but flat and static. The user wants it to feel
interactive and modern with motion and micro-interactions. Chosen direction
(validated via animated mockups): a dark, glassy workspace (style "C · Glass")
with animated bubbles, bouncing typing dots, hover/press feedback, smooth theme
transitions, and a scroll-to-bottom button.

## Scope

- **Chat page only.** Home, login, signup, and the top bar stay as-is (the top
  bar renders on the chat page too, but keeps its existing themed look).
- **No new dependencies.** Pure CSS + the existing vanilla `chat.js`.
- **No Python/backend changes.**

## Visual Design

The chat workspace (`.history-panel` + `.chat-panel`) gets a permanent dark-glass
look regardless of light/dark mode:

- Panel background: deep slate gradient with subtle `backdrop-filter: blur`.
- Accent color continues to flow from the app theme (`html[data-theme]`) so glows
  and highlights keep the ocean/midnight/sunset personality.
- User bubbles: accent gradient fill with a soft glow `box-shadow`.
- Bot bubbles: translucent glass (`rgba` background, blur, thin light border).
- Thread background: slightly translucent so the glass shows through.

**Consequence (accepted):** because the workspace is always dark, the chat-page
dark-mode toggle and theme select now influence the accent color and the top bar,
not the workspace background.

## Micro-Interactions

1. **Bubble entrance animation** — each appended bubble animates in with a soft
   blur-fade and slight rise (the validated "C · Glass" motion).
2. **Typing indicator** — replace the italic "Thinking..." text with three
   bouncing, accent-colored dots, staggered.
3. **Send button** — accent glow `box-shadow` on hover; subtle scale-down on
   active press.
4. **Input** — focus glow ring.
5. **Sidebar hover** — hover/press feedback on history items, personality chips,
   and the theme controls, with smooth transitions.
6. **Smooth theme transitions** — `transition` on colors/backgrounds/borders
   (~0.25s) when switching themes or light/dark.
7. **Scroll-to-bottom button** — floating circular button at the bottom-right of
   the thread; appears only when the thread is scrolled up from the bottom; click
   glides smoothly to the bottom; hidden at the bottom.
8. **Reduced motion** — `@media (prefers-reduced-motion: reduce)` disables the
   animations.

## Implementation

### Files

- **Create:** `static/css/chat-glass.css` — all glass styling, animations, and
  transitions for the chat page. Loaded ONLY on the chat page so `style.css` and
  other pages are untouched.
- **Modify:** `templates/chat.html` — add `<link>` to `chat-glass.css` (after the
  base `style.css` link), add the scroll-to-bottom button element
  (`<button id="scroll-bottom" class="scroll-bottom" aria-label="Scroll to bottom">`).
- **Modify:** `static/js/chat.js` — build the typing dots container instead of
  "Thinking..." text; add the scroll listener that toggles the scroll-to-bottom
  button and its click handler.
- **Test:** `tests/test_chat_api.py` (or a suitable existing test file) — add a
  test asserting the chat page response contains the `chat-glass.css` link and the
  `scroll-bottom` button.

### Behavior details

- `appendBubble` keeps its current XSS-safe behavior (user = `textContent`, bot =
  `formatMarkdown`). The entrance animation applies via CSS on insertion — no JS
  change needed there.
- The scroll-to-bottom button must not appear during normal auto-scroll after
  sending a message. Logic: show the button when `thread.scrollHeight -
  thread.scrollTop - thread.clientHeight > ~120px`; hide otherwise. Update on
  `thread` scroll events and after append.
- Typing dots markup (created in `chat.js`, removed in `finally` as today):

```html
<div class="bubble bot typing">
  <span class="typing-dots"><i></i><i></i><i></i></span>
</div>
```

## Testing

- `pytest -q` → expect 17 passing + 1 new test = 18.
- `node --test tests/formatter.test.js` → expect 11 passing (unchanged).
- Manual browser verification:
  1. Log in as `tester@example.com` / `password123`, open `/chat`.
  2. Send a message: user bubble animates in, typing dots bounce, bot reply
     animates in. No raw "Thinking..." text.
  3. Scroll the thread up: scroll-to-bottom button fades in; click glides down and
     hides the button.
  4. Hover send button, chips, history items: glow/hover feedback. Focus the
     input: glow ring.
  5. Switch themes and light/dark: colors cross-fade smoothly.
  6. Narrow the window below 900px: workspace still looks correct (mobile rules
     from the full-screen layout continue to apply).
  7. Other pages (home/login/signup) unchanged.
  8. OS-level "reduce motion" setting (or devtools emulation) disables animations.
