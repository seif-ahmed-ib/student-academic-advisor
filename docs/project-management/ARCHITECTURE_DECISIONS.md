# Student Academic Advisor — Architecture Decisions

Course: **Basic of AI Programming Skills (DSC 311)**
Project Domain: **Student Academic Advisor**
Architecture Version: **3.3**
Status: **Approved**
Approval Date: **2026-08-19**

## 1. Purpose

This document is the architectural Source of Truth for the Student Academic Advisor project.

It records the decisions approved after reviewing:

1. The official Project Requirements and Cover Sheet.
2. Lectures 1–8.
3. Sections 3–7, including their code.
4. External architecture proposals and their revisions.

No architectural decision should be changed silently. Any future change must document its reason, impact, and compatibility with the official requirements.

## 2. Source Precedence

If project sources conflict, use this order:

1. Official project requirements.
2. Course lectures.
3. Section code and supporting materials.
4. Outputs from external AI models.
5. Optional team improvements.

External AI output is never adopted automatically.

## 3. Requirement Classification

### 3.1 Official Requirements

- Use at least two distinct Knowledge Representation techniques.
- Production Rules must be one of the techniques.
- Keep the Knowledge Base separate from inference logic.
- Provide a substantial, non-trivial rule set.
- Include at least one nested condition.
- Respect operator precedence: `NOT`, then `AND`, then `OR`.
- Include at least one chained rule.
- Distinguish Intermediate Conclusions from Final Conclusions.
- Implement and state a chaining strategy.
- Resolve rule dependencies correctly using topological ordering.
- Detect circular dependencies.
- Explain which rules fired and in what order.
- Represent at least the key domain facts using fuzzy values in `[0,1]`.
- Implement:
  - `AND = minimum`
  - `OR = maximum`
  - `NOT = 1 - value`
  - Fuzzy Value, FV
  - Confidence Factor, CF
  - Confidence Value, `CV = FV × CF`
- Aggregate Final Conclusion CVs using Maximum and/or Union.
- Produce an Inference Network Diagram using the official symbols.
- Include a complete worked inference example showing FV, CF, and CV.
- Apply K-Means to data from the same project domain.
- Prepare, evaluate, visualize, and interpret the clustering results.
- Submit source code and a written report.

### 3.2 Approved Implementation Decisions

- Use O-A-V as the second Knowledge Representation technique.
- Use Forward Chaining.
- Store the Knowledge Base as data in `rules.json`.
- Store rule conditions as restricted, human-readable strings.
- Parse each condition once into an internal AST.
- Never use `eval()`.
- Resolve dependencies using deterministic topological ordering.
- Break topological ties using Knowledge Base declaration order.
- Run Knowledge Base and cycle validation before inference.
- Scope one inference run to one student.
- Propagate a producing rule's CV as the value of its derived conclusion.
- Derive Intermediate/Final status structurally from dependencies.
- Reject duplicate conclusion producers.
- Use no configurable firing threshold.
- Implement both Maximum and Union aggregation.
- Keep K-Means independent from the Expert System at code level.
- Connect Part A and Part B through domain features and result interpretation.
- Use the UCI Student Performance dataset and `student-por.csv` as the approved
  primary file.
- Use `G1`, `G2`, `absences`, `studytime`, and `failures` as the approved shared
  conceptual features for Part A and Part B.
- Keep `G3` out of early Part A premises and K-Means training; use it only for
  post-hoc interpretation.
- Adopt a validated raw-to-fuzzy conversion step outside the Knowledge Base and
  Inference Engine.
- Produce exactly five approved concern-oriented initial fuzzy facts from one
  student's five raw values.
- Keep Part B on separately prepared raw features rather than Part A membership
  degrees.
- Adopt `docs/part-a/RULE_BASE_AND_DEPENDENCY_DESIGN.md` version 1.1 as the
  Rule Base and dependency-design Source of Truth.
- Use the approved compact but non-trivial six-rule network, R1 through R6, in
  Knowledge Base declaration order.
