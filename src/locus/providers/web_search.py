# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Web-search provider protocol + concrete implementations.

The protocol is deliberately minimal: ``async search(query, max_results)``
returns a list of :class:`SearchResult`. Implementations live behind
optional dependencies so locus stays a small core.

Built-in implementations
------------------------

- :class:`OpenAISearchPreviewProvider` — uses one of OpenAI's search
  models (``gpt-5-search-api``). The model performs the search itself and
  cites its sources as ``url_citation`` annotations; we turn those into
  ``SearchResult`` objects. Requires the ``openai`` extra.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from locus.providers.types import SearchResult


if TYPE_CHECKING:
    from locus.models.native.openai import OpenAIModel


@runtime_checkable
class BaseWebSearchProvider(Protocol):
    """Protocol every web-search provider must implement."""

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]:
        """Return ``max_results`` (or fewer) search hits for ``query``."""
        ...


class OpenAISearchPreviewProvider:
    """Web search via an OpenAI search model such as ``gpt-5-search-api``.

    The search model runs the query itself and cites its sources as
    ``url_citation`` annotations on the reply; those citations are the
    results. A model (or test double) that returns no annotations gets a
    second, prompt-based request asking for the hits as JSON. The shape is
    spelled out in the prompt because the search models reject
    ``response_format`` (``json_schema`` fails with a 500, ``json_object``
    with a 400). The name predates the retirement of the
    ``gpt-4o-*-search-preview`` models it was built for.

    Args:
        model: An :class:`OpenAIModel` instance. The caller picks the
            search-capable model id (e.g. ``"gpt-5-search-api"``).
        max_chars_per_snippet: Cap each snippet to this length so the
            agent context doesn't blow up.
    """

    def __init__(
        self,
        model: OpenAIModel,
        *,
        max_chars_per_snippet: int = 500,
    ) -> None:
        self._model = model
        self._cap = max_chars_per_snippet

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]:
        hits = await self._search_via_citations(query, max_results)
        if hits:
            return hits
        return await self._search_via_prompt(query, max_results)

    async def _search_via_citations(self, query: str, max_results: int) -> list[SearchResult]:
        """Return the ``url_citation`` annotations of a bare-query reply.

        Yields ``[]`` when the model object has no awaitable client (a stub)
        or the reply carries no citations, so the caller can fall back.
        """
        import inspect  # noqa: PLC0415

        client = getattr(self._model, "client", None)
        completions = getattr(getattr(client, "chat", None), "completions", None)
        create = getattr(completions, "create", None)
        if create is None:
            return []
        pending = create(
            model=self._model.config.model,
            messages=[{"role": "user", "content": query}],
        )
        if not inspect.isawaitable(pending):
            return []
        completion = await pending
        message = completion.choices[0].message
        text = message.content or ""
        out: list[SearchResult] = []
        seen: set[str] = set()
        for annotation in getattr(message, "annotations", None) or []:
            citation = getattr(annotation, "url_citation", None)
            url = getattr(citation, "url", None)
            if not url or url in seen:
                continue
            seen.add(url)
            start = getattr(citation, "start_index", None)
            end = getattr(citation, "end_index", None)
            snippet = text[start:end] if isinstance(start, int) and isinstance(end, int) else ""
            out.append(
                SearchResult(
                    title=getattr(citation, "title", "") or url,
                    url=url,
                    snippet=snippet[: self._cap],
                )
            )
            if len(out) >= max_results:
                break
        return out

    async def _search_via_prompt(self, query: str, max_results: int) -> list[SearchResult]:
        """Ask for the hits as a JSON object named in the prompt and parse leniently."""
        # Importing here keeps the file lazy on the openai dep at
        # module-load time — locus core stays import-free of openai.
        from pydantic import BaseModel, ConfigDict  # noqa: PLC0415

        from locus.core.messages import Message  # noqa: PLC0415
        from locus.core.structured import parse_structured  # noqa: PLC0415

        class _Hit(BaseModel):
            model_config = ConfigDict(extra="forbid")
            title: str
            url: str
            snippet: str

        class _Hits(BaseModel):
            model_config = ConfigDict(extra="forbid")
            results: list[_Hit]

        messages = [
            Message.system(
                "You are a web search engine. For the user's query, return "
                f"the top {max_results} results as one JSON object of the form "
                '{"results": [{"title": "...", "url": "https://...", '
                '"snippet": "..."}]}. Every url must be a real, absolute URL; '
                f"snippets are at most {self._cap} characters. Reply with the "
                "JSON object only: no prose before or after it, no markdown."
            ),
            Message.user(query),
        ]
        # No ``response_format`` on purpose: the search models reject it (see
        # the class docstring), so the JSON contract lives in the prompt.
        response = await self._model.complete(messages=messages, tools=None)
        content = response.message.content or "{}"
        # ``strict=False`` already digs the object out of surrounding prose or
        # a markdown fence, so an unparseable reply simply means no results.
        parsed = parse_structured(content, _Hits, strict=False)
        if not parsed.success or parsed.parsed is None:
            return []
        typed: _Hits = parsed.parsed  # type: ignore[assignment]
        return [
            SearchResult(title=h.title, url=h.url, snippet=(h.snippet or "")[: self._cap])
            for h in typed.results[:max_results]
        ]


__all__: list[str] = ["BaseWebSearchProvider", "OpenAISearchPreviewProvider"]


# Type-only re-export marker so IDEs surface the protocol on hover.
_: Any = BaseWebSearchProvider
