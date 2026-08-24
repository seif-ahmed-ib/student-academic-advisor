# Student Academic Advisor

A course project for **Basic of AI Programming Skills (DSC 311)** that combines:

- **Part A:** an explainable fuzzy rule-based Expert System.
- **Part B:** reproducible K-Means clustering on student performance data.

The two parts share the Student Academic Advisor domain and academic concepts while
remaining independent implementations. Their outputs are compared post-hoc rather
than forcing cluster labels into rules or Expert System results into training.

## Current Status

- Part A implementation complete.
- Part B implementation and executable notebook complete.
- Part A / Part B integration analysis complete.
- Inference Network Diagram and worked inference example complete.
- Streamlit presentation interface complete.
- **219 automated tests passing** at the audited project checkpoint.

## Main Results

- Dataset: UCI Student Performance, `student-por.csv` (649 records).
- K-Means features: `G1`, `G2`, `absences`, `studytime`, and `failures`.
- Final K: **2**, selected from candidates 2 through 10.
- Selected Silhouette Score: **0.2716647**.
- Cluster sizes: **332** and **317** students.
- The higher-support profile has a mean Expert System fuzzy Union of `0.459942`,
  compared with `0.128029` for the stronger academic profile.

These clusters are descriptive profiles, not ground-truth risk labels.

## Project Structure

```text
student_academic_advisor/
  expert_system/       Part A facts, rules, parser, inference, trace, aggregation
  ml_pipeline/         Part B preparation, K-Means, evaluation, reporting
  integration/         Post-hoc comparison of independent Part A and Part B outputs
data/raw/               Original UCI source files
notebooks/              Executable Part B analysis notebook
outputs/                Reproducible Part A, Part B, and integration artifacts
docs/                   Decisions, diagrams, analyses, audit, and final report
tests/                  Expert System, ML pipeline, and integration tests
```

## Setup

The project was validated with Python 3.11.

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run Tests

```bat
python -m pytest -q
```

## Run Part A

Generate the complete `POR-0649` fuzzy-inference trace and Markdown example:

```bat
python -m student_academic_advisor.expert_system.demo
```

## Run Part B

Regenerate K-Means metrics, assignments, profiles, chart, and results document:

```bat
python -m student_academic_advisor.ml_pipeline.run_pipeline
```

Open the presentation notebook:

```text
notebooks/part_b_kmeans_analysis.ipynb
```

## Run the Integration Analysis

```bat
python -m student_academic_advisor.integration.run_analysis
```

## Key Documentation

- [Final report](docs/report/FINAL_REPORT.md)
- [Final compliance audit](docs/project-management/FINAL_COMPLIANCE_AUDIT.md)
- [Master requirements checklist](docs/project-management/MASTER_REQUIREMENTS_CHECKLIST.md)
- [Architecture decisions](docs/project-management/ARCHITECTURE_DECISIONS.md)
- [Fuzzy fact design](docs/part-a/FUZZY_FACTS_AND_MEMBERSHIP_DESIGN.md)
- [Rule-base design](docs/part-a/RULE_BASE_AND_DEPENDENCY_DESIGN.md)
- [Inference Network Diagram](docs/part-a/INFERENCE_NETWORK_DIAGRAM.md)
- [Worked inference example](outputs/part-a/worked_example_por_0649.md)
- [K-Means results](docs/part-b/KMEANS_RESULTS.md)
- [Part A / Part B integration](docs/integration/PART_A_PART_B_INTEGRATION.md)

## Method Boundaries

- Production Rules and O-A-V facts are the two Knowledge Representation techniques.
- The Knowledge Base is external data and is separate from inference logic.
- The system uses forward chaining, dependency resolution, topological ordering,
  cycle detection, and live explainability traces.
- Fuzzy operators are AND=min, OR=max, and NOT=`1-x`; each rule uses
  `CV = FV * CF`.
- K-Means uses separately standardized raw features.
- `G3` is excluded from both Part A premises and K-Means training and is used only
  for post-hoc interpretation.
- No arbitrary firing threshold is used.

## Dataset Attribution

The project uses the
[UCI Student Performance dataset](https://doi.org/10.24432/C5TG7T), created by
Paulo Cortez and licensed under CC BY 4.0. The original data dictionary is retained
with the raw files.

## Streamlit Presentation Layer

The project includes an optional Streamlit interface for presentation and
demonstration purposes. It reuses the tested Part A, Part B, and integration
implementations rather than duplicating their logic.

The interface provides:

- Project overview and workflow.
- Interactive individual-student fuzzy Expert System inference.
- Raw inputs and fuzzified facts.
- Rule-by-rule FV, CF, and CV inference trace.
- Final Conclusions, Maximum aggregation, and fuzzy Union.
- Inference Network Diagram.
- Part B data-preparation evidence.
- K-Means K-selection results and visualizations.
- Cluster profiles and interpretations.
- Part A / Part B post-hoc integration results.
- Project sources, methodological boundaries, and limitations.

Run the interface with:

```bat
python -m streamlit run streamlit_app.py
```
