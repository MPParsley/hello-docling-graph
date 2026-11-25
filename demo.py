"""Hello World docling-graph demo.

Turns ``data/hello_world.md`` into a knowledge graph with docling-graph and writes
the results (interactive graph, report, CSV/JSON/Cypher exports) to ``site/``.

Extraction backend:
- If ``MISTRAL_API_KEY`` is set, a real remote LLM (Mistral) extracts the entities.
- Otherwise an offline "mock" LLM client returns fixed JSON, so the demo runs
  everywhere (including GitHub Actions without secrets). Docling conversion,
  validation, graph building, exports and visualization are always real.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Iterator

from docling_graph import PipelineConfig, run_pipeline

from templates import Company

ROOT = Path(__file__).parent
SOURCE = ROOT / "data" / "hello_world.md"
OUT = ROOT / "outputs"
SITE = ROOT / "site"

# What a well-behaved LLM would return for data/hello_world.md.
MOCK_EXTRACTION: dict[str, Any] = {
    "name": "Hello World Ltd.",
    "founded": 2024,
    "headquarters": {"city": "Brussels", "country": "Belgium"},
    "employees": [
        {"name": "Ada Lovelace", "role": "Chief Executive", "email": "ada@helloworld.example"},
        {"name": "Alan Turing", "role": "Head of Research", "email": "alan@helloworld.example"},
        {"name": "Grace Hopper", "role": "Lead Engineer", "email": "grace@helloworld.example"},
    ],
    "products": [
        {
            "name": "Greeter",
            "description": 'A service that says "Hello, World!" in 42 languages.',
            "built_by": [{"name": "Grace Hopper"}],
        },
        {
            "name": "Echo",
            "description": "An API that repeats whatever you send it.",
            "built_by": [{"name": "Alan Turing"}],
        },
    ],
}


class MockLLMClient:
    """Offline stand-in implementing docling-graph's ``LLMClientProtocol``."""

    def get_json_response(self, prompt: Any, schema_json: str, *args: Any, **kwargs: Any) -> Any:
        return json.loads(json.dumps(MOCK_EXTRACTION))

    def get_json_response_stream(self, prompt: Any, schema_json: str, *args: Any, **kwargs: Any) -> Iterator[Any]:
        yield self.get_json_response(prompt, schema_json)


def _name(node: dict[str, Any]) -> str:
    if "name" in node:
        return str(node["name"])
    if "city" in node:
        return f"{node['city']}, {node.get('country', '')}"
    return str(node.get("label", "?"))


def main() -> None:
    use_real_llm = bool(os.environ.get("MISTRAL_API_KEY"))
    print(f"Extraction mode: {'Mistral (remote LLM)' if use_real_llm else 'offline mock LLM'}")

    shutil.rmtree(OUT, ignore_errors=True)
    config = PipelineConfig(
        source=str(SOURCE),
        template=Company,
        backend="llm",
        inference="remote",
        extraction_contract="direct",
        use_chunking=False,  # tiny document: one LLM call, no tokenizer download
        output_dir=str(OUT),
        dump_to_disk=True,
        llm_client=None if use_real_llm else MockLLMClient(),
    )
    ctx = run_pipeline(config)

    graph = ctx.knowledge_graph
    print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    for u, v, data in graph.edges(data=True):
        print(f"  {_name(graph.nodes[u])} -[{data.get('label')}]-> {_name(graph.nodes[v])}")

    # Collect everything that was written into a static site folder.
    shutil.rmtree(SITE, ignore_errors=True)
    graph_html = next(iter(sorted(OUT.rglob("graph.html"))), None)
    if graph_html is None:
        raise SystemExit("graph.html was not generated")
    run_dir = graph_html.parent.parent  # outputs/<run>/ (docling/, docling_graph/, metadata.json)
    shutil.copytree(run_dir, SITE / "output")
    shutil.copy(SOURCE, SITE / "hello_world.md")
    shutil.copy(ROOT / "web" / "index.html", SITE / "index.html")
    (SITE / "summary.json").write_text(
        json.dumps(
            {
                "mode": "mistral" if use_real_llm else "mock",
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges(),
            },
            indent=2,
        )
    )
    print(f"Site written to {SITE}")


if __name__ == "__main__":
    main()
