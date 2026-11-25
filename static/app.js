// Logika strony: wysyła tekst do /api/check i pokazuje kartę z werdyktem.

const form = document.getElementById("check-form");
const textarea = document.getElementById("message");
const checkBtn = document.getElementById("check-btn");
const pasteBtn = document.getElementById("paste-btn");
const againBtn = document.getElementById("again-btn");
const errorBox = document.getElementById("error");
const statusBox = document.getElementById("status");
const result = document.getElementById("result");
const card = document.getElementById("card");
const verdictTitle = document.getElementById("verdict-title");
const checkLabel = document.getElementById("check-label");

let busy = false; // true, gdy czekamy na odpowiedź serwera

// Gdy ktoś wyłączył animacje w systemie, przewijamy od razu, bez płynnego ruchu.
function scrollBehavior() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
  textarea.setAttribute("aria-invalid", "true");
}

function hideError() {
  errorBox.hidden = true;
  textarea.removeAttribute("aria-invalid");
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
  // Klasa werdyktu wybiera w CSS kolor karty i jedną z trzech ikon.
  card.className = `verdict ${data.verdict}`;
  verdictTitle.textContent = data.title;
  fillList("advice", data.advice);
  fillList("reasons", data.reasons);
  result.hidden = false;
  statusBox.textContent = "Wynik jest gotowy.";
  // Fokus na tytule wyniku: czytnik ekranu od razu go przeczyta.
  verdictTitle.focus({ preventScroll: true });
  result.scrollIntoView({ behavior: scrollBehavior(), block: "start" });
}

// Zamienia błąd sieci na prosty komunikat z tym, co zrobić.
function networkErrorMessage() {
  if (!navigator.onLine) {
    return "Nie ma internetu. Włącz Wi-Fi albo dane komórkowe i naciśnij „Sprawdź wiadomość” jeszcze raz.";
  }
  return "Nie udało się połączyć ze stroną. Odczekaj chwilę i spróbuj jeszcze raz.";
}

async function check(text) {
  if (busy) return; // nie wysyłamy drugiego zapytania, zanim przyjdzie pierwsze
  hideError();
  result.hidden = true;
  if (!text.trim()) {
    showError("Najpierw wklej treść wiadomości albo link.");
    textarea.focus();
    return;
  }

  // Zamiast "disabled" używamy aria-disabled: przycisk nie traci fokusu z klawiatury.
  busy = true;
  checkBtn.setAttribute("aria-disabled", "true");
  form.setAttribute("aria-busy", "true");
  checkBtn.classList.add("is-busy"); // pokazuje kręcące się kółko
  checkLabel.textContent = "Sprawdzam…";
  statusBox.textContent = "Sprawdzam wiadomość…";
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
        : "Coś poszło nie tak po naszej stronie. Odczekaj minutę i spróbuj jeszcze raz.");
      statusBox.textContent = "";
      return;
    }
    showResult(data);
  } catch {
    showError(networkErrorMessage());
    statusBox.textContent = "";
  } finally {
    busy = false;
    checkBtn.removeAttribute("aria-disabled");
    form.removeAttribute("aria-busy");
    checkBtn.classList.remove("is-busy");
    checkLabel.textContent = "Sprawdź wiadomość";
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  check(textarea.value);
});

pasteBtn.addEventListener("click", async () => {
  try {
    textarea.value = await navigator.clipboard.readText();
    hideError();
    textarea.focus();
  } catch {
    showError("Nie udało się wkleić automatycznie. Przytrzymaj palec w polu tekstowym i wybierz „Wklej”.");
  }
});

againBtn.addEventListener("click", () => {
  textarea.value = "";
  result.hidden = true;
  statusBox.textContent = "";
  textarea.focus();
  window.scrollTo({ top: 0, behavior: scrollBehavior() });
});

// --- Wskazówka "dodaj do ekranu głównego" (tylko iPhone/iPad w Safari) ---
const HINT_KEY = "iosHintClosed";
const hint = document.getElementById("ios-hint");

function isIosSafari() {
  const ua = navigator.userAgent;
  // iPad z nowym iOS udaje Maca, ale ma ekran dotykowy.
  const ios = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  // Chrome, Firefox, Edge i Opera na iPhonie mają w nazwie CriOS, FxiOS, EdgiOS, OPiOS.
  const otherBrowser = /CriOS|FxiOS|EdgiOS|OPiOS/.test(ua);
  return ios && !otherBrowser;
}

function isStandalone() {
  // Strona otwarta z ikony na ekranie głównym (wtedy wskazówka nie ma sensu).
  return window.navigator.standalone === true || window.matchMedia("(display-mode: standalone)").matches;
}

function hintWasClosed() {
  try {
    return localStorage.getItem(HINT_KEY) === "1";
  } catch {
    return false; // np. tryb prywatny: localStorage niedostępny
  }
}

if (isIosSafari() && !isStandalone() && !hintWasClosed()) {
  hint.hidden = false;
}

document.getElementById("ios-hint-close").addEventListener("click", () => {
  hint.hidden = true;
  try {
    localStorage.setItem(HINT_KEY, "1");
  } catch {
    // Nie da się zapisać? Trudno, wskazówka wróci przy następnej wizycie.
  }
  textarea.focus(); // fokus nie może zniknąć razem z ukrytym przyciskiem
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
