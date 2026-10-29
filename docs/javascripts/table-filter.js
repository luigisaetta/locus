// Table filter — reference pages get a search box that hides table rows as the
// reader types. Two shapes:
//
//   * a catalogue page (front matter `table_filter: true`: the event
//     catalogues, the environment variables) gets ONE box above the first
//     table that filters every table on the page and hides a section whose
//     table has no matching rows left, along with headings that introduce no
//     table at all while a query is active;
//   * any other page with a single large table gets a box above that table.
//
// Hiding uses a class with `display: none !important`, because the `hidden`
// attribute loses to any author `display` rule. Re-runs on instant-navigation
// page changes via Material's `document$`.

(function () {
  const TABLE_MIN_ROWS = 20;
  const HIDDEN = "locus-filter-hidden";

  // Material renders a table as .md-typeset__scrollwrap > .md-typeset__table > table;
  // the outer scroll wrapper is the element that sits among the page's blocks.
  function wrapperOf(table) {
    return table.closest(".md-typeset__scrollwrap") || table.closest(".md-typeset__table") || table;
  }

  function isHeading(el) {
    return /^H[2-4]$/.test(el.tagName);
  }

  function isBoundary(el) {
    return isHeading(el) || el.classList.contains("locus-table-filter") ||
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
    if (prev && isHeading(prev)) block.unshift(prev);
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

  // Heading groups that contain no table (an aside between catalogues) hide
  // while a query is active, so the first visible "result" is never a heading
  // with nothing under it.
  function tablelessGroups(article, owned) {
    const groups = [];
    let group = null;
    for (const el of article.children) {
      if (isHeading(el)) {
        if (group && !group.withTable) groups.push(group.els);
        group = { els: [el], withTable: owned.has(el) };
      } else if (group) {
        group.els.push(el);
        if (owned.has(el) || el.classList.contains("locus-table-filter")) group.withTable = true;
      }
    }
    if (group && !group.withTable) groups.push(group.els);
    return groups;
  }

  function wire(article, tables, anchorBefore, placeholder, pageMode) {
    const ui = makeBox(placeholder);
    anchorBefore.parentNode.insertBefore(ui.box, anchorBefore);
    const rows = [];
    const sections = new Map();
    const owned = new Set();
    for (const table of tables) {
      for (const tr of table.querySelectorAll("tbody tr")) {
        rows.push({ el: tr, table: table, text: tr.textContent.toLowerCase() });
      }
      if (pageMode) {
        const block = sectionOf(table);
        sections.set(table, block);
        for (const el of block) owned.add(el);
      }
    }
    const tableless = pageMode ? tablelessGroups(article, owned) : [];

    function apply() {
      const q = ui.input.value.trim().toLowerCase();
      const alive = new Set();
      let shown = 0;
      for (const row of rows) {
        const match = !q || row.text.indexOf(q) !== -1;
        row.el.classList.toggle(HIDDEN, !match);
        if (match) {
          shown += 1;
          alive.add(row.table);
        }
      }
      if (pageMode) {
        for (const [table, block] of sections) {
          const show = !q || alive.has(table);
          for (const el of block) el.classList.toggle(HIDDEN, !show);
        }
        for (const els of tableless) for (const el of els) el.classList.toggle(HIDDEN, Boolean(q));
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
    // A catalogue page opts in with `table_filter: true` in its front matter
    // (overrides/main.html turns that into this meta tag).
    const pageMode = document.querySelector('meta[name="locus:table-filter"][content="page"]');
    if (pageMode && tables.length > 1) {
      wire(article, tables, sectionOf(tables[0])[0], "Filter " + total + " rows across " + tables.length + " tables…", true);
      return;
    }
    for (const table of tables) {
      const n = table.querySelectorAll("tbody tr").length;
      if (n >= TABLE_MIN_ROWS) wire(article, [table], wrapperOf(table), "Filter " + n + " rows…", false);
    }
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
