// Logika strony: wysyła tekst do /api/check i pokazuje kartę z werdyktem.

const form = document.getElementById("check-form");
const textarea = document.getElementById("message");
const checkBtn = document.getElementById("check-btn");
const pasteBtn = document.getElementById("paste-btn");
const againBtn = document.getElementById("again-btn");
const errorBox = document.getElementById("error");
const result = document.getElementById("result");
const card = document.getElementById("card");

const ICONS = { scam: "⛔", suspicious: "⚠️", no_signs: "✅" };

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function fillList(id, items) {
  const list = document.getElementById(id);
  list.replaceChildren(...items.map((text) => {
    const li = document.createElement("li");
    li.textContent = text; // textContent, nie innerHTML: brak ryzyka XSS
    return li;
  }));
}

function showResult(data) {
  card.className = `card ${data.verdict}`;
  document.getElementById("verdict-icon").textContent = ICONS[data.verdict] || "";
  document.getElementById("verdict-title").textContent = data.title;
  fillList("advice", data.advice);
  fillList("reasons", data.reasons);
  result.hidden = false;
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function check(text) {
  errorBox.hidden = true;
  result.hidden = true;
  if (!text.trim()) {
    showError("Najpierw wklej treść wiadomości albo link.");
    textarea.focus();
    return;
  }

  checkBtn.disabled = true;
  checkBtn.textContent = "Sprawdzam…";
  try {
    const response = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      showError(data.detail && typeof data.detail === "string"
        ? data.detail
        : "Coś poszło nie tak. Spróbuj jeszcze raz.");
      return;
    }
    showResult(data);
  } catch {
    showError("Brak połączenia z internetem. Sprawdź połączenie i spróbuj ponownie.");
  } finally {
    checkBtn.disabled = false;
    checkBtn.textContent = "SPRAWDŹ";
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  check(textarea.value);
});

pasteBtn.addEventListener("click", async () => {
  try {
    textarea.value = await navigator.clipboard.readText();
    textarea.focus();
  } catch {
    showError("Nie udało się wkleić automatycznie. Przytrzymaj palec w polu tekstowym i wybierz „Wklej”.");
  }
});

againBtn.addEventListener("click", () => {
  textarea.value = "";
  result.hidden = true;
  textarea.focus();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// "Udostępnij" na Androidzie: system otwiera stronę z ?text=...&url=...
const params = new URLSearchParams(window.location.search);
const shared = [params.get("title"), params.get("text"), params.get("url")].filter(Boolean).join("\n");
if (shared) {
  textarea.value = shared;
  history.replaceState(null, "", "/"); // usuwamy treść z adresu strony
  check(shared);
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}