- Use the three structurally Intermediate Conclusions and three structurally
  Final Conclusions defined in the approved Rule Base design.
- Use the approved author-assigned CF values and semantic rationales recorded in
  the Rule Base design.
- Interpret every Final Conclusion as a degree of academic-support need reached
  through a distinct evidence pathway, so Maximum and Union aggregate values in
  one coherent semantic direction.

### 3.3 Optional or Deferred Enhancements

The following are not part of the required initial implementation:

- Additional fuzzy predicates beyond the five approved initial facts. Any future
  addition requires a separately reviewed versioned design change.
- Automatic membership-function generation or tuning.
- Programmatic Inference Network Diagram generation.
- GUI.
- Web application or API.
- Database.
- Authentication.
- Agent framework.
- ANN.
- Deployment or Docker configuration.

Optional components may only be added after the rubric requirements are safely completed.

Raw-to-fuzzy conversion is no longer in this optional list. Architecture v3.2
adopts it as an Implementation Decision; it is still not an Official Requirement.

## 4. Knowledge Representation

### 4.1 Production Rules

Production Rules represent domain reasoning using:

```text
IF condition THEN conclusion
```

The stored rule fields are separated. The `condition` field does not contain the `IF` or `THEN` keywords.

The approved rule content, conclusion vocabulary, CF values, dependency edges,
and declaration order are defined in:

```text
docs/part-a/RULE_BASE_AND_DEPENDENCY_DESIGN.md
```

The adopted design contains six rules, R1 through R6. Its structurally derived
conclusion classes are:

- Intermediate: `engagement_concern`, `persistent_low_performance`, and
  `core_academic_risk`.
- Final: `attendance_based_support_need`,
  `emerging_performance_support_need`, and
  `compounded_academic_support_need`.

The Rule Base design document is the Source of Truth for the exact conditions,
descriptions, CF values, and dependency graph; they are not duplicated here.

### 4.2 O-A-V Facts

Facts use Object-Attribute-Value representation:

```text
(Student, fuzzy_attribute, membership_value)
```

Illustrative example only:

```text
(Student_01, low_first_period_performance, 0.80)
```

The value is a fuzzy membership degree, not a raw grade measurement.

## 5. Rule Representation

### 5.1 Human-Authored RuleSource

The Knowledge Base stores:

```text
RuleSource:
  id: string
  condition: string
  conclusion: string
  cf: float in [0,1]
  description: string
```

Example condition format:

```text
low_first_period_performance AND (high_absence OR low_study_time)
```

The Knowledge Base contains no evaluation functions, control flow, or domain-specific `if/else` code.

### 5.2 Internal LoadedRule

After loading and validation, each RuleSource becomes:

```text
LoadedRule:
  id: string
  declaration_index: integer
  condition_source: string
  condition_ast: ConditionAST
  conclusion: string
  cf: float
  description: string
```

`id` and `declaration_index` are different:

- `id` identifies the rule.
- `declaration_index` records its position in `rules.json`.

### 5.3 Condition AST

```text
ConditionNode:
  kind: FACT_REF | NOT | AND | OR
  fact_attribute: optional string
  operands: list of ConditionNode
```

Structural constraints:

- `FACT_REF` contains one fact attribute.
- `NOT` contains exactly one operand.
- `AND` and `OR` contain two or more operands.

The parser enforces:

```text
NOT > AND > OR
```

Parentheses override normal precedence.

## 6. Raw Input, Fuzzification, Facts, and Working Memory

### 6.1 RawStudentInput Schema

One Part A run begins with one validated raw student record:

```text
RawStudentInput:
  object_id: string
  g1: integer from 0 through 20
  g2: integer from 0 through 20
  absences: integer from 0 through 93
  studytime: integer in {1, 2, 3, 4}
  failures: integer in {0, 1, 2, 3}
```

Raw input is outside the Knowledge Base and Working Memory. Invalid values are
rejected with a field-specific error and are never silently clipped or guessed.

