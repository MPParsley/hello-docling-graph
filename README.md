# Hello Docling Graph

A minimal "hello world" for [docling-graph](https://github.com/docling-project/docling-graph):
a small Markdown fact sheet is turned into a knowledge graph, and the result is published
to GitHub Pages by GitHub Actions.

```
data/hello_world.md ──Docling──▶ document ──LLM + Pydantic template──▶ NetworkX graph ──▶ site/ (Pages)
```

## Files

| File | What it does |
|------|--------------|
| `data/hello_world.md` | Input document (a fictional company fact sheet) |
| `templates.py` | Pydantic template: `Company`, `Person`, `Product`, `Location` and edges `EMPLOYS`, `MAKES`, `BUILT_BY`, `HEADQUARTERED_IN` |
| `demo.py` | Runs `docling_graph.run_pipeline(...)` and gathers the output into `site/` |
| `web/index.html` | Landing page that renders `graph.json` with Cytoscape.js |
| `.github/workflows/pages.yml` | Builds the graph on every push/PR, deploys `site/` to Pages from `main` |

## Extraction: mock or real LLM

docling-graph uses an LLM to fill the Pydantic template. To keep the demo runnable without
secrets, `demo.py` plugs in an **offline mock LLM client** (it implements docling-graph's
`LLMClientProtocol` and returns fixed JSON). Docling conversion, validation, graph building,
exports and visualisation are all real.

Set `MISTRAL_API_KEY` (locally, or as a repository secret for Actions) and the demo
uses Mistral (`mistral-small-latest`, docling-graph's default remote model) instead.

## Run locally

```bash
uv venv && uv pip install --torch-backend cpu -r requirements.txt
```

```bash
.venv/bin/python demo.py
```

```bash
python -m http.server -d site 8000
```

Then open http://localhost:8000.

## Enable GitHub Pages (one time)

1. Repository **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Push to `main` (or run the workflow manually). The site URL appears on the workflow run's
   `deploy` job.
