# Card illustrations

A feature card on the home page opens with a small drawing from this
directory instead of a generic icon:

```markdown
- {{ locus_glyph pipelines }} **[Pipelines](concepts/multi-agent/composition.md)**
```

The build hook inlines `pipelines.svg` as a one-line `<span class="tl-glyph">`
that themes with the page. The drawings use the diagram vocabulary of the
parent directory at a smaller scale, so the home page and the concept pages
read as one system.

`pipelines.svg` is the reference. Match it.

## Rules

1. `viewBox="0 0 96 56"`, exactly. The glyph is shown at 96 px wide, so it is
   drawn at display size and strokes stay 1.5 px.
2. **No text.** At this size a word is noise; the card title says what the
   drawing means. A `<title>` for the person reading the file is the only text.
3. **No inline styling**, as for the diagrams: classes only.
4. **At most one `.primary` element**, the subject of the card. Every other
   shape is neutral.
5. **Nothing closer than 2 px to the edge**, nothing overlapping, edges that
   do not cross shapes. Seven shapes is the ceiling; four is typical.
6. **The drawing is a claim.** Draw the pattern as the SDK runs it (a swarm is
   a mesh, a handoff is a chain, a graph has a cycle), not a metaphor.

## Vocabulary

| Element | Markup |
| --- | --- |
| Node | `<g class="node"><rect x y width height rx="3"/></g>`, at least 16×10 |
| The subject | `g.node.primary` (also `g.store.primary`) |
| Optional / conditional | `g.node.optional` (dashed border) |
| Terminal | `g.node.end` (inverted) |
| Outcome | `g.node.allow` · `.hold` · `.deny` · `.abstain` |
| Edge | `<path class="edge" marker-end="url(#ah)" d="…"/>`, `.dashed` for conditional, `.allow`/`.hold`/`.deny` for an outcome path |
| Datastore | `<g class="store"><path d="cylinder"/></g>` |
| Decision | `<g class="decision"><polygon points="…"/></g>` |
| Band | `<g class="lane"><rect rx="4"/></g>` behind a group of nodes |
| Process boundary | `<path class="divider" d="M48,4 L48,52"/>` |
| Point | `<circle class="dot" r="1.6"/>` for a stream of events |

One arrowhead marker:

```xml
<defs><marker id="ah" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto" markerUnits="userSpaceOnUse"><path class="arrowhead" d="M0,0 L6,3 L0,6 z"/></marker></defs>
```
