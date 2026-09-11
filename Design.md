# Design — PS26019 MVP

## 1. Design Direction

A professional **policy-intelligence workspace**, not a generic chatbot or standalone GIS portal.

The interface communicates:

**Evidence → Geography → Analytics → Simulation → Decision Insight**

## 2. UX Flow

```text
ASK → EXPLORE → ANALYZE → SIMULATE → UNDERSTAND
```

## 3. Main Screens

### Dashboard
Show:
- selected region;
- land-use KPIs;
- historical change;
- recent scenarios;
- local AI status.

### Evidence Explorer

```text
Search policy/research question
--------------------------------
Filters | Evidence results
Source  | title
Year    | source/year
Topic   | snippet
        | open source
```

### GIS Workspace

```text
Region | Year | Layers | Scenario
-----------------------------------
Layers       |             MAP
□ LULC       |
□ Roads      |
□ Settlements|
□ Boundaries |
-----------------------------------
Agriculture | Built-up | Change | Area
```

### Scenario Workspace

Inputs:
- study area;
- conversion percentage;
- target class;
- factor weights.

Show formula and assumptions before execution.

### Results

Side-by-side:
- baseline;
- scenario;
- KPI delta;
- affected areas on map.

Every simulated value is clearly labeled.

### Local AI Insight

Sections:
- Summary;
- Evidence used;
- Observed facts;
- Scenario result;
- Assumptions;
- Limitations.

## 4. Visual Language

- restrained government/policy aesthetic;
- neutral map interface;
- clear status badges;
- high information density;
- minimal decoration.

## 5. Semantics

Use explicit labels:
- Observed;
- Source-derived;
- Simulated;
- Assumption;
- Model;
- Limitation.

Never make simulated output look like official statistics.

## 6. Local AI Status

Show:

```text
AI Provider: Local
Runtime: Connected / Offline
Model: configured local model
```

System status may show:
- SQLite connected;
- local LLM connected/offline;
- embedding index ready;
- dataset version.

If offline, core non-AI modules remain usable.

## 7. Accessibility

- keyboard navigation;
- readable contrast;
- text alternatives for map information;
- no color-only meaning;
- visible focus;
- accessible KPI tables.

## 8. Three-Minute Demo

1. Ask a policy question.
2. Retrieve evidence.
3. Select Kolkata/peri-urban study area.
4. Show historical land-use change.
5. Configure scenario.
6. Run simulation.
7. Show affected areas/KPI delta.
8. Generate local evidence-backed insight.
