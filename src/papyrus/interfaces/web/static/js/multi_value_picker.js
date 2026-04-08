document.addEventListener("DOMContentLoaded", () => {
  const pickers = document.querySelectorAll("[data-multi-value-picker]");
  if (!pickers.length) return;

  const parseLines = (value) =>
    value
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);

  const normalizeItem = (item) => {
    const value = String((item && item.value) || "").trim();
    if (!value) return null;
    return {
      value,
      label: String((item && item.label) || value).trim() || value,
      detail: String((item && item.detail) || "").trim(),
    };
  };

  const matchesQuery = (item, query) => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) return true;
    return [item.value, item.label, item.detail]
      .filter(Boolean)
      .some((candidate) => candidate.toLowerCase().includes(normalizedQuery));
  };

  const buildSearchUrl = (baseUrl, query, excludeObjectId) => {
    const url = new URL(baseUrl, window.location.origin);
    url.searchParams.set("query", query);
    if (excludeObjectId) url.searchParams.set("exclude_object_id", excludeObjectId);
    return url.toString();
  };

  pickers.forEach((picker) => {
    const input = picker.querySelector(".multi-value-picker-input");
    const selected = picker.querySelector(".multi-value-picker-selected");
    const results = picker.querySelector(".multi-value-picker-results");
    const storage = picker.querySelector(".multi-value-picker-storage");
    const status = picker.querySelector(".multi-value-picker-status");
    if (!input || !selected || !results || !storage || !status) return;

    const staticOptions = JSON.parse(picker.dataset.staticOptions || "[]")
      .map(normalizeItem)
      .filter(Boolean);
    const searchUrl = picker.dataset.searchUrl || "";
    const excludeObjectId = picker.dataset.excludeObjectId || "";
    const emptyLabel = picker.dataset.emptyLabel || "No values selected yet.";
    let selectedItems = [];
    let requestToken = 0;
    let debounceTimer = 0;

    const syncFromStorage = () => {
      const selectedValues = parseLines(storage.value);
      selectedItems = selectedValues.map((value) => {
        return (
          staticOptions.find((item) => item.value === value) || {
            value,
            label: value,
            detail: "",
          }
        );
      });
    };

    const syncStorage = () => {
      storage.value = selectedItems.map((item) => item.value).join("\n");
    };

    const setStatus = (message) => {
      status.textContent = message;
    };

    const clearResults = () => {
      results.innerHTML = "";
      results.hidden = true;
    };

    const renderSelected = () => {
      selected.innerHTML = "";
      if (!selectedItems.length) {
        const empty = document.createElement("p");
        empty.className = "multi-value-picker-empty";
        empty.textContent = emptyLabel;
        selected.append(empty);
      } else {
        selectedItems.forEach((item) => {
          const chip = document.createElement("span");
          chip.className = "multi-value-chip";

          const copy = document.createElement("span");
          copy.className = "multi-value-chip-copy";
          copy.textContent = item.label;
          chip.append(copy);

          if (item.detail) {
            const meta = document.createElement("span");
            meta.className = "multi-value-chip-meta";
            meta.textContent = item.detail;
            chip.append(meta);
          }

          const remove = document.createElement("button");
          remove.type = "button";
          remove.className = "multi-value-chip-remove";
          remove.textContent = "Remove";
          remove.addEventListener("click", () => {
            selectedItems = selectedItems.filter((selectedItem) => selectedItem.value !== item.value);
            syncStorage();
            renderSelected();
            if (staticOptions.length) renderStaticResults(input.value);
          });
          chip.append(remove);

          selected.append(chip);
        });
      }

      const count = selectedItems.length;
      setStatus(
        count
          ? `${count} selected. Search again to add more items or use manual entry below.`
          : emptyLabel,
      );
    };

    const addItem = (item) => {
      if (selectedItems.some((selectedItem) => selectedItem.value === item.value)) return;
      selectedItems = [...selectedItems, item];
      syncStorage();
      renderSelected();
      input.value = "";
      clearResults();
    };

    const renderResults = (items) => {
      clearResults();
      if (!items.length) {
        setStatus("No matching values. Use manual entry below if needed.");
        return;
      }

      const fragment = document.createDocumentFragment();
      items.forEach((item) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "multi-value-picker-result";
        button.addEventListener("click", () => addItem(item));

        const title = document.createElement("span");
        title.className = "multi-value-picker-result-title";
        title.textContent = item.label;
        button.append(title);

        const metaText = item.detail || item.value;
        if (metaText) {
          const meta = document.createElement("span");
          meta.className = "multi-value-picker-result-meta";
          meta.textContent = metaText;
          button.append(meta);
        }

        fragment.append(button);
      });
      results.append(fragment);
      results.hidden = false;
      setStatus("Select one or more values to populate the field automatically.");
    };

    const renderStaticResults = (query) => {
      const nextItems = staticOptions
        .filter((item) => !selectedItems.some((selectedItem) => selectedItem.value === item.value))
        .filter((item) => matchesQuery(item, query))
        .slice(0, 10);
      renderResults(nextItems);
    };

    const runRemoteSearch = async (query) => {
      const currentToken = ++requestToken;
      setStatus("Searching existing knowledge objects...");
      try {
        const response = await fetch(
          buildSearchUrl(searchUrl, query, excludeObjectId),
          { headers: { Accept: "application/json" } },
        );
        if (!response.ok) throw new Error(`search failed: ${response.status}`);
        const payload = await response.json();
        if (currentToken !== requestToken) return;
        const nextItems = (Array.isArray(payload.items) ? payload.items : [])
          .map(normalizeItem)
          .filter(Boolean)
          .filter((item) => !selectedItems.some((selectedItem) => selectedItem.value === item.value));
        renderResults(nextItems);
      } catch (_error) {
        clearResults();
        setStatus("Search failed. Use manual entry below if needed.");
      }
    };

    input.addEventListener("focus", () => {
      if (staticOptions.length) {
        renderStaticResults(input.value);
      } else if (!input.value.trim()) {
        setStatus("Type at least 2 characters to search existing knowledge objects.");
      }
    });

    input.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      const query = input.value.trim();
      if (staticOptions.length) {
        renderStaticResults(query);
        return;
      }
      if (!query) {
        clearResults();
        renderSelected();
        return;
      }
      if (query.length < 2) {
        clearResults();
        setStatus("Type at least 2 characters to search existing knowledge objects.");
        return;
      }
      debounceTimer = window.setTimeout(() => {
        void runRemoteSearch(query);
      }, 180);
    });

    input.addEventListener("blur", () => {
      window.setTimeout(() => {
        clearResults();
      }, 180);
    });

    storage.addEventListener("input", () => {
      syncFromStorage();
      renderSelected();
    });

    syncFromStorage();
    renderSelected();
  });
});
