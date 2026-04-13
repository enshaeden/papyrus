document.addEventListener("DOMContentLoaded", () => {
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
