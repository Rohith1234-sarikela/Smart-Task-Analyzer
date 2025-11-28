from datetime import date
from typing import List, Dict, Any, Tuple, Set

TODAY = date.today()

def build_dependency_graph(tasks: List[Dict[str, Any]]) -> Tuple[Dict[int, List[int]], Dict[int, int]]:
    """Returns adjacency (id -> deps) and dependents count (id -> num tasks blocked by this)."""
    adjacency = {}
    dependents_count = {}

    id_set: Set[int] = set()
    for t in tasks:
        if "id" in t and t["id"] is not None:
            id_set.add(t["id"])

    for t in tasks:
        tid = t.get("id")
        deps = t.get("dependencies") or []
        adjacency[tid] = deps
        for dep_id in deps:
            if dep_id in id_set:
                dependents_count[dep_id] = dependents_count.get(dep_id, 0) + 1

    for tid in id_set:
        dependents_count.setdefault(tid, 0)

    return adjacency, dependents_count

def detect_cycles(adjacency: Dict[int, List[int]]) -> Set[int]:
    """Detect circular dependencies via DFS. Returns set of ids involved in cycles."""
    visited = set()
    stack = set()
    cyclic = set()

    def dfs(node: int):
        if node in stack:
            cyclic.update(stack)
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nei in adjacency.get(node, []):
            dfs(nei)
        stack.remove(node)

    for node in adjacency.keys():
        dfs(node)

    return cyclic

def compute_urgency(due_date):
    if not due_date:
        # No due date → neutral urgency
        return 8, False

    delta_days = (due_date - TODAY).days
    if delta_days < 0:
        # Overdue, weight more
        overdue_days = abs(delta_days)
        urgency = 25 + min(10, overdue_days)  # max ~35
        return urgency, True
    elif delta_days == 0:
        return 25, False
    elif delta_days <= 3:
        return 20, False
    elif delta_days <= 7:
        return 15, False
    elif delta_days <= 14:
        return 10, False
    else:
        return 5, False

def compute_effort_component(hours: float) -> float:
    if hours <= 1:
        return 12
    elif hours <= 3:
        return 9
    elif hours <= 6:
        return 5
    elif hours <= 10:
        return 3
    else:
        return 1

def normalize_score(score: float) -> float:
    return max(0.0, min(100.0, round(score, 2)))

def smart_balance_score(importance, urgency, effort_comp, deps_comp, has_cycle: bool) -> float:
    score = (
        importance * 3.0
        + urgency * 1.8
        + effort_comp * 1.2
        + deps_comp * 1.5
    )
    if has_cycle:
        score -= 10  # Penalize cyclic tasks slightly
    return normalize_score(score)

def fastest_wins_score(importance, urgency, effort_comp, deps_comp, has_cycle: bool) -> float:
    score = (
        effort_comp * 3.0
        + importance * 1.5
        + urgency * 1.0
        + deps_comp * 1.0
    )
    if has_cycle:
        score -= 10
    return normalize_score(score)

def high_impact_score(importance, urgency, effort_comp, deps_comp, has_cycle: bool) -> float:
    score = (
        importance * 4.0
        + urgency * 1.2
        + deps_comp * 1.5
        - effort_comp * 0.5
    )
    if has_cycle:
        score -= 10
    return normalize_score(score)

def deadline_driven_score(importance, urgency, effort_comp, deps_comp, has_cycle: bool) -> float:
    score = (
        urgency * 4.0
        + importance * 2.0
        + deps_comp * 1.0
        - effort_comp * 0.3
    )
    if has_cycle:
        score -= 10
    return normalize_score(score)

STRATEGY_FUNCTIONS = {
    "smart_balance": smart_balance_score,
    "fastest_wins": fastest_wins_score,
    "high_impact": high_impact_score,
    "deadline_driven": deadline_driven_score,
}

def build_explanation(task, urgency, is_overdue, effort_comp, deps_count, has_cycle, strategy):
    reasons = []

    if is_overdue:
        reasons.append("Task is overdue and should be addressed immediately.")
    elif urgency >= 20:
        reasons.append("Task has a very near deadline.")
    elif urgency >= 15:
        reasons.append("Task deadline is approaching soon.")

    importance = task["importance"]
    if importance >= 9:
        reasons.append("Marked as critical in importance.")
    elif importance >= 7:
        reasons.append("Marked as high importance.")

    hours = task["estimated_hours"]
    if hours <= 2:
        reasons.append("Low effort – good quick win.")
    elif hours >= 8:
        reasons.append("High effort – plan adequate time.")

    if deps_count > 0:
        reasons.append(f"This task is blocking {deps_count} other task(s).")

    if has_cycle:
        reasons.append("Warning: This task is part of a circular dependency; review dependencies.")

    if not reasons:
        reasons.append("Balanced task with moderate urgency, importance, and effort.")

    strategy_labels = {
        "smart_balance": "Smart Balance: trade-off between urgency, impact, effort, and dependencies.",
        "fastest_wins": "Fastest Wins: favors tasks that can be completed quickly.",
        "high_impact": "High Impact: favors high-importance tasks, even if they take more time.",
        "deadline_driven": "Deadline Driven: favors tasks with the closest deadlines.",
    }
    reasons.append(strategy_labels[strategy])

    return " ".join(reasons)

def analyze_tasks(tasks: List[Dict[str, Any]], strategy: str = "smart_balance") -> List[Dict[str, Any]]:
    adjacency, dependents_count = build_dependency_graph(tasks)
    cyclic_ids = detect_cycles(adjacency)

    scorer = STRATEGY_FUNCTIONS[strategy]

    scored = []
    for t in tasks:
        tid = t.get("id")
        due_date = t.get("due_date")
        importance = t["importance"]
        hours = float(t["estimated_hours"])

        urgency, is_overdue = compute_urgency(due_date)
        effort_comp = compute_effort_component(hours)
        deps_comp = float(dependents_count.get(tid, 0))
        has_cycle = tid in cyclic_ids if tid is not None else False

        score = scorer(importance, urgency, effort_comp, deps_comp, has_cycle)
        explanation = build_explanation(
            t, urgency, is_overdue, effort_comp, int(deps_comp), has_cycle, strategy
        )

        enriched = {
            **t,
            "score": score,
            "strategy": strategy,
            "is_overdue": is_overdue,
            "blocks_tasks": int(deps_comp),
            "has_circular_dependency": has_cycle,
            "explanation": explanation,
        }
        scored.append(enriched)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
