document.addEventListener("DOMContentLoaded", () => {
  const inputs = document.querySelectorAll("[data-filter-input='true']");
  for (const input of inputs) {
    input.addEventListener("input", () => {
      const table = document.querySelector("[data-filter-table='true'] table");
      if (!table) return;
      const query = input.value.trim().toLowerCase();
      for (const row of table.querySelectorAll("tbody tr")) {
        row.hidden = query !== "" && !row.textContent.toLowerCase().includes(query);
      }
    });
  }
});
