// Program output blocks (```text) on a phone.
//
// The stylesheet wraps output like a terminal does. Two kinds of line read
// badly that way: a banner or rule printed at sixty columns ("=====", "────")
// wraps into a full line and a stub, and a column-aligned block (a report with
// three aligned columns, a piecewise definition) loses its columns. This
// marks rule lines (the stylesheet clips them to one line) and flags blocks
// where two or more lines carry runs of three or more inner spaces as aligned
// (the stylesheet lets those scroll instead). Re-runs on Material's
// instant-navigation page changes.

(function () {
  const RULE = /^([=\-─═_*#~])\1{19,}\s*$/;
  const ALIGNED = /\S {3,}\S/;

  function apply() {
    document.querySelectorAll(".md-typeset .language-text pre > code").forEach(function (code) {
      if (code.dataset.outputScanned) return;
      code.dataset.outputScanned = "1";
      let aligned = 0;
      code.querySelectorAll(':scope > span[id^="__span"]').forEach(function (line) {
        const t = line.textContent.replace(/\n$/, "");
        if (RULE.test(t)) line.classList.add("tl-out-rule");
        if (ALIGNED.test(t)) aligned++;
      });
      if (aligned >= 2) code.classList.add("tl-out-aligned");
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(apply);
  } else {
    document.addEventListener("DOMContentLoaded", apply);
  }
})();
