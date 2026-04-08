document.addEventListener("DOMContentLoaded", () => {
  for (const toggle of document.querySelectorAll("[data-disclosure-target]")) {
    toggle.addEventListener("click", () => {
      const target = document.querySelector(toggle.getAttribute("data-disclosure-target") || "");
      if (target) target.toggleAttribute("hidden");
    });
  }
});
