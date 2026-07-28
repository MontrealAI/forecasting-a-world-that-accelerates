from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import networkx as nx


@dataclass(frozen=True)
class Task:
    task_id: str
    success_probability: float
    max_attempts: int
    ai_time: float
    verification_time: float
    human_fallback_time: float = 0.0
    authority_latency: float = 0.0
    external_latency: float = 0.0
    ai_cost: float = 0.0
    verification_cost: float = 0.0
    human_fallback_cost: float = 0.0
    per_attempt_reliability: float | None = None
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    correlated_group: str | None = None

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id cannot be empty")
        if not 0 < self.success_probability <= 1:
            raise ValueError("success_probability must be in (0,1]")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        nonnegative = (
            self.ai_time,
            self.verification_time,
            self.human_fallback_time,
            self.authority_latency,
            self.external_latency,
            self.ai_cost,
            self.verification_cost,
            self.human_fallback_cost,
        )
        if any(value < 0 or not math.isfinite(value) for value in nonnegative):
            raise ValueError("times and costs must be finite and nonnegative")
        reliability = self.success_probability if self.per_attempt_reliability is None else self.per_attempt_reliability
        if not 0 < reliability <= 1:
            raise ValueError("per_attempt_reliability must be in (0,1]")

    @property
    def expected_attempts(self) -> float:
        p = self.success_probability
        return (1.0 - (1.0 - p) ** self.max_attempts) / p

    @property
    def escalation_probability(self) -> float:
        return (1.0 - self.success_probability) ** self.max_attempts

    @property
    def expected_duration(self) -> float:
        return (
            self.expected_attempts * (self.ai_time + self.verification_time)
            + self.escalation_probability * self.human_fallback_time
            + self.authority_latency
            + self.external_latency
        )

    @property
    def expected_cost(self) -> float:
        return (
            self.expected_attempts * (self.ai_cost + self.verification_cost)
            + self.escalation_probability * self.human_fallback_cost
        )

    @property
    def achieved_reliability(self) -> float:
        r = self.success_probability if self.per_attempt_reliability is None else self.per_attempt_reliability
        return 1.0 - (1.0 - r) ** self.max_attempts


@dataclass(frozen=True)
class WorkflowResult:
    total_work: float
    critical_path: float
    coordination_overhead: float
    estimated_duration: float
    workflow_reliability: float
    expected_cost: float
    cost_per_verified_success: float
    escalation_probability_upper_bound: float
    task_metrics: dict[str, dict[str, float]]


def _critical_path_node_weighted(graph: nx.DiGraph, durations: dict[str, float]) -> float:
    order = list(nx.topological_sort(graph))
    finish: dict[str, float] = {}
    for node in order:
        predecessors = list(graph.predecessors(node))
        start = max((finish[pred] for pred in predecessors), default=0.0)
        finish[node] = start + durations[node]
    return max(finish.values(), default=0.0)


def analyze_workflow(
    tasks: list[Task],
    parallel_workers: int = 1,
    parallel_efficiency: float = 1.0,
    coordination_coefficient: float = 0.0,
    correlated_failure_penalty: float = 0.0,
) -> WorkflowResult:
    if not tasks:
        raise ValueError("at least one task is required")
    if parallel_workers < 1:
        raise ValueError("parallel_workers must be at least 1")
    if not 0 < parallel_efficiency <= 1:
        raise ValueError("parallel_efficiency must be in (0,1]")
    if coordination_coefficient < 0 or correlated_failure_penalty < 0:
        raise ValueError("coordination and correlation penalties must be nonnegative")

    task_map = {task.task_id: task for task in tasks}
    if len(task_map) != len(tasks):
        raise ValueError("task_id values must be unique")
    graph = nx.DiGraph()
    graph.add_nodes_from(task_map)
    for task in tasks:
        for dependency in task.dependencies:
            if dependency not in task_map:
                raise ValueError(f"unknown dependency {dependency!r} for task {task.task_id!r}")
            graph.add_edge(dependency, task.task_id)
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("workflow dependencies must form a directed acyclic graph")

    durations = {task.task_id: task.expected_duration for task in tasks}
    total_work = sum(durations.values())
    critical_path = _critical_path_node_weighted(graph, durations)
    effective_workers = parallel_workers**parallel_efficiency
    coordination = coordination_coefficient * max(0.0, math.log2(parallel_workers))
    estimated_duration = max(critical_path, total_work / effective_workers) + coordination

    log_reliability = sum(math.log(max(task.achieved_reliability, 1e-300)) for task in tasks)
    log_reliability -= correlated_failure_penalty
    workflow_reliability = min(1.0, max(0.0, math.exp(log_reliability)))
    expected_cost = sum(task.expected_cost for task in tasks)
    cost_per_verified = math.inf if workflow_reliability <= 0 else expected_cost / workflow_reliability
    escalation_upper = min(1.0, sum(task.escalation_probability for task in tasks))

    metrics = {
        task.task_id: {
            "expected_attempts": task.expected_attempts,
            "escalation_probability": task.escalation_probability,
            "expected_duration": task.expected_duration,
            "expected_cost": task.expected_cost,
            "achieved_reliability": task.achieved_reliability,
        }
        for task in tasks
    }
    return WorkflowResult(
        total_work=total_work,
        critical_path=critical_path,
        coordination_overhead=coordination,
        estimated_duration=estimated_duration,
        workflow_reliability=workflow_reliability,
        expected_cost=expected_cost,
        cost_per_verified_success=cost_per_verified,
        escalation_probability_upper_bound=escalation_upper,
        task_metrics=metrics,
    )


def task_from_mapping(record: dict[str, Any]) -> Task:
    dependencies = tuple(record.get("dependencies", ()))
    return Task(
        task_id=str(record["task_id"]),
        success_probability=float(record["success_probability"]),
        max_attempts=int(record["max_attempts"]),
        ai_time=float(record["ai_time"]),
        verification_time=float(record["verification_time"]),
        human_fallback_time=float(record.get("human_fallback_time", 0.0)),
        authority_latency=float(record.get("authority_latency", 0.0)),
        external_latency=float(record.get("external_latency", 0.0)),
        ai_cost=float(record.get("ai_cost", 0.0)),
        verification_cost=float(record.get("verification_cost", 0.0)),
        human_fallback_cost=float(record.get("human_fallback_cost", 0.0)),
        per_attempt_reliability=(
            None if record.get("per_attempt_reliability") is None else float(record["per_attempt_reliability"])
        ),
        dependencies=dependencies,
        correlated_group=record.get("correlated_group"),
    )
