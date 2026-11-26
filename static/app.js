// Logika strony: wysyła tekst do /api/check i pokazuje kartę z werdyktem.

const form = document.getElementById("check-form");
const textarea = document.getElementById("message");
const checkBtn = document.getElementById("check-btn");
const pasteBtn = document.getElementById("paste-btn");
const againBtn = document.getElementById("again-btn");
const errorBox = document.getElementById("error");
const statusBox = document.getElementById("status");
const result = document.getElementById("result");
const verdictBox = document.getElementById("verdict");
const verdictTitle = document.getElementById("verdict-title");
const checkLabel = document.getElementById("check-label");
const counter = document.getElementById("counter");

// Ten sam limit co MAX_TEXT_LENGTH na serwerze (app/config.py).
const MAX_LENGTH = 3000;
// Licznik pokazujemy dopiero blisko limitu, żeby nie rozpraszał przy krótkich SMS-ach.
const COUNTER_FROM = 2500;

let busy = false; // true, gdy czekamy na odpowiedź serwera

// Zamiast cicho ucinać tekst (atrybut maxlength), pokazujemy licznik i ostrzegamy.
function updateCounter() {
  const length = textarea.value.length;
  const over = length > MAX_LENGTH;
  counter.hidden = length < COUNTER_FROM;
  // Pełne zdanie zamiast "3100 / 3000": senior od razu wie, o co chodzi.
  counter.textContent = counter.hidden ? ""
    : over ? `Za długo o ${length - MAX_LENGTH} znaków (mieści się ${MAX_LENGTH}).`
    : `Wpisano ${length} z ${MAX_LENGTH} znaków.`;
  counter.classList.toggle("is-over", over);
  updateDescription();
}

// Czytnik ekranu czyta opis pola z aria-describedby. Wpisujemy tam tylko to,
// co jest widoczne: inaczej przeczytałby ukryty, stary komunikat o błędzie.
function updateDescription() {
  const ids = [counter, errorBox].filter((el) => !el.hidden).map((el) => el.id);
  if (ids.length) textarea.setAttribute("aria-describedby", ids.join(" "));
  else textarea.removeAttribute("aria-describedby");
}

// Gdy ktoś wyłączył animacje w systemie, przewijamy od razu, bez płynnego ruchu.
function scrollBehavior() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
}

// invalid = false dla podpowiedzi, które nie są błędem w treści (np. nieudane wklejanie).
function showError(message, invalid = true) {
  errorBox.textContent = message;
  errorBox.hidden = false;
  if (invalid) textarea.setAttribute("aria-invalid", "true");
  else textarea.removeAttribute("aria-invalid");
  updateDescription();
}

function hideError() {
  errorBox.hidden = true;
  errorBox.textContent = ""; // czyścimy, żeby stary komunikat nigdzie nie wrócił
  textarea.removeAttribute("aria-invalid");
  updateDescription();
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
  verdictBox.className = `verdict ${data.verdict}`;
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
  if (text.trim().length > MAX_LENGTH) {
    showError(`Wiadomość jest za długa: ma ${text.trim().length} znaków, a mieści się ${MAX_LENGTH}. `
      + "Wklej tylko najważniejszą część, na przykład fragment z linkiem.");
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

// Licznik odświeżamy przy każdej zmianie w polu (pisanie, wklejanie, usuwanie).
textarea.addEventListener("input", () => {
  updateCounter();
  if (!errorBox.hidden) hideError(); // ktoś poprawia tekst, więc stary błąd znika
});

pasteBtn.addEventListener("click", async () => {
  try {
    textarea.value = await navigator.clipboard.readText();
    updateCounter(); // zmiana z JS nie wywołuje zdarzenia "input"
    hideError();
    textarea.focus();
  } catch {
    showError("Nie udało się wkleić automatycznie. Wklej sam: przytrzymaj palec w polu i wybierz „Wklej” "
      + "albo na komputerze naciśnij Ctrl+V.", false);
  }
});

againBtn.addEventListener("click", () => {
  textarea.value = "";
  updateCounter();
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
  updateCounter();
  history.replaceState(null, "", "/"); // usuwamy treść z adresu strony
  check(shared);
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}
