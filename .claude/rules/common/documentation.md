# Documentation Output

## Format

Deliverable documents are **single self-contained HTML files**, not Markdown.
This covers design docs, analysis, reports, handover notes, and anything with a
diagram in it.

**Exception — a repository's canonical docs.** `README`, `CHANGELOG`,
`CONTRIBUTING`, and any `docs/` tree already kept in Markdown follow that
repository's existing convention. Never convert them; a Markdown README is what
the host renders and what contributors expect.

## Self-contained

The file must open correctly from disk with no network:

- Inline all CSS in a `<style>` block. No external stylesheets, no CDN
- No web fonts — use the system font stack
- No external scripts. No Mermaid, D3, or Chart.js pulled from a CDN
- Embed images as `data:` URIs, or don't use them

A document that renders differently offline is broken.

## Diagrams

Diagrams are **inline SVG or HTML/CSS**. Never PNG/JPG, never a screenshot of a
diagram, never an external diagramming service.

| Shape                                    | Build it with        |
| ---------------------------------------- | -------------------- |
| Flow, hierarchy, sequence, state machine | inline SVG           |
| Box-and-arrow, comparison, matrix        | HTML + CSS grid/flex |

Rules:

- Text in a diagram is **real text**, never converted to paths — it must stay
  searchable, selectable, and translatable
- Stroke and fill use `currentColor` or a CSS variable so the diagram follows
  the document theme instead of fighting it
- Every SVG carries a `<title>` as its first child — screen readers announce it
  and it survives being copied into another document
- Label the edges. An unlabeled arrow between two boxes says almost nothing
- **Never let an SVG shrink to fit a narrow screen.** Scaling a 700px diagram into
  390px turns 13px labels into 6px mush. Wrap it in `.diagram-scroll`
  (`overflow-x: auto`) and give the SVG a `min-width` so it scrolls sideways
  instead. Box-and-arrow layouts built in HTML/CSS should reflow to a column
  instead — that is the reason to prefer them for simple shapes

## Theme

Support light and dark through `prefers-color-scheme`. Define colors as CSS
variables on `:root` and override them in the dark block. Diagrams that use
`currentColor` follow along with no extra work.

## Start from the template

- `~/.claude/templates/document.html` — the shell: reset, typography, tables,
  code blocks, theme variables, and the shared arrowhead definition
- `~/.claude/templates/diagram-patterns.html` — copyable SVG and CSS for the
  common diagram shapes

Copy the template, replace the content, delete what you don't use. Don't
hand-roll a new stylesheet per document — that is how five documents end up
looking like five different projects.
