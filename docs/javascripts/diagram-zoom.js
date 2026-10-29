// Diagram expand — every inlined diagram (figure.tl-dia, written by the build
// hook) gets an "Expand" button and opens a copy of its SVG in a full-width
// overlay, so a dense drawing is readable without widening the page column.
// The overlay panel carries the tl-dia class so the SVG keeps its theme styles.

(function () {
  const ICON =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 3h6v6h-2V6.41l-3.29 3.3-1.42-1.42L17.59 5H15V3zM3 15h2v2.59l3.29-3.3 1.42 1.42L6.41 19H9v2H3v-6z"/></svg>';

  function open(figure) {
    const svg = figure.querySelector("svg");
    if (!svg) return;
    const overlay = document.createElement("div");
    overlay.className = "tl-dia-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    const title = svg.querySelector("title");
    if (title) overlay.setAttribute("aria-label", title.textContent);
    const panel = document.createElement("div");
    panel.className = "tl-dia-overlay__panel tl-dia md-typeset";
    const clone = svg.cloneNode(true);
    panel.appendChild(clone);
    const close = document.createElement("button");
    close.type = "button";
    close.className = "tl-dia-overlay__close";
    close.textContent = "Close";
    overlay.appendChild(panel);
    overlay.appendChild(close);
    // Locking the page scroll removes the scrollbar; keep its width as padding
    // so the page behind the overlay does not shift on systems with classic
    // scrollbars.
    const gutter = window.innerWidth - document.documentElement.clientWidth;
    document.body.appendChild(overlay);
    document.documentElement.classList.add("tl-dia-open");
    if (gutter > 0) document.body.style.paddingRight = gutter + "px";
    // The drawing's design width is its viewBox width; its labels are 15px at
    // that size. "Expand" always shows at least that: when the panel is
    // narrower than the drawing (a phone, a portrait tablet) the clone keeps
    // the design width as a minimum and pans, and a line under it says so.
    const box = svg.viewBox && svg.viewBox.baseVal;
    if (box && box.width) {
      const inner = panel.clientWidth - 2 * parseFloat(getComputedStyle(panel).paddingLeft);
      if (inner < box.width) {
        clone.style.minWidth = Math.round(box.width) + "px";
        const hint = document.createElement("p");
        hint.className = "tl-dia-overlay__hint";
        hint.textContent = "Drag sideways to see the whole drawing. Pinch to zoom.";
        overlay.appendChild(hint);
      }
    }
    const previous = document.activeElement;
    function dismiss() {
      overlay.remove();
      document.documentElement.classList.remove("tl-dia-open");
      document.body.style.paddingRight = "";
      document.removeEventListener("keydown", onKey);
      if (previous && previous.focus) previous.focus();
    }
    function onKey(event) {
      if (event.key === "Escape") dismiss();
    }
    overlay.addEventListener("click", function (event) {
      if (!panel.contains(event.target)) dismiss();
    });
    close.addEventListener("click", dismiss);
    document.addEventListener("keydown", onKey);
    close.focus();
  }

  function init() {
    // On a touch screen the inline figure fits the column and is too small to
    // read, so the whole figure opens the overlay; the button stays as the
    // visible affordance and for keyboards.
    const touch = window.matchMedia("(hover: none)").matches;
    document.querySelectorAll("figure.tl-dia").forEach(function (figure) {
      if (figure.querySelector(".tl-dia__expand")) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "tl-dia__expand";
      button.setAttribute("aria-label", "Expand diagram");
      button.innerHTML = ICON + "<span>Expand</span>";
      button.addEventListener("click", function (event) {
        event.stopPropagation();
        open(figure);
      });
      figure.appendChild(button);
      if (touch) {
        figure.classList.add("tl-dia--tap");
        figure.addEventListener("click", function (event) {
          if (event.target.closest("a")) return;
          open(figure);
        });
      }
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
