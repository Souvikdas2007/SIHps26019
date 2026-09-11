"""Deterministic land-use analytics."""

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class LandUseObservation:
    spatial_unit_id: str
    observed_year: int
    land_use_class: str
    area_sq_m: float


@dataclass(frozen=True)
class AnalyticsSummary:
    totals_by_year: dict[int, dict[str, float]]
    percentages_by_year: dict[int, dict[str, float]]
    change_between_periods: dict[str, float]
    observation_count: int

    def as_dict(self) -> dict:
        return asdict(self)


def summarize_land_use(observations: Iterable[LandUseObservation]) -> AnalyticsSummary:
    """Calculate class totals, percentages and first-to-last changes."""
    collected = list(observations)
    if not collected:
        raise ValueError("At least one land-use observation is required")
    if any(observation.area_sq_m < 0 for observation in collected):
        raise ValueError("Observation areas cannot be negative")

    totals_by_year: dict[int, dict[str, float]] = {}
    for observation in collected:
        year_totals = totals_by_year.setdefault(observation.observed_year, {})
        year_totals[observation.land_use_class] = round(
            year_totals.get(observation.land_use_class, 0.0) + observation.area_sq_m,
            6,
        )

    percentages_by_year: dict[int, dict[str, float]] = {}
    for year, class_totals in totals_by_year.items():
        total_area = sum(class_totals.values())
        percentages_by_year[year] = {
            land_use_class: round((area / total_area) * 100, 6)
            for land_use_class, area in class_totals.items()
        }

    years = sorted(totals_by_year)
    first_year, last_year = years[0], years[-1]
    classes = set(totals_by_year[first_year]) | set(totals_by_year[last_year])
    change_between_periods = {
        land_use_class: round(
            totals_by_year.get(last_year, {}).get(land_use_class, 0.0)
            - totals_by_year.get(first_year, {}).get(land_use_class, 0.0),
            6,
        )
        for land_use_class in sorted(classes)
    }

    return AnalyticsSummary(
        totals_by_year=totals_by_year,
        percentages_by_year=percentages_by_year,
        change_between_periods=change_between_periods,
        observation_count=len(collected),
    )