### 6.2 Approved Fuzzification Boundary

The approved raw-to-fuzzy layer converts the five raw values into exactly five
initial fuzzy facts:

| Raw value | Initial fuzzy fact |
|---|---|
| `g1` | `low_first_period_performance` |
| `g2` | `low_second_period_performance` |
| `absences` | `high_absence` |
| `studytime` | `low_study_time` |
| `failures` | `high_failure_history` |

The exact approved membership functions, breakpoints, coverage counts, and worked
example are defined in `docs/part-a/FUZZY_FACTS_AND_MEMBERSHIP_DESIGN.md`.

Fuzzification:

- Is an adopted Implementation Decision, not an Official Requirement.
- Runs outside the Knowledge Base and Inference Engine.
- Contains no Production Rules or CF values.
- Produces values in `[0,1]` without early rounding.
- Creates zero-valued initial facts rather than dropping them.

### 6.3 Fact Schema

```text
Fact:
  object_id: string
  attribute: string
  value: float in [0,1]
  origin: INITIAL | DERIVED
```

Definitions:

- `INITIAL`: produced from the approved input boundary before inference starts.
- `DERIVED`: produced by a Production Rule.
- `object_id`: identifies the student being advised.

### 6.4 Working Memory

Each inference run is scoped to one student.

Working Memory:

- Is initialized with all five fuzzy O-A-V facts after input validation and
  fuzzification.
- Grows as rules produce derived conclusions.
- Is separate from the static Knowledge Base.
- Accepts initial facts only during pre-inference initialization; after that, only
  the Inference Engine writes derived facts.
- Never mixes facts belonging to different students in one run.
- Never stores the original raw measurements.

## 7. Knowledge Base Validation

Before inference starts, validation must check:

- The Knowledge Base is not empty.
- Every Rule ID is unique.
- Every derived conclusion attribute has exactly one producer.
- Every Rule contains the required fields.
- Every CF is numeric and within `[0,1]`.
- Every condition uses valid restricted syntax.
- Parentheses are balanced.
- AST operand counts are valid.
- Every referenced attribute is either:
  - an initial/base fact, or
  - another rule's conclusion.
- A base fact name does not conflict with a derived conclusion name.
- No circular dependency exists.
- At least one Final Conclusion exists.

If validation fails, inference must not start.

## 8. Duplicate Conclusion Policy

Multiple rules must not produce the same derived attribute.

Invalid design:

```text
R1 -> academic_risk
R2 -> academic_risk
```

Correct design:

```text
R1 -> low_gpa_support
R2 -> poor_attendance_support
R3: low_gpa_support OR poor_attendance_support -> academic_risk
```

This policy:

- Prevents silent overwriting.
- Avoids inventing unsupported intermediate aggregation.
- Keeps dependencies explicit.
- Makes the trace and diagram easier to explain.

Maximum and Union are reserved for Knowledge-Base-level aggregation across Final Conclusions.

## 9. Dependency Resolution

For every rule:

1. Inspect all `FACT_REF` nodes in its AST.
2. If a referenced attribute is produced by another rule, add a dependency edge:

```text
Producer Rule -> Consumer Rule
```

The Dependency Graph is used to:

- Detect cycles.
- Produce a valid topological order.
- Classify conclusions.
- Determine inference execution order.

When several rules are ready simultaneously, their declaration order in `rules.json` breaks the tie.

If a cycle exists, the system reports the involved rules and refuses to run.

## 10. Intermediate and Final Conclusions

Conclusion status is never written manually in `rules.json`.

It is derived structurally:

- Intermediate Conclusion: consumed by at least one other rule.
- Final Conclusion: not consumed by any other rule.

The dependency graph is the Source of Truth for this classification.

## 11. Forward-Chaining Semantics

Before inference begins:

1. Load and parse the Knowledge Base.
2. Validate the Knowledge Base, build the dependency graph, and detect cycles
   before creating or touching Working Memory facts.
