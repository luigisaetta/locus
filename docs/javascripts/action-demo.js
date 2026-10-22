/* Copyright (c) 2025, 2026 Oracle and/or its affiliates.
   Licensed under the Universal Permissive License v1.0 as shown at
   https://oss.oracle.com/licenses/upl/ */
(function () {
  const scenarios = {
    staging: {
      status: "✓ Allowed", tone: "allow",
      summary: "The staging rollout passes policy and the simulated deploy function runs.",
      evidence: "CI passed · image checkout-api:1.8.2 · staging", decision: "allow",
      audit: "deploy checkout-api · allow · policy checks passed", line: "blast"
    },
    production: {
      status: "… Held for approval", tone: "hold",
      summary: "The production label triggers a human hold. No deploy function runs.",
      evidence: "CI passed · image checkout-api:1.8.2 · production", decision: "require_human",
      audit: "deploy checkout-api · hold (require_human) · production policy", line: "human"
    },
    prohibited: {
      status: "× Denied", tone: "deny",
      summary: "The prohibited label triggers a hard denial. Approval cannot override it.",
      evidence: "CI passed · action tagged prohibited", decision: "deny",
      audit: "deploy checkout-api · deny · label denied by policy", line: "deny"
    },
    unsupported: {
      status: "↺ Abstained", tone: "abstain",
      summary: "The unsupported causal claim scores below the GSAR threshold, so no deploy is proposed.",
      evidence: "Claim: database saturation · evidence refs: none", decision: "replan",
      audit: "grounding decision · replan · unsupported claim", line: "ground"
    }
  };

  function mount(root) {
    const buttons = root.querySelectorAll("[data-demo-scenario]");
    if (!buttons.length) return;
    const fields = {
      status: root.querySelector("[data-demo-status]"), summary: root.querySelector("[data-demo-summary]"),
      evidence: root.querySelector("[data-demo-evidence]"), decision: root.querySelector("[data-demo-decision]"),
      audit: root.querySelector("[data-demo-audit]")
    };
    const tablist = root.querySelector('[role="tablist"]');
    const panel = root.querySelector('[role="tabpanel"]');
    function select(name) {
      const scenario = scenarios[name];
      if (!scenario) return;
      buttons.forEach((button) => {
        const selected = button.dataset.demoScenario === name;
        button.setAttribute("aria-selected", String(selected));
        button.tabIndex = selected ? 0 : -1;
        if (selected && panel && button.id) panel.setAttribute("aria-labelledby", button.id);
      });
      Object.entries(fields).forEach(([key, node]) => { if (node) node.textContent = scenario[key]; });
      fields.status.className = "action-demo__status action-demo__status--" + scenario.tone;
      root.querySelectorAll("[data-code-line]").forEach((line) => {
        line.classList.toggle("is-active", line.dataset.codeLine === scenario.line);
      });
    }
    buttons.forEach((button) => button.addEventListener("click", () => select(button.dataset.demoScenario)));
    if (tablist) tablist.addEventListener("keydown", (event) => {
      const list = Array.from(buttons);
      const current = list.indexOf(event.target);
      if (current < 0) return;
      let next;
      if (event.key === "ArrowRight") next = (current + 1) % list.length;
      else if (event.key === "ArrowLeft") next = (current - 1 + list.length) % list.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = list.length - 1;
      else return;
      event.preventDefault();
      select(list[next].dataset.demoScenario);
      list[next].focus();
    });
    select("staging");
  }

  function init() { document.querySelectorAll("[data-action-demo]").forEach(mount); }
  if (typeof document$ !== "undefined") document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);
})();
