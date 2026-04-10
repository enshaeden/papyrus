document.addEventListener("DOMContentLoaded", () => {
  const nextPath = document.querySelector("[data-current-path]");
  const select = document.querySelector("[data-actor-select]");
  const form = select ? select.closest("form") : null;
  if (!nextPath || !select || !form) {
    return;
  }

  const actorCookie = document.cookie
    .split("; ")
    .find((item) => item.startsWith("papyrus_actor="));
  const currentActor = actorCookie ? decodeURIComponent(actorCookie.split("=")[1]) : "local.operator";
  if ([...select.options].some((option) => option.value === currentActor)) {
    select.value = currentActor;
  }

  const trackedForms = [...document.querySelectorAll("form.governed-form")];
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

  const syncNextPath = () => {
    const selected = select.options[select.selectedIndex];
    if (!selected) {
      nextPath.value = window.location.pathname + window.location.search;
      return;
    }
    nextPath.value =
      select.value === currentActor
        ? window.location.pathname + window.location.search
        : (selected.dataset.home || "/");
  };

  syncNextPath();
  select.addEventListener("change", () => {
    syncNextPath();
    if (
      hasUnsavedChanges() &&
      !window.confirm("You have unsaved changes on this page. Switch views and discard them?")
    ) {
      select.value = currentActor;
      syncNextPath();
      return;
    }
    if (typeof form.requestSubmit === "function") {
      form.requestSubmit();
      return;
    }
    form.submit();
  });
});
