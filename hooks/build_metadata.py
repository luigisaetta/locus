# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""Build documentation facts from the SDK used for this exact build.

The deploy workflow installs a tagged SDK checkout before MkDocs runs. Reading
the imported SDK and provider registry here means an older docs build
cannot accidentally display a newer PyPI release, and provider tables cannot
drift from the routes the SDK actually registers.
"""

from __future__ import annotations

import os
import re
from importlib import import_module
from pathlib import Path
from typing import Any


SDK_VERSION_TOKEN = "{{ locus_sdk_version }}"  # noqa: S105 — template placeholder, not a secret
PROVIDER_TABLE_TOKEN = "{{ locus_provider_table }}"  # noqa: S105 — template placeholder, not a secret
EXAMPLE_MODEL_TOKEN = "{{ locus_example_model }}"  # noqa: S105 — template placeholder, not a secret
EVENT_COUNT_TOKEN = "{{ locus_event_count }}"  # noqa: S105 — template placeholder, not a secret
EVENT_PREFIXES_TOKEN = "{{ locus_event_prefixes }}"  # noqa: S105 — template placeholder, not a secret

_SDK_REPO = "https://github.com/oracle/locus/"
#: A link into the SDK repo on its moving ``main`` branch.
_SDK_MAIN_LINK = re.compile(r"https://github\.com/oracle/locus/(blob|tree)/main/([^)\s\"'#>]+)")
#: Only a plain release has a tag to pin to; a dev or local build does not.
_RELEASE = re.compile(r"^\d+\.\d+\.\d+$")

#: ``{{ locus_diagram agent-loop }}`` inlines docs/diagrams/agent-loop.svg.
_DIAGRAM_TOKEN = re.compile(r"\{\{\s*locus_diagram\s+([a-z0-9][a-z0-9-]*)\s*\}\}")
_XML_PROLOG = re.compile(r"<\?xml[^>]*\?>\s*")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_ID_ATTR = re.compile(r'\bid="([^"]+)"')


def _sdk_version() -> str:
    try:
        sdk = import_module("locus")
    except ModuleNotFoundError as exc:  # pragma: no cover - build misconfiguration
        raise RuntimeError(
            "Install the Locus SDK used for this documentation build before running MkDocs"
        ) from exc
    return str(sdk.__version__)


def _provider_table() -> str:
    providers = import_module("locus.models.providers")
    return str(providers.provider_table())


def _events() -> list[str]:
    """Every canonical event name the SDK declares, from its ``EV_*`` constants."""
    emit = import_module("locus.observability.emit")
    return sorted(
        value
        for name, value in vars(emit).items()
        if name.startswith("EV_") and isinstance(value, str)
    )


def _event_count(events: list[str]) -> str:
    """Rounded down to the ten, so "60+" stays true as events are added."""
    return f"{len(events) // 10 * 10}+"


def _event_prefixes(events: list[str]) -> str:
    return ", ".join(f"`{prefix}.*`" for prefix in sorted({e.split(".")[0] for e in events}))


def _sdk_checkout(config: Any) -> Path | None:
    """The SDK repository this build installed, when one is on disk.

    The docs live in the SDK repository, so the checkout is the repository
    root (``mkdocs.yml``'s directory). ``LOCUS_SDK_DIR`` still overrides it,
    and a ``.sdk`` sub-checkout is honoured for builds against a pinned tag.
    """
    candidates = []
    if os.environ.get("LOCUS_SDK_DIR"):
        candidates.append(Path(os.environ["LOCUS_SDK_DIR"]))
    if config.get("config_file_path"):
        root = Path(config["config_file_path"]).parent
        candidates.append(root / ".sdk")
        if (root / "pyproject.toml").is_file():
            candidates.append(root)
    return next((c for c in candidates if c.is_dir()), None)


def pin_sdk_links(markdown: str, version: str, checkout: Path | None) -> str:
    """Point SDK source links at the release this site documents.

    A ``blob/main`` link shows whatever the SDK's main branch holds today, which
    drifts from the documented release, and its ``#L`` line anchors break the
    first time the file changes. A tag never moves. A path that does not exist
    at the release (added to main after it) is left on main rather than turned
    into a 404.
    """
    if not _RELEASE.match(version):
        return markdown

    def pin(match: re.Match[str]) -> str:
        kind, path = match.group(1), match.group(2)
        if checkout is not None and not (checkout / path).exists():
            return match.group(0)
        return f"{_SDK_REPO}{kind}/v{version}/{path}"

    return _SDK_MAIN_LINK.sub(pin, markdown)


def render_diagram(name: str, docs_dir: Path) -> str:
    """Inline one diagram so it themes with the page.

    Diagrams live as SVG under docs/diagrams and style themselves with the
    ``.tl-dia`` classes in locus.css, which read the --tl-* tokens. Inlined,
    they follow the light/dark toggle; as an <img> they could not see it.
    Every id is prefixed with the diagram name so two diagrams on one page
    cannot collide on a marker or a <title>.
    """
    path = docs_dir / "diagrams" / f"{name}.svg"
    if not path.is_file():
        raise RuntimeError(f"{{{{ locus_diagram {name} }}}} names {path}, which does not exist")
    svg = _COMMENT.sub("", _XML_PROLOG.sub("", path.read_text()))
    ids = set(_ID_ATTR.findall(svg))
    for old in sorted(ids, key=len, reverse=True):
        new = f"{name}--{old}"
        svg = re.sub(rf'\bid="{re.escape(old)}"', f'id="{new}"', svg)
        svg = svg.replace(f"url(#{old})", f"url(#{new})").replace(
            f'href="#{old}"', f'href="#{new}"'
        )
        svg = re.sub(
            r'(aria-(?:labelledby|describedby)="[^"]*)\b' + re.escape(old) + r"\b",
            lambda m: m.group(1) + new,
            svg,
        )
    # Blank lines would end the raw-HTML block early and hand the rest to Markdown.
    body = "\n".join(line for line in svg.strip().splitlines() if line.strip())
    return f'\n<figure class="tl-dia">\n{body}\n</figure>\n'


def on_config(config: Any) -> Any:
    extra = dict(config.get("extra", {}))
    extra["sdk_version"] = _sdk_version()
    checkout = _sdk_checkout(config)
    extra["sdk_checkout"] = str(checkout) if checkout else None
    config["extra"] = extra
    return config


def on_page_markdown(markdown: str, *, config: Any, **_: Any) -> str:
    """Expand build facts only where their explicit tokens appear."""
    extra = config["extra"]
    sdk_version = extra["sdk_version"]
    rendered = markdown.replace(SDK_VERSION_TOKEN, sdk_version)
    if PROVIDER_TABLE_TOKEN in rendered:
        rendered = rendered.replace(PROVIDER_TABLE_TOKEN, _provider_table())
    if EXAMPLE_MODEL_TOKEN in rendered:
        if not extra.get("example_model"):
            raise RuntimeError(
                "A page uses {{ locus_example_model }} but mkdocs.yml sets no extra.example_model"
            )
        rendered = rendered.replace(EXAMPLE_MODEL_TOKEN, extra["example_model"])
    if EVENT_COUNT_TOKEN in rendered or EVENT_PREFIXES_TOKEN in rendered:
        events = _events()
        rendered = rendered.replace(EVENT_COUNT_TOKEN, _event_count(events))
        rendered = rendered.replace(EVENT_PREFIXES_TOKEN, _event_prefixes(events))
    if "locus_diagram" in rendered:
        docs_dir = Path(config["docs_dir"])
        rendered = _DIAGRAM_TOKEN.sub(lambda m: render_diagram(m.group(1), docs_dir), rendered)
    checkout = extra.get("sdk_checkout")
    return pin_sdk_links(rendered, sdk_version, Path(checkout) if checkout else None)
