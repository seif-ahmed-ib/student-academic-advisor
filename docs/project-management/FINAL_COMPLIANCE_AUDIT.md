# Final Requirements Compliance Audit

Course: **Basic of AI Programming Skills (DSC 311)**
Project: **Student Academic Advisor**
Audit version: **1.0**
Audit date: **2026-08-23**
Technical baseline: **219 automated tests passed**

## 1. Verdict

**Technical and rubric evidence: PASS.**

No blocking implementation gap was found in the official Part A or Part B
requirements. The repository contains source code and reproducible evidence for
Knowledge Representation, forward-chaining inference, fuzzy reasoning, the required
Inference Network Diagram, K-Means data preparation and evaluation, and domain-level
interpretation connecting both parts.

The project is not yet administratively submission-ready because the official Cover
Sheet requires real team data and handwritten attendance signatures. The final
Markdown report must also be exported to the format requested by the TA and visually
checked. Individual-assessment preparation remains important because it represents
9 of the 20 marks shown on the Cover Sheet.

## 2. Audit Scope and Source Precedence

The audit used this precedence:

1. `AI_Skills_Project_Description.pdf`.
2. `DSC-311-Group-Project-Cover-Sheets-(HNU--Summer2026).pdf`.
3. Approved project decision documents.
4. Implemented source code and generated artifacts.
5. Automated tests and reproducible executions.

No optional feature is counted as an official requirement.

## 3. Mark-Oriented Compliance Matrix

| Rubric item | Marks | Status | Principal evidence |
|---|---:|---|---|
| Part A - Knowledge Representation | 2 | PASS | `rules.json`, O-A-V `Fact`, parser, architecture and rule-design documents |
| Part A - Inference Engine | 1 | PASS | dependency graph, cycle detection, forward engine, Working Memory, trace tests |
| Part A - Fuzzy Logic | 2 | PASS | five memberships, min/max/1-x, FV/CF/CV, Maximum/Union, worked example |
| Part A - Inference Network Diagram | 1 | PASS | `inference_network.png`, `inference_network.svg`, diagram mapping document |
| Part A - Individual | 4 | PREPARATION REQUIRED | Technical material exists; every member must be able to explain it |
| Part B - Data Preparation | 2 | PASS | dataset audit, feature decisions, preprocessing code, notebook and tests |
| Part B - Model Implementation | 2 | PASS | scikit-learn K-Means pipeline, deterministic configuration and assignments |
| Part B - Evaluation | 1 | PASS | K=2..10 inertia/Silhouette results, chart, profiles and interpretation |
| Part B - Individual | 5 | PREPARATION REQUIRED | Technical material exists; every member must be able to defend it |

The audit does not predict the awarded grade. It confirms that evidence exists for
each non-individual rubric row and identifies the remaining individual preparation.

## 4. Part A Evidence Review

### 4.1 Knowledge Representation

The project uses two distinct techniques:

- Production Rules stored outside engine logic in
  `student_academic_advisor/expert_system/knowledge_base/rules.json`.
- O-A-V fuzzy facts represented by immutable `Fact` records containing student
  object ID, attribute, value in `[0,1]`, and origin.

Rules have separate `id`, `condition`, `conclusion`, `cf`, and `description` fields.
Conditions are parsed once into a restricted AST. The engine interprets this data;
it does not hide academic conclusions in domain-specific control flow.

### 4.2 Rule Base

The six-rule Knowledge Base is compact but non-trivial:

- Nested conditions: R3, R4, and R6.
- NOT precedence example: R5.
- Chained edges: R1 -> R3, R2 -> R3, and R3 -> R6.
- Three structurally Intermediate and three structurally Final Conclusions.

Validation rejects duplicate IDs, duplicate producers, invalid fields, invalid CFs,
unknown facts, collisions, malformed conditions, and rule sets with no Final
Conclusion.

### 4.3 Inference Engine and Explainability

The engine implements forward chaining. The dependency graph is topologically
sorted, with Knowledge Base declaration order used for deterministic ties. Cycles
and self-dependencies are reported before inference.

Every evaluated rule produces a live trace containing condition text, premise
values, operator steps, FV, CF, CV, fired/contributes flags, conclusion attribute
and value, structural status, and evaluation order.

### 4.4 Fuzzy Logic

Five key student facts are fuzzified into `[0,1]`. The implementation provides:

