const toggle = document.querySelector("[data-alert-toggle]");
const knob = document.querySelector("[data-alert-knob]");
const text = document.querySelector("[data-alert-text]");

let enabled = true;

function render() {
  toggle.style.background = enabled ? "#2a8a5f" : "#cdd7d6";
  knob.style.transform = enabled ? "translateX(22px)" : "translateX(0)";
  text.textContent = enabled
    ? "On: clinician and emergency contact alerts are enabled."
    : "Off: falls are logged, but notifications are paused.";
}

if (toggle) {
  toggle.addEventListener("click", () => {
    enabled = !enabled;
    render();
  });
  render();
}
