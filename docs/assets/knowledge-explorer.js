(function () {
  function parseJson(id) {
    var node = document.getElementById(id);
    if (!node) {
      return null;
    }
    try {
      return JSON.parse(node.textContent || "null");
    } catch (_error) {
      return null;
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function buildOptions(values, currentValue, includeNoneOption) {
    var options = ['<option value="">Any</option>'];
    if (includeNoneOption) {
      options.push('<option value="__none__"' + (currentValue === "__none__" ? " selected" : "") + ">Unclassified</option>");
    }
    values.forEach(function (value) {
      var selected = currentValue === value ? " selected" : "";
      options.push('<option value="' + escapeHtml(value) + '"' + selected + ">" + escapeHtml(value) + "</option>");
    });
    return options.join("");
  }

  function articleMatches(article, state, defaultStatuses) {
    if (state.query) {
      var haystack = [
        article.title,
        article.summary,
        article.path,
        article.type,
        article.status,
        article.owner,
        article.team,
        article.audience,
        article.services.join(" "),
        article.systems.join(" "),
        article.tags.join(" "),
      ]
        .join(" ")
        .toLowerCase();
      if (haystack.indexOf(state.query.toLowerCase()) === -1) {
        return false;
      }
    }

    if (state.type && article.type !== state.type) {
      return false;
    }
    if (state.audience && article.audience !== state.audience) {
      return false;
    }
    if (state.team && article.team !== state.team) {
      return false;
    }
    if (state.owner && article.owner !== state.owner) {
      if (state.owner === "__none__") {
        if (String(article.owner || "").trim() !== "") {
          return false;
        }
      } else if (article.owner !== state.owner) {
        return false;
      }
    }
    if (state.status) {
      if (article.status !== state.status) {
        return false;
      }
    } else if (defaultStatuses.length && defaultStatuses.indexOf(article.status) === -1) {
      return false;
    }

    if (state.service) {
      if (state.service === "__none__") {
        if (article.services.length !== 0) {
          return false;
        }
      } else if (article.services.indexOf(state.service) === -1) {
        return false;
      }
    }

    if (state.system) {
      if (state.system === "__none__") {
        if (article.systems.length !== 0) {
          return false;
        }
      } else if (article.systems.indexOf(state.system) === -1) {
        return false;
      }
    }

    if (state.tag) {
      if (state.tag === "__none__") {
        if (article.tags.length !== 0) {
          return false;
        }
      } else if (article.tags.indexOf(state.tag) === -1) {
        return false;
      }
    }

    return true;
  }

  function renderCard(article) {
    var chips = [
      article.type,
      article.status,
      article.audience,
      article.team,
    ]
      .concat(article.services)
      .concat(article.tags)
      .map(function (value) {
        return '<span class="kb-chip">' + escapeHtml(value) + "</span>";
      })
      .join("");

    return (
      '<article class="kb-result-card">' +
      '<h3><a href="' + escapeHtml(article.site_path) + '">' + escapeHtml(article.title) + "</a></h3>" +
      "<p>" + escapeHtml(article.summary) + "</p>" +
      '<div class="kb-result-meta">' + chips + "</div>" +
      '<p class="kb-result-path">' + escapeHtml(article.path) + "</p>" +
      "<p>Owner: " + escapeHtml(article.owner) + " | Last reviewed: " + escapeHtml(article.last_reviewed) + "</p>" +
      "</article>"
    );
  }

  function initExplorer() {
    var explorer = document.getElementById("kb-explorer");
    if (!explorer) {
      return;
    }

    var data = parseJson("kb-explorer-data");
    var taxonomies = parseJson("kb-explorer-taxonomies");
    if (!data || !taxonomies) {
      return;
    }

    var controls = document.getElementById("kb-explorer-controls");
    var summary = document.getElementById("kb-explorer-summary");
    var resultsNode = document.getElementById("kb-explorer-results");
    var params = new URLSearchParams(window.location.search);
    var state = {
      query: params.get("query") || "",
      type: params.get("type") || "",
      audience: params.get("audience") || "",
      service: params.get("service") || "",
      system: params.get("system") || "",
      tag: params.get("tag") || "",
      status: params.get("status") || "",
      team: params.get("team") || "",
      owner: params.get("owner") || "",
    };

    function writeStateToUrl() {
      var next = new URLSearchParams();
      Object.keys(state).forEach(function (key) {
        if (state[key]) {
          next.set(key, state[key]);
        }
      });
      var nextQuery = next.toString();
      var nextUrl = window.location.pathname + (nextQuery ? "?" + nextQuery : "");
      window.history.replaceState({}, "", nextUrl);
    }

    function render() {
      controls.innerHTML =
        '<label><span>Search</span><input data-field="query" type="search" value="' + escapeHtml(state.query) + '" placeholder="title, summary, path, tag" /></label>' +
        '<label><span>Type</span><select data-field="type">' + buildOptions(taxonomies.type, state.type, false) + "</select></label>" +
        '<label><span>Audience</span><select data-field="audience">' + buildOptions(taxonomies.audience, state.audience, false) + "</select></label>" +
        '<label><span>Service</span><select data-field="service">' + buildOptions(taxonomies.service, state.service, true) + "</select></label>" +
        '<label><span>System</span><select data-field="system">' + buildOptions(taxonomies.system, state.system, true) + "</select></label>" +
        '<label><span>Tag</span><select data-field="tag">' + buildOptions(taxonomies.tag, state.tag, true) + "</select></label>" +
        '<label><span>Status</span><select data-field="status">' + buildOptions(taxonomies.status, state.status, false) + "</select></label>" +
        '<label><span>Team</span><select data-field="team">' + buildOptions(taxonomies.team, state.team, false) + "</select></label>" +
        '<label><span>Owner</span><select data-field="owner">' + buildOptions(taxonomies.owner, state.owner, true) + "</select></label>" +
        '<button type="button" id="kb-clear-filters">Clear Filters</button>';

      var filtered = data.filter(function (article) {
        return articleMatches(article, state, taxonomies.default_statuses || []);
      });

      summary.textContent =
        "Showing " +
        filtered.length +
        " article(s) out of " +
        data.length +
        (state.status ? "" : " across default current statuses: " + (taxonomies.default_statuses || []).join(", "));

      resultsNode.innerHTML = filtered.length
        ? filtered.map(renderCard).join("")
        : '<article class="kb-result-card"><p>No articles matched the current filters.</p></article>';

      Array.prototype.forEach.call(controls.querySelectorAll("[data-field]"), function (node) {
        node.addEventListener("input", function (event) {
          state[event.target.getAttribute("data-field")] = event.target.value;
          writeStateToUrl();
          render();
        });
        node.addEventListener("change", function (event) {
          state[event.target.getAttribute("data-field")] = event.target.value;
          writeStateToUrl();
          render();
        });
      });

      var clearButton = document.getElementById("kb-clear-filters");
      if (clearButton) {
        clearButton.addEventListener("click", function () {
          Object.keys(state).forEach(function (key) {
            state[key] = "";
          });
          writeStateToUrl();
          render();
        });
      }
    }

    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initExplorer);
  } else {
    initExplorer();
  }
})();
