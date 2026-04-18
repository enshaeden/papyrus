document.addEventListener("DOMContentLoaded", () => {
  const pickers = document.querySelectorAll("[data-citation-picker]");
  if (!pickers.length) return;

  const buildSearchUrl = (baseUrl, query, excludeObjectId) => {
    const url = new URL(baseUrl, window.location.origin);
    url.searchParams.set("query", query);
    if (excludeObjectId) url.searchParams.set("exclude_object_id", excludeObjectId);
    return url.toString();
  };

  pickers.forEach((picker) => {
    const index = picker.dataset.citationIndex;
    const input = picker.querySelector(`#citation_${index}_lookup`);
    const titleField = picker.querySelector(`#citation_${index}_source_title`);
    const typeField = picker.querySelector(`#citation_${index}_source_type`);
    const refField = picker.querySelector(`#citation_${index}_source_ref`);
    const results = picker.querySelector(".citation-picker-results");
    const status = picker.querySelector(".citation-picker-status");
    if (!input || !titleField || !typeField || !refField || !results || !status) return;

    let requestToken = 0;
    let debounceTimer = 0;

    const clearResults = () => {
      results.innerHTML = "";
      results.hidden = true;
    };

    const setStatus = (message) => {
      status.textContent = message;
    };

    const syncStatusToSelection = () => {
      if (titleField.value && refField.value) {
        setStatus(`Selected source: ${titleField.value} -> ${refField.value}`);
        return;
      }
      setStatus("Search guidance by title, tag, or reference code. Selecting a result fills the fields below.");
    };

    const selectResult = (item) => {
      input.value = item.title;
      titleField.value = item.title;
      typeField.value = "document";
      refField.value = item.path;
      setStatus(`Selected source: ${item.title} (${item.object_id}) -> ${item.path}`);
      clearResults();
    };

    const renderResults = (items) => {
      clearResults();
      if (!items.length) {
        setStatus("No matching guidance found. Enter the source manually below if needed.");
        return;
      }
      const fragment = document.createDocumentFragment();
      items.forEach((item) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "citation-picker-result";
        button.addEventListener("click", () => selectResult(item));

        const title = document.createElement("span");
        title.className = "citation-picker-result-title";
        title.textContent = item.title;

        const meta = document.createElement("span");
        meta.className = "citation-picker-result-meta";
        meta.textContent =
          String(item.detail || "").trim() ||
          `${item.object_id} | ${item.path}`;

        button.append(title, meta);
        fragment.append(button);
      });
      results.append(fragment);
      results.hidden = false;
      setStatus("Select an existing guidance item to fill the citation fields.");
    };

    const runSearch = async (query) => {
      const currentToken = ++requestToken;
      setStatus("Searching guidance...");
      try {
        const response = await fetch(
          buildSearchUrl(
            picker.dataset.searchUrl || "/write/citations/search",
            query,
            picker.dataset.excludeObjectId || "",
          ),
          { headers: { Accept: "application/json" } },
        );
        if (!response.ok) throw new Error(`search failed: ${response.status}`);
        const payload = await response.json();
        if (currentToken !== requestToken) return;
        renderResults(Array.isArray(payload.items) ? payload.items : []);
      } catch (_error) {
        clearResults();
        setStatus("Search failed. Enter the source manually below.");
      }
    };

    input.addEventListener("input", () => {
      const query = input.value.trim();
      clearTimeout(debounceTimer);
      if (!query) {
        clearResults();
        syncStatusToSelection();
        return;
      }
      if (query.length < 2) {
        clearResults();
        setStatus("Type at least 2 characters to search guidance.");
        return;
      }
      debounceTimer = window.setTimeout(() => {
        void runSearch(query);
      }, 180);
    });

    input.addEventListener("blur", () => {
      window.setTimeout(() => {
        clearResults();
      }, 180);
    });

    syncStatusToSelection();
  });
});
