"""
The ESI rules engine.

Reads esi_rules.yaml and evaluates a (TriageRequest, ExtractedFacts) pair
against all rules in order: A → B → C → D. Returns an EngineResult.

This module contains ZERO medical knowledge. All clinical logic lives in
esi_rules.yaml, which is traceable to the AHRQ ESI Handbook v4. The engine
is pure mechanics: load rules, evaluate conditions, pick a level.
"""

from pathlib import Path

import yaml
from models import TriageRequest
from rules.facts import ExtractedFacts
from rules.result import EngineResult


RULES_PATH = Path(__file__).parent / "esi_rules.yaml"

# Data-driven operator dispatch: each YAML operator maps to a Python function.
# Adding a new operator = adding one line here. The rest of the engine doesn't change.

OPERATORS = {
    "equals": lambda actual, expected: actual == expected,
    "not_equals": lambda actual, expected: actual != expected,
    "less_than": lambda actual, expected: actual < expected,
    "less_than_or_equal": lambda actual, expected: actual <= expected,
    "greater_than": lambda actual, expected: actual > expected,
    "greater_than_or_equal": lambda actual, expected: actual >= expected,
    "contains": lambda actual, expected: expected in actual if actual is not None else False,

}


def load_rules() -> list[dict]:
    " Read esi_rules.yaml and return the list of rules dicts."
    with open(RULES_PATH) as f:
        return yaml.safe_load(f)["rules"]
    

def build_fact_pool(request: TriageRequest, facts: ExtractedFacts) -> dict:
    " Merge TriageRequest + ExtractedFacts + computed fields into one flat dict."
    pool = request.model_dump(mode='json')
    pool.update(facts.model_dump(mode='json'))
    pool["predicted_resource_count"] = len(facts.predicted_resources)
    pool.setdefault("patient_age_months", None) 
    return pool


def evaluate_condition(cond: dict, pool: dict) -> bool:
    "Recursively evaluate a condition, handles simple, all_of and any_of shape."
    if "all_of" in cond:
        return all(evaluate_condition(c, pool) for c in cond["all_of"])
    if "any_of" in cond:
        return any(evaluate_condition(c, pool) for c in cond["any_of"])
    
    actual = pool.get(cond["field"])
    if actual is None:
        return False
    return OPERATORS[cond["operator"]](actual, cond["value"])


def evaluate_rule(rule: dict, pool: dict) -> bool:
    "A rule fires when applies_when (if present) is true AND trigger is true."
    applies_when = rule.get("applies_when")
    if applies_when and not evaluate_condition(applies_when, pool):
        return False
    return evaluate_condition(rule["trigger"], pool)


def triage(request: TriageRequest, facts: ExtractedFacts) -> EngineResult:
    "Run all rules in handbook order; return the assigned ESI level + reasoning."
    rules = load_rules()
    pool = build_fact_pool(request, facts)

    primary_rule = None  # First A/B/C rule that fires (the base level)
    upgrade_rule = None  # Any D rule that fires (upgrades C → 2)

    for rule in rules:
        if not evaluate_rule(rule, pool):
            continue

        decision_point = rule["decision_point"]
        if decision_point == "D":
            upgrade_rule = rule
        elif primary_rule is None:
            primary_rule = rule
            if decision_point in ("A", "B"):
                break  # A/B is definitive — no D upgrade possible

    if primary_rule is None:
        raise RuntimeError("No primary rule fired. Check that Decision C rules cover all cases.")

    # C-level base with a D upgrade → ESI 2
    if primary_rule["decision_point"] == "C" and upgrade_rule:
        return EngineResult(
            esi_level=upgrade_rule["esi_level"],
            rules_fired=[primary_rule["rule_id"], upgrade_rule["rule_id"]],
            rationales=[primary_rule["rationale"], upgrade_rule["rationale"]],
            decision_path="C_upgraded_by_D",
        )

    return EngineResult(
        esi_level=primary_rule["esi_level"],
        rules_fired=[primary_rule["rule_id"]],
        rationales=[primary_rule["rationale"]],
        decision_path=primary_rule["decision_point"],
    )