- `AND = min`.
- `OR = max`.
- `NOT(x) = 1 - x`.
- `CV = FV * CF`.
- CV propagation through Intermediate Conclusions.
- Maximum and fuzzy Union across Final Conclusions only.

No configurable firing threshold is used. A rule fires when `FV > 0`; it contributes
when `CV > 0`. Zero-valued facts remain defined.

### 4.5 Diagram and Worked Example

The diagram uses every official symbol: square facts, circle-inside-square
Intermediate Conclusions, plain-circle Final Conclusions, and AND/OR/NOT gates.
The `POR-0649` report follows a complete path and lists every FV, CF, and CV as well
as Maximum and Union.

## 5. Part B Evidence Review

### 5.1 Data Preparation

The selected source is UCI Student Performance, `student-por.csv`:

- 649 rows and 33 raw columns.
- Semicolon delimiter.
- Zero missing rows, empty strings, and exact duplicates.
- Five training features: `G1`, `G2`, `absences`, `studytime`, and `failures`.
- No nominal encoding needed for this selected numerical/ordinal matrix.
- `StandardScaler` applied before distance-based clustering.
- `G3` excluded from training and used only post-hoc.

The pipeline checks missingness and duplicates rather than inventing cleaning work
that the selected file does not need.

### 5.2 Model Implementation

The project uses scikit-learn K-Means with `random_state=42` and `n_init=20`.
Candidates `K=2` through `K=10` are evaluated, and the final model assigns all 649
retained records to one of two clusters.

### 5.3 Evaluation and Interpretation

`K=2` achieved the highest observed Silhouette Score, `0.2716647`. The Elbow curve
does not have one sharp break, and K=4 is close, so the report correctly presents
K=2 as the strongest relative and parsimonious tested choice rather than an
objective natural truth.

Observed profiles:

| Cluster | Descriptive profile | Students | G1 mean | G2 mean | Absences mean | Study time mean | Failures mean |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | Stronger academic profile | 332 | 13.380 | 13.593 | 2.401 | 2.286 | 0.012 |
| 1 | Higher academic-support-need profile | 317 | 9.325 | 9.451 | 4.978 | 1.558 | 0.442 |

The Silhouette Score indicates overlap, so the report correctly avoids calling the
clusters ground-truth risk classes.

## 6. Part A / Part B Coherence

Both systems use the same academic concepts but remain methodologically independent:

- Part A converts one student's raw values to fuzzy facts and applies explicit
  rules.
- Part B scales raw population features and discovers clusters without expert
  conclusions.
- Integration occurs after both runs by joining `source_row` and comparing outputs.

Cluster 1 has mean fuzzy Union `0.459942`, compared with `0.128029` for Cluster 0.
The greatest difference is in `compounded_academic_support_need`. R4's
attendance-based signal is somewhat stronger in Cluster 0, which is correctly
explained as a complementary rule aimed at attendance concern when performance
concern is limited.

## 7. Test and Reproducibility Evidence

- 219 automated tests pass on the merged `develop` baseline.
- Part A tests cover input validation, fuzzy boundaries, parsing, precedence,
  Knowledge Base validation, dependency resolution, cycles, inference, trace,
  aggregation, and the worked example.
- Part B tests cover preparation, scaling, clustering, K selection, outputs, and
  the full pipeline.
- Integration tests cover the 649-record join, cluster summaries, safety boundaries,
  artifact generation, and invalid assignment data.
- Executed Part B notebook: 16 executed code cells, zero execution errors, and IDs
  present for all cells at the approved checkpoint.

## 8. Required Actions Before Submission

1. Enter the real team data on the official Cover Sheet, ordered by ID.
2. Select the Student Academic Advisor checkbox.
3. Leave only attendance signatures for handwriting.
4. Confirm the TA's accepted report format, then export and visually inspect it.
5. Review the full repository from a fresh environment and confirm the documented
   run commands.
6. Merge the final approved `develop` release into `main`.
7. Prepare all members for the individual assessment.

## 9. Optional Enhancements

The following are explicitly non-blocking:

- Streamlit presentation interface and deployment.
- CI automation.
- Additional rules, predicates, datasets, or cluster experiments.

They should be attempted only after the required submission artifacts and viva
preparation are secure.

## 10. Final Audit Decision

The implemented project satisfies the technical requirements identified in the two
official PDFs. Approval is conditional only on completing the real team Cover Sheet,
exporting the report in the required submission format, final release verification,
and individual preparation. No technical redesign is recommended.
