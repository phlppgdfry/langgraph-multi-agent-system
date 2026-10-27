"""Pydantic V2 schemas for structured multi-agent communication and report validation."""

from typing import Literal

from pydantic import BaseModel, Field


class MetricItem(BaseModel):
    """Quantitative indicator extracted from unstructured research text."""

    metric: str = Field(..., description="Name or label of the metric")
    value: str = Field(
        ..., description="Observed quantitative value (e.g., '+42%', '$3.4M')"
    )
    type: Literal[
        "percentage", "financial", "performance", "accuracy", "roi", "observability"
    ] = Field(..., description="Category classification")
    context: str | None = Field(
        None, description="Contextual excerpt or source validation"
    )


class ResearchNote(BaseModel):
    """Structured evidence snippet gathered by researcher agents."""

    title: str = Field(..., description="Title of the source document or study")
    snippet: str = Field(..., description="Excerpt or summarized findings")
    source: str = Field(..., description="URL, domain, or internal citation")
    category: str = Field("evidence", description="Classification of the finding")


class CriticVerdict(BaseModel):
    """Self-correction evaluation result produced by the Critic agent."""

    score: int = Field(..., ge=0, le=100, description="Rigor score from 0 to 100")
    passed: bool = Field(
        ..., description="True if score meets or exceeds minimum threshold"
    )
    verified: bool = Field(
        ..., description="True if claims are corroborated by primary sources"
    )
    strengths: list[str] = Field(
        default_factory=list, description="Validated strong points"
    )
    recommendation: str = Field(
        ..., description="Actionable critique or approval feedback"
    )


class ExecutiveReport(BaseModel):
    """Final synthesized briefing structure."""

    title: str = Field(..., description="Title of the briefing")
    executive_summary: str = Field(..., description="High-level executive overview")
    scorecard: list[MetricItem] = Field(
        default_factory=list, description="Quantitative indicators"
    )
    strategic_findings: list[str] = Field(
        default_factory=list, description="Core actionable findings"
    )
    critic_score: int = Field(..., description="Rigor score assigned by the Critic")
    sources: list[str] = Field(
        default_factory=list, description="Validated source URLs"
    )
    generated_at: str = Field(..., description="ISO 8601 date string")
