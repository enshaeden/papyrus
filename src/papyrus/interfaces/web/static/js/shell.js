document.addEventListener("DOMContentLoaded", () => {
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  const shell = document.querySelector(".app-shell");
  const navToggle = document.getElementById("nav-toggle");
  const asideToggle = document.getElementById("aside-toggle");

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
      });
    }

    if (asideToggle) {
      asideToggle.addEventListener("click", () => {
        const isCollapsed = shell.classList.toggle("aside-collapsed");
        localStorage.setItem("aside-collapsed", isCollapsed);
      });
    }
  }

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