3. Validate the current student's `RawStudentInput`.
4. Apply the five approved membership mappings.
5. Initialize Working Memory with all five fuzzy facts, including zero-valued facts.
6. Identify all base facts required by the loaded rules.
7. Confirm that every required base fact exists for the current student.
8. Produce the deterministic topological order.

If structural validation, raw-input validation, fuzzification validation, or the
required-base-fact check fails, inference does not start and the specific errors are
reported.

During inference, every rule is evaluated exactly once in topological order.

For each rule:

1. Read its premise values from Working Memory.
2. Capture a premise snapshot.
3. Evaluate the AST and record the operator steps.
4. Compute FV.
5. Read the rule's author-assigned CF.
6. Compute:

```text
CV = FV × CF
```

7. Classify the conclusion as Intermediate or Final.
8. Write the conclusion into Working Memory as a DERIVED Fact with:

```text
Fact.value = CV
```

9. Append the RuleEvaluation to the inference trace.

The CV is written for both Intermediate and Final Conclusions.

A derived fact remains defined even when `CV = 0`. This is necessary because a downstream rule may apply `NOT` to that conclusion.

## 12. Evaluation, Firing, and Contribution

No configurable threshold such as `0.5` is used.

Definitions:

```text
evaluated = all required premise values were available
activation_degree = FV
fired = evaluated AND FV > 0
contributes = evaluated AND CV > 0
```

Important distinctions:

- Available premises mean the rule can be evaluated.
- `FV > 0` means the rule fired to a positive degree.
- `CV > 0` means the rule contributed positive support.
- A zero-CV result remains a defined derived fact.

## 13. Fuzzy Logic Calculations

### 13.1 Initial Fact Fuzzification

The raw-to-fuzzy layer applies the five approved membership mappings before
inference starts. These mappings produce initial fuzzy facts; they do not calculate
rule FV or CV and do not determine whether a rule fired.

The detailed formulas live in
`docs/part-a/FUZZY_FACTS_AND_MEMBERSHIP_DESIGN.md`. Membership-function boundaries
must not be duplicated inside the Knowledge Base or Inference Engine.

### 13.2 AND

```text
AND(a, b) = min(a, b)
```

### 13.3 OR

```text
OR(a, b) = max(a, b)
```

### 13.4 NOT

```text
NOT(a) = 1 - a
```

### 13.5 Fuzzy Value

FV is the composite fuzzy value of the complete rule condition after evaluating its AST.

### 13.6 Confidence Factor

CF is fixed, author-assigned, and constrained to `[0,1]`.

### 13.7 Confidence Value

```text
CV = FV × CF
```

For a chained rule, the producing rule's CV becomes the fuzzy value of its derived conclusion and is consumed by dependent rules.

## 14. Explainability Trace

### 14.1 OperatorStep

```text
OperatorStep:
  operator: FACT_REF | NOT | AND | OR
  fact_attribute: optional string
  inputs: list of float
  output: float
```

For `FACT_REF`, `fact_attribute` identifies the value being read.

Operator steps are recorded innermost-first.

### 14.2 RuleEvaluation

```text
RuleEvaluation:
  rule_id: string
  declaration_index: integer
  condition_text: string
  premise_snapshot: mapping of attribute to value
  operator_steps: list of OperatorStep
  fv: float
  cf: float
  cv: float
  evaluated: boolean
  fired: boolean
  contributes: boolean
  conclusion_attribute: string
  conclusion_value: float
  conclusion_status: INTERMEDIATE | FINAL
  evaluation_order: integer
```

If the rule is evaluated:

```text
conclusion_value = CV
```

The trace is captured live during inference and is not reconstructed from final Working Memory alone.

## 15. Final Conclusion Aggregation

After all rules are evaluated, collect the CVs of all structurally Final Conclusions.

### 15.1 Maximum Method

```text
CV(KB) = max(final CVs)
```

### 15.2 Union Method

For two values:

