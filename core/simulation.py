"""Deterministic, explainable policy scenario simulation."""

from dataclasses import asdict, dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class CandidateArea:
    spatial_unit_id: str
    land_use_class: str
    area_sq_m: float
    urban_proximity: float
    population_pressure: float
    infrastructure_access: float
    environmental_constraint: float
    eligible: bool = True


@dataclass(frozen=True)
class ScenarioParameters:
    requested_area_sq_m: float
    target_land_use_class: str
    weights: Mapping[str, float]
    scenario_version: str
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class SimulationResult:
    selected_units: tuple[str, ...]
    allocated_area_sq_m: float
    baseline_area_by_class: dict[str, float]
    scenario_area_by_class: dict[str, float]
    scores: dict[str, float]
    parameters: dict
    limitation: str

    def as_dict(self) -> dict:
        return asdict(self)


def run_conversion_scenario(
    candidates: Iterable[CandidateArea],
    parameters: ScenarioParameters,
) -> SimulationResult:
    """Rank eligible agricultural candidates and allocate a requested area."""
    if parameters.requested_area_sq_m < 0:
        raise ValueError("Requested conversion area cannot be negative")
    required_factors = {
        "urban_proximity",
        "population_pressure",
        "infrastructure_access",
        "environmental_constraint",
    }
    if set(parameters.weights) != required_factors:
        raise ValueError("Weights must define exactly the four scenario factors")
    if any(weight < 0 for weight in parameters.weights.values()):
        raise ValueError("Scenario weights cannot be negative")

    collected = list(candidates)
    if any(candidate.area_sq_m < 0 for candidate in collected):
        raise ValueError("Candidate areas cannot be negative")
    baseline = _totals(collected)
    eligible = [
        candidate
        for candidate in collected
        if candidate.eligible and candidate.land_use_class == "agriculture"
    ]
    scored = {
        candidate.spatial_unit_id: _score(candidate, parameters.weights)
        for candidate in eligible
    }
    ranked = sorted(
        eligible,
        key=lambda candidate: (-scored[candidate.spatial_unit_id], candidate.spatial_unit_id),
    )

    remaining = parameters.requested_area_sq_m
    selected: list[tuple[CandidateArea, float]] = []
    for candidate in ranked:
        if remaining <= 0:
            break
        allocated_from_candidate = min(candidate.area_sq_m, remaining)
        selected.append((candidate, allocated_from_candidate))
        remaining -= allocated_from_candidate

    allocated_area = min(
        parameters.requested_area_sq_m,
        sum(allocated_area for _, allocated_area in selected),
    )
    scenario = dict(baseline)
    for candidate, allocated_from_candidate in selected:
        scenario["agriculture"] = scenario.get("agriculture", 0.0) - allocated_from_candidate
        scenario[parameters.target_land_use_class] = scenario.get(
            parameters.target_land_use_class, 0.0
        ) + allocated_from_candidate

    return SimulationResult(
        selected_units=tuple(candidate.spatial_unit_id for candidate, _ in selected),
        allocated_area_sq_m=round(allocated_area, 6),
        baseline_area_by_class={key: round(value, 6) for key, value in baseline.items()},
        scenario_area_by_class={key: round(value, 6) for key, value in scenario.items()},
        scores={key: round(value, 6) for key, value in scored.items()},
        parameters={
            "requested_area_sq_m": parameters.requested_area_sq_m,
            "target_land_use_class": parameters.target_land_use_class,
            "weights": dict(parameters.weights),
            "scenario_version": parameters.scenario_version,
            "assumptions": list(parameters.assumptions),
        },
        limitation="Scenario analysis only; this is not an authoritative prediction of future land use.",
    )


def _score(candidate: CandidateArea, weights: Mapping[str, float]) -> float:
    return (
        weights["urban_proximity"] * candidate.urban_proximity
        + weights["population_pressure"] * candidate.population_pressure
        + weights["infrastructure_access"] * candidate.infrastructure_access
        - weights["environmental_constraint"] * candidate.environmental_constraint
    )


def _totals(candidates: Iterable[CandidateArea]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for candidate in candidates:
        totals[candidate.land_use_class] = totals.get(candidate.land_use_class, 0.0) + candidate.area_sq_m
    return totals
