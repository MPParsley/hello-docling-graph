"""Pydantic templates that describe the knowledge graph we want docling-graph to build.

- Entities (nodes with a stable identity) declare ``graph_id_fields``.
- Relationships (edges) are declared with ``edge(label=...)``.
"""

from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field


def edge(label: str, **kwargs: Any) -> Any:
    """Mark a field as a graph edge with the given label."""
    return Field(json_schema_extra={"edge_label": label}, **kwargs)


class Location(BaseModel):
    """A city/country where an organization is based."""

    model_config = ConfigDict(graph_id_fields=["city", "country"])
    city: str = Field(description="City name, e.g. 'Brussels'")
    country: str = Field(description="Country name, e.g. 'Belgium'")


class Person(BaseModel):
    """A team member of the company."""

    model_config = ConfigDict(graph_id_fields=["name"])
    name: str = Field(description="Full name of the person")
    role: str | None = Field(default=None, description="Job title")
    email: str | None = Field(default=None, description="Email address")


class Product(BaseModel):
    """A product made by the company."""

    model_config = ConfigDict(graph_id_fields=["name"])
    name: str = Field(description="Product name")
    description: str | None = Field(default=None, description="What the product does")
    built_by: List[Person] = edge("BUILT_BY", default_factory=list, description="People who built it")


class Company(BaseModel):
    """Root document entity: the company described in the fact sheet."""

    model_config = ConfigDict(graph_id_fields=["name"])
    name: str = Field(description="Legal company name")
    founded: int | None = Field(default=None, description="Year founded")
    headquarters: Location | None = edge("HEADQUARTERED_IN", default=None, description="HQ location")
    employees: List[Person] = edge("EMPLOYS", default_factory=list, description="Team members")
    products: List[Product] = edge("MAKES", default_factory=list, description="Products")
