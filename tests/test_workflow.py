import pytest

from fwta.workflow import Task, analyze_workflow


def test_task_expectations() -> None:
    task = Task("x", 0.5, 3, 1.0, 0.5, human_fallback_time=4.0)
    assert task.expected_attempts == pytest.approx(1.75)
    assert task.escalation_probability == pytest.approx(0.125)
    assert task.expected_duration == pytest.approx(1.75 * 1.5 + 0.125 * 4.0)


def test_workflow_critical_path_and_parallelism() -> None:
    tasks = [
        Task("a", 1.0, 1, 2.0, 0.0),
        Task("b", 1.0, 1, 3.0, 0.0, dependencies=("a",)),
        Task("c", 1.0, 1, 4.0, 0.0, dependencies=("a",)),
        Task("d", 1.0, 1, 1.0, 0.0, dependencies=("b", "c")),
    ]
    result = analyze_workflow(tasks, parallel_workers=4, parallel_efficiency=1.0)
    assert result.total_work == pytest.approx(10.0)
    assert result.critical_path == pytest.approx(7.0)
    assert result.estimated_duration == pytest.approx(7.0)


def test_cycle_is_rejected() -> None:
    tasks = [
        Task("a", 1.0, 1, 1.0, 0.0, dependencies=("b",)),
        Task("b", 1.0, 1, 1.0, 0.0, dependencies=("a",)),
    ]
    with pytest.raises(ValueError):
        analyze_workflow(tasks)
