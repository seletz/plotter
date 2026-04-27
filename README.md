# plotter

Code, generators, and the public **logbook** for designs I make on my **iDraw H A1**
pen plotter.

The logbook itself is the point — see the live site:
**https://seletz.github.io/plotter/**

## Repo layout

```
.
├── docs/                # Logbook source (markdown). Built by zensical.
│   ├── index.md         # Landing page
│   ├── about.md         # About / authoring rules
│   └── designs/         # One markdown file per design
├── templates/
│   └── design.md        # Per-design page template (4 headings)
├── cuboid/              # Generator for the "cuboid" design
├── calibrate/           # Plotter calibration tooling
├── zensical.toml        # Site config
├── mise.toml            # Task runner / tool versions
└── .github/workflows/   # CI: build & deploy site to GH Pages
```

## Authoring a new design page

1. Pick a slug, e.g. `radial-bursts`.
2. Copy the template:
   ```sh
   cp templates/design.md docs/designs/radial-bursts.md
   ```
3. Fill in **Vision** and **Inspiration**. Leave **Journey** empty until something happens.
4. Add the page to `nav` in `zensical.toml`.
5. Add a bullet to `docs/designs/index.md` under the appropriate status.
6. Preview locally:
   ```sh
   mise run docs:serve
   ```
   then open <http://localhost:8000>.

Every design page has the same four headings, in this order:

1. **Vision** — what the design is / wants to be.
2. **Inspiration** — references, links, prior art.
3. **Journey** — dated work log, append-only.
4. **Status** — `vision` / `prototyping` / `plotted` / `shelved`.

Pages are **hand-written**. AI assistance is limited to spell-check and light grammar.

## Tasks

All tasks are run via [`mise`](https://mise.jdx.dev/):

| Task | What it does |
| --- | --- |
| `mise run docs:build` | Build the static site into `./site` |
| `mise run docs:serve` | Serve the site locally with live reload |
| `mise run cuboid` | Generate the cuboid SVG |
| `mise run calibrate` | Generate + optimize the plotter calibration sheet |

## Python deps

Managed exclusively with [`uv`](https://docs.astral.sh/uv/). To install / sync:

```sh
uv sync
```

To add a dependency:

```sh
uv add <package>            # runtime
uv add --dev <package>      # dev only
```

## Deployment

On every push to `develop`, GitHub Actions runs `mise run docs:build` and publishes
`./site` to GitHub Pages. The workflow lives in `.github/workflows/docs.yml`.

Repo Settings → Pages must have **Source = GitHub Actions**.
