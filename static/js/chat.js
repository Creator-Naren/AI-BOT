const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const thread = document.getElementById("chat-thread");
const historyList = document.getElementById("history-list");
const themeSelect = document.getElementById("theme-select");
const darkModeToggle = document.getElementById("dark-mode-toggle");
const scrollButton = document.getElementById("scroll-bottom");
let sending = false;

function appendBubble(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  if (role === "bot") {
    bubble.innerHTML = formatMarkdown(text);
  } else {
    bubble.textContent = text;
  }
  thread.appendChild(bubble);
  thread.scrollTop = thread.scrollHeight;
  updateScrollButton();
}

function updateScrollButton() {
  const distanceFromBottom =
    thread.scrollHeight - thread.scrollTop - thread.clientHeight;
  scrollButton?.classList.toggle("visible", distanceFromBottom > 120);
}

async function loadHistory() {
  const response = await fetch("/api/history");
  const payload = await response.json();
  historyList.innerHTML = "";
  if (!payload.conversations?.length) {
    historyList.innerHTML = "<li>No chats yet.</li>";
    return;
  }

  payload.conversations.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `${item.title} (${new Date(item.updated_at).toLocaleString()})`;
    historyList.appendChild(li);
  });
}

async function persistTheme() {
  const body = {
    theme: themeSelect.value,
    dark_mode: darkModeToggle.checked,
  };
  const response = await fetch("/api/preferences/theme", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) return;
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (sending) return;
  const message = input.value.trim();
  if (!message) return;

  sending = true;
  const sendButton = form.querySelector("button[type='submit']");
  if (sendButton) sendButton.disabled = true;

  appendBubble("user", message);
  input.value = "";

  const typing = document.createElement("div");
  typing.className = "bubble bot typing";
  typing.innerHTML = '<span class="typing-dots"><i></i><i></i><i></i></span>';
  thread.appendChild(typing);
  thread.scrollTop = thread.scrollHeight;
  updateScrollButton();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!response.ok) throw new Error("Chat request failed");
    const payload = await response.json();
    appendBubble("bot", payload.assistant_message || payload.message || "Unable to process.");
  } catch {
    appendBubble("bot", "Unable to process your message. Please try again.");
  } finally {
    typing.remove();
    if (sendButton) sendButton.disabled = false;
    sending = false;
  }
  await loadHistory();
});

themeSelect?.addEventListener("change", async () => {
  document.documentElement.dataset.theme = themeSelect.value;
  await persistTheme();
});

darkModeToggle?.addEventListener("change", async () => {
  document.documentElement.classList.toggle("dark", darkModeToggle.checked);
  await persistTheme();
});

if (themeSelect && window.initialTheme) {
  themeSelect.value = window.initialTheme;
}

const PERSONALITY_PRESETS = {
  "": "",
  friendly: "You are warm, encouraging, and approachable.",
  professional: "You are professional, precise, and to the point.",
  humorous: "You are witty and playful, using light humor where appropriate.",
};

const personalityInput = document.getElementById("personality-input");
const personalitySave = document.getElementById("personality-save");
const personalityStatus = document.getElementById("personality-status");

if (personalityInput) {
  personalityInput.value = window.initialPersonality || "";
}

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    personalityInput.value = PERSONALITY_PRESETS[chip.dataset.preset] || "";
    if (personalityStatus) personalityStatus.textContent = "";
  });
});

personalitySave?.addEventListener("click", async () => {
  if (personalitySave.disabled) return;
  personalitySave.disabled = true;
  const personality = (personalityInput?.value || "").trim();
  try {
    const response = await fetch("/api/preferences/personality", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ personality }),
    });
    if (!response.ok) throw new Error("Personality save failed");
    const payload = await response.json();
    if (payload.success && personalityStatus) {
      personalityStatus.textContent = "Saved";
      personalityStatus.classList.remove("error");
      setTimeout(() => (personalityStatus.textContent = ""), 2000);
    } else if (personalityStatus) {
      personalityStatus.textContent = "Save failed";
      personalityStatus.classList.add("error");
    }
  } catch {
    if (personalityStatus) {
      personalityStatus.textContent = "Save failed";
      personalityStatus.classList.add("error");
    }
  } finally {
    personalitySave.disabled = false;
  }
});

loadHistory();

thread?.addEventListener("scroll", updateScrollButton, { passive: true });
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
scrollButton?.addEventListener("click", () => {
  thread?.scrollTo({ top: thread.scrollHeight, behavior: reduceMotion ? "auto" : "smooth" });
});
