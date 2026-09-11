export type Analytics = { totals_by_year: Record<string, Record<string, number>>; percentages_by_year?: Record<string, Record<string, number>>; change_between_periods: Record<string, number> };
export type Evidence = { source_id: string; title: string; source: string; snippet: string };
export type Insight = { status: string; summary: string; limitations: string[]; evidence_used?: Evidence[] };
export type ScenarioResult = { selected_units: string[]; allocated_area_sq_m: number; baseline_area_by_class: Record<string, number>; scenario_area_by_class: Record<string, number>; scores: Record<string, number>; limitation: string; scenario_identifier?: string; result_checksum?: string };
export type Dataset = { id: number; name: string; profile_identifier: string; source: string; versions: Array<Record<string, unknown>> };
export type Model = { id: number; model_name: string; provider: string; runtime: string; model_version: string; model_format: string };
export type Catalog = { datasets: Dataset[]; models: Model[] };