```text
U(a, b) = a + b - (a × b)
```

For more than two values, fold one value at a time in deterministic Final Conclusion order.

Both Maximum and Union will be implemented and reported.

Intermediate Conclusion CVs must not be included in Knowledge-Base-level aggregation.

## 16. Inference Network Diagram

The required artifact must use:

- Square: assertion/base fact.
- Circle inside a square: Intermediate Conclusion.
- Plain circle: Final Conclusion.
- AND, OR, and NOT gates connecting the nodes.

The diagram must:

- Represent nested conditions correctly.
- Match the approved Rule Base.
- Show chained dependencies.
- Use the official symbols exactly.

The diagram may be produced manually using a drawing tool. Programmatic generation is optional and not part of the initial implementation.

## 17. Part B — K-Means Architecture

The K-Means pipeline remains independent from the Expert System implementation.

Approved data decisions:

- Source: UCI Student Performance.
- Primary file: `student-por.csv`, containing 649 records and 33 columns.
- Do not concatenate it with `student-mat.csv` because the source documents 382
  students shared between the two files.
- Initial K-Means features: `G1`, `G2`, `absences`, `studytime`, and `failures`.
- `G3` is excluded from K-Means training and reserved for post-hoc description.
- The selected raw file contains no missing values, empty strings, or exact
  duplicate rows; these conditions are checked and reported without fabricated
  imputation or deletion.
- The five initial features are already numerical or ordinal-coded, so nominal
  encoding is not required for the initial feature matrix.
- Scaling is required, but the exact scaler remains open.
- Part B uses prepared raw feature values, never Part A membership degrees.

The pipeline will include:

1. Source-aware loading using the file's semicolon delimiter.
2. Repeatable data-quality validation.
3. Selection of the five approved features.
4. Documented treatment of valid extremes and skew.
5. Scaling appropriate to the observed data.
6. K-Means training.
7. Elbow Method.
8. Silhouette Score.
9. Cluster visualization.
10. Cluster size and centroid profiling.
11. Interpretation using original feature scales when possible.
12. Post-hoc use of `G3` without treating it as a cluster label.
13. Comparison with Part A reasoning patterns.

The following must not be assumed before training:

- The correct value of K.
- Cluster labels.
- Cluster meanings.
- Which cluster represents academic risk.

Cluster labels are not ground truth.

## 18. Part A and Part B Coherence

The two parts are connected through:

- The Student Academic Advisor domain.
- The approved shared concepts: first-period performance, second-period
  performance, absences, study time, and failure history.
- Part A fuzzy facts derived from one student's five raw values.
- Part B clustering on separately scaled raw values for the same five concepts.
- Final report interpretation.

They are not connected by:

- Feeding cluster IDs directly into the Expert System.
- Feeding Part A fuzzy membership degrees into K-Means.
- Treating a cluster as a verified risk label.
- Forcing K-Means results to agree with the Production Rules.

Agreement, partial agreement, or disagreement between the two parts are all valid findings.

## 19. Approved Minimal Folder Structure

```text
student-academic-advisor/
├── student_academic_advisor/
│   ├── expert_system/
│   │   ├── knowledge_base/
│   │   │   └── rules.json
│   │   ├── models.py
│   │   ├── raw_input.py
│   │   ├── fuzzification.py
│   │   ├── rule_parser.py
│   │   ├── validation.py
│   │   ├── fuzzy_logic.py
│   │   ├── dependency_graph.py
│   │   ├── working_memory.py
│   │   ├── inference_engine.py
│   │   ├── trace.py
│   │   └── aggregation.py
│   └── ml_pipeline/
│       ├── data_preparation.py
│       ├── clustering.py
│       └── interpretation.py
├── data/
│   └── raw/
│       └── uci_student_performance/
├── tests/
│   ├── expert_system/
│   └── ml_pipeline/
├── docs/
│   ├── project-management/
│   ├── data/
│   ├── part-a/
│   ├── diagrams/
│   └── report/
├── run_demo.py
├── README.md
└── requirements.txt
```

