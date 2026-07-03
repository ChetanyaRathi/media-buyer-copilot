from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from . import agent, actions
from .metrics import compute_metrics


class PipelineState(TypedDict):
    canonical_rows: list
    metrics: list
    decisions: list
    summary: dict


def metrics_node(state: PipelineState) -> dict:
    return {"metrics": compute_metrics(state["canonical_rows"])}


def decide_node(state: PipelineState) -> dict:
    return {"decisions": agent.decide(state["metrics"])}


def critique_node(state: PipelineState) -> dict:
    return {"decisions": agent.critique(state["metrics"], state["decisions"])}


def actions_node(state: PipelineState) -> dict:
    metrics = state["metrics"]
    by_key = {(m["platform"], m["campaign"], m["ad_set"]): m for m in metrics}
    decisions = []
    for decision in state["decisions"]:
        key = (decision["platform"], decision["campaign"], decision["ad_set"])
        metric = by_key.get(key, {})
        draft = actions.draft_action(decision, metric)
        decisions.append({**decision, **draft})
    summary = actions.build_summary(metrics, decisions)
    return {"decisions": decisions, "summary": summary}


def _build():
    graph = StateGraph(PipelineState)
    graph.add_node("compute_metrics", metrics_node)
    graph.add_node("decide", decide_node)
    graph.add_node("critique", critique_node)
    graph.add_node("actions", actions_node)
    graph.add_edge(START, "compute_metrics")
    graph.add_edge("compute_metrics", "decide")
    graph.add_edge("decide", "critique")
    graph.add_edge("critique", "actions")
    graph.add_edge("actions", END)
    return graph.compile()


PIPELINE = _build()


def run_pipeline(canonical_rows: list[dict]) -> dict:
    final = PIPELINE.invoke(
        {"canonical_rows": canonical_rows, "metrics": [], "decisions": [], "summary": {}}
    )
    return {
        "summary": final["summary"],
        "metrics": final["metrics"],
        "decisions": final["decisions"],
    }
