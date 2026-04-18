document.addEventListener("DOMContentLoaded", () => {
  const shell = document.querySelector(".app-shell");
  const navToggle = document.getElementById("nav-toggle");
  const asideToggle = document.getElementById("aside-toggle");
  const refreshIcons = () => {
    if (typeof lucide === "undefined") {
      return;
    }
    if (navToggle) {
      navToggle
        .querySelector("[data-lucide]")
        ?.setAttribute(
          "data-lucide",
          shell?.classList.contains("nav-collapsed") ? "panel-left-open" : "panel-left-close",
        );
    }
    if (asideToggle) {
      asideToggle
        .querySelector("[data-lucide]")
        ?.setAttribute(
          "data-lucide",
          shell?.classList.contains("aside-collapsed")
            ? "panel-right-open"
            : "panel-right-close",
        );
    }
    lucide.createIcons();
  };

  if (shell) {
    if (localStorage.getItem("nav-collapsed") === "true") {
      shell.classList.add("nav-collapsed");
    }
    if (localStorage.getItem("aside-collapsed") === "true") {
      shell.classList.add("aside-collapsed");
    }

    if (navToggle) {
      navToggle.addEventListener("click", () => {
        const isCollapsed = shell.classList.toggle("nav-collapsed");
        localStorage.setItem("nav-collapsed", isCollapsed);
        refreshIcons();
      });
    }

    if (asideToggle) {
      asideToggle.addEventListener("click", () => {
        const isCollapsed = shell.classList.toggle("aside-collapsed");
        localStorage.setItem("aside-collapsed", isCollapsed);
        refreshIcons();
      });
    }
  }

  refreshIcons();

  const trackedCards = document.querySelectorAll(
    ".panel, .read-result-card, .read-selected-context, .oversight-board__card, .oversight-board__column, .oversight-cleanup-board article, .admin-control-card, .admin-overview__shared-work, .admin-control-panel__state",
  );
  trackedCards.forEach((card) => {
    card.addEventListener("mousemove", (event) => {
      const rect = card.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      card.style.setProperty("--mouse-x", `${x}px`);
      card.style.setProperty("--mouse-y", `${y}px`);
    });
  });

  const trackedForms = [...document.querySelectorAll("form.governed-form")];
  if (!trackedForms.length) {
    return;
  }

  const formSignature = (trackedForm) => {
    const formData = new FormData(trackedForm);
    return JSON.stringify(
      [...formData.entries()].map(([name, fieldValue]) => [
        name,
        fieldValue instanceof File ? fieldValue.name : String(fieldValue),
      ]),
    );
  };
  const initialSignatures = new Map(
    trackedForms.map((trackedForm) => [trackedForm, formSignature(trackedForm)]),
  );
  const hasUnsavedChanges = () =>
    trackedForms.some((trackedForm) => formSignature(trackedForm) !== initialSignatures.get(trackedForm));

  window.addEventListener("beforeunload", (event) => {
    if (!hasUnsavedChanges()) {
      return;
    }
    event.preventDefault();
    event.returnValue = "";
  });
});