`raw_input.py` validates `RawStudentInput`. `fuzzification.py` owns the five
membership mappings and creates the initial fuzzy Facts. Neither module contains
Production Rules, CF values, dependency logic, or inference control flow.

## 20. Required Test Coverage

Part A tests must cover:

- Raw input required fields, types, and accepted domains.
- All approved membership-function boundaries and partial values.
- Fuzzification outputs across all 649 selected records remain in `[0,1]`.
- Exactly five initial facts are produced for each valid input.
- Zero-valued initial facts remain present.
- The documented `POR-0649` fuzzification example.
- Rule parsing.
- Operator precedence.
- Nested conditions.
- Invalid syntax.
- Unbalanced parentheses.
- Fuzzy AND, OR, and NOT.
- FV, CF, and CV validation.
- Duplicate Rule IDs.
- Duplicate conclusion producers.
- Undefined fact references.
- Base/derived name collisions.
- Cycle detection.
- Deterministic topological ordering.
- Missing initial facts.
- CV propagation through chained rules.
- Zero-CV derived facts.
- Intermediate/Final classification.
- Maximum aggregation.
- Union aggregation.
- Trace completeness.
- Complete end-to-end inference.

Part B tests must already cover:

- Correct semicolon-delimited loading of `student-por.csv`.
- Expected raw shape of 649 rows and 33 columns.
- Missing-value and exact-duplicate checks.
- Exact selection and order of the five approved K-Means features.
- Exclusion of `G3` from the K-Means input matrix.

Additional Part B tests will be finalized after the scaling and outlier-treatment
decisions are approved.

## 21. Remaining Open Decisions

The following remain open:

- Final human-readable output wording that presents the three approved
  academic-support conclusions to the user without changing their rule semantics.
- Scaling method for the five K-Means inputs.
- Outlier transformation, if any.
- Candidate and final values of K.
- Cluster visualizations.
- Cluster interpretations.
- Final Part A/Part B empirical comparison method.
- Manual or programmatic production of the required Inference Network Diagram.

The dataset, source, primary file, five shared features, five initial fuzzy facts,
membership functions, raw-to-fuzzy adoption, missing-value result, initial
encoding decision, six-rule content, conclusion vocabulary, dependency graph, and
CF values are approved and are no longer open.

## 22. Rejected Architecture Choices

The following must not be reintroduced without an approved architecture change:

- Hard-coded domain conclusions inside the Inference Engine.
- General-purpose `if/else` as the Knowledge Base.
- `eval()` for condition evaluation.
- Manually authored `conclusion_type`.
- Alphabetical Rule-ID tie-breaking.
- Configurable firing threshold.
- Silent duplicate-producer overwriting.
- Automatic duplicate-producer aggregation.
- Including Intermediate CVs in final KB aggregation.
- Labeling raw-to-fuzzy conversion as an Official Requirement.
- Asking users to invent fuzzy membership degrees manually.
- Placing membership breakpoints in the Knowledge Base or Inference Engine.
- Feeding Part A fuzzy membership degrees into K-Means.
- Mandatory programmatic diagram generation.
- Raw Input inside the Knowledge Base.
- Raw measurements inside Working Memory.
- Working Memory inside the Knowledge Base.
- Silent changes to the approved dataset, primary file, or five-feature scope.
- Premature K or cluster-label assumptions.
- GUI, API, database, agents, ANN, or deployment complexity.

## 23. Approval

Architecture v3.3 is approved as the implementation baseline.

Version 3.3 adopts the approved Rule Base and Dependency Design v1.1, closes the
previously open decisions for rule content, rule count, derived-conclusion names,
dependency structure, and author-assigned CF values, and leaves the v3.2 runtime,
fuzzification, inference, trace, aggregation, Part B, and separation decisions
unchanged.

No project code has been written at this stage.

Any future architectural change must be discussed and approved before implementation.
