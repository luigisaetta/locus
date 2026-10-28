// Table filter — reference pages get a search box that hides table rows as the
// reader types. Two shapes, chosen from the page itself with no markup:
//
//   * a catalogue page (several tables adding up to many rows: the event
//     catalogues, the environment variables) gets ONE box above the first
//     table that filters every table on the page and hides a section whose
//     table has no matching rows left;
//   * a page with a single large table gets a box above that table.
//
// Re-runs on instant-navigation page changes via Material's `document$`.

(function () {
  const PAGE_MIN_TABLES = 4;
  const PAGE_MIN_ROWS = 40;
  const TABLE_MIN_ROWS = 15;

  // Material renders a table as .md-typeset__scrollwrap > .md-typeset__table > table;
  // the outer scroll wrapper is the element that sits among the page's blocks.
  function wrapperOf(table) {
    return table.closest(".md-typeset__scrollwrap") || table.closest(".md-typeset__table") || table;
  }

  function isBoundary(el) {
    return /^H[2-4]$/.test(el.tagName) || el.classList.contains("locus-table-filter") ||
      el.classList.contains("md-typeset__scrollwrap") || el.tagName === "TABLE";
  }

  // The heading that introduces a table, everything between the two, and the
  // notes that follow the table up to the next heading or table.
  function sectionOf(table) {
    const wrapper = wrapperOf(table);
    const block = [wrapper];
    let prev = wrapper.previousElementSibling;
    while (prev && !isBoundary(prev)) {
      block.unshift(prev);
      prev = prev.previousElementSibling;
    }
    if (prev && /^H[2-4]$/.test(prev.tagName)) block.unshift(prev);
    let next = wrapper.nextElementSibling;
    while (next && !isBoundary(next)) {
      block.push(next);
      next = next.nextElementSibling;
    }
    return block;
  }

  function makeBox(placeholder) {
    const box = document.createElement("div");
    box.className = "locus-table-filter";
    const input = document.createElement("input");
    input.type = "search";
    input.className = "locus-table-filter__input";
    input.setAttribute("aria-label", "Filter the tables on this page");
    input.setAttribute("autocomplete", "off");
    input.setAttribute("spellcheck", "false");
    input.placeholder = placeholder;
    const count = document.createElement("span");
    count.className = "locus-table-filter__count";
    count.setAttribute("aria-live", "polite");
    box.appendChild(input);
    box.appendChild(count);
    return { box: box, input: input, count: count };
  }

  function wire(tables, anchorBefore, placeholder, hideSections) {
    const ui = makeBox(placeholder);
    anchorBefore.parentNode.insertBefore(ui.box, anchorBefore);
    const rows = [];
    const sections = new Map();
    for (const table of tables) {
      for (const tr of table.querySelectorAll("tbody tr")) {
        rows.push({ el: tr, table: table, text: tr.textContent.toLowerCase() });
      }
      if (hideSections) sections.set(table, sectionOf(table));
    }
    function apply() {
      const q = ui.input.value.trim().toLowerCase();
      const alive = new Set();
      let shown = 0;
      for (const row of rows) {
        const match = !q || row.text.indexOf(q) !== -1;
        row.el.hidden = !match;
        if (match) {
          shown += 1;
          alive.add(row.table);
        }
      }
      if (hideSections) {
        for (const [table, block] of sections) {
          const show = !q || alive.has(table);
          for (const el of block) el.hidden = !show;
        }
      }
      ui.count.textContent = q ? shown + " of " + rows.length : "";
    }
    ui.input.addEventListener("input", apply);
    ui.input.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        ui.input.value = "";
        apply();
      }
    });
  }

  function init() {
    // The Examples index has its own filter for its lists.
    if (document.querySelector("#notebook-filter-input")) return;
    const article = document.querySelector("article.md-content__inner");
    if (!article || article.querySelector(".locus-table-filter")) return;
    const tables = Array.from(article.querySelectorAll("table"));
    if (!tables.length) return;
    const total = tables.reduce(function (n, t) {
      return n + t.querySelectorAll("tbody tr").length;
    }, 0);
    if (tables.length >= PAGE_MIN_TABLES && total >= PAGE_MIN_ROWS) {
      const first = sectionOf(tables[0])[0];
      wire(tables, first, "Filter " + total + " rows across " + tables.length + " tables…", true);
      return;
    }
    for (const table of tables) {
      const n = table.querySelectorAll("tbody tr").length;
      if (n >= TABLE_MIN_ROWS) wire([table], wrapperOf(table), "Filter " + n + " rows…", false);
    }
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
