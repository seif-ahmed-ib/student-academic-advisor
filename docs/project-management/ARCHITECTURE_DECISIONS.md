# Student Academic Advisor — Architecture Decisions

Course: **Basic of AI Programming Skills (DSC 311)**
Project Domain: **Student Academic Advisor**
Architecture Version: **3.1**
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

### 3.3 Optional or Deferred Enhancements

The following are not part of the required initial implementation:

- Raw-to-fuzzy conversion layer.
- Membership-function generation from raw measurements.
- Programmatic Inference Network Diagram generation.
- GUI.
- Web application or API.
- Database.
- Authentication.
- Agent framework.
- ANN.
- Deployment or Docker configuration.

Optional components may only be added after the rubric requirements are safely completed.

## 4. Knowledge Representation

### 4.1 Production Rules

Production Rules represent domain reasoning using:

```text
IF condition THEN conclusion
```

The stored rule fields are separated. The `condition` field does not contain the `IF` or `THEN` keywords.

### 4.2 O-A-V Facts

Facts use Object-Attribute-Value representation:

```text
(Student, fuzzy_attribute, membership_value)
```

Illustrative example only:

```text
(Student_01, low_gpa, 0.80)
```

The value is a fuzzy membership degree, not a raw GPA measurement.

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
gpa_low AND (attendance_poor OR workload_high)
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

## 6. Fact and Working Memory Design

### 6.1 Fact Schema

```text
Fact:
  object_id: string
  attribute: string
  value: float in [0,1]
  origin: INITIAL | DERIVED
```

Definitions:

- `INITIAL`: present when the inference run starts.
- `DERIVED`: produced by a Production Rule.
- `object_id`: identifies the student being advised.

### 6.2 Working Memory

Each inference run is scoped to one student.

Working Memory:

- Starts with the student's initial fuzzy O-A-V facts.
- Grows as rules produce derived conclusions.
- Is separate from the static Knowledge Base.
- Can only be modified by the Inference Engine.
- Never mixes facts belonging to different students in one run.

Raw measurements, if introduced later, remain outside the Knowledge Base and Working Memory until converted into valid fuzzy facts.

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

1. Validate the Knowledge Base.
2. Identify all required base facts.
3. Confirm that every required base fact exists for the current student.
4. Build the dependency graph.
5. Produce the deterministic topological order.

If a required base fact is missing, inference does not start and the missing attributes are reported.

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

### 13.1 AND

```text
AND(a, b) = min(a, b)
```

### 13.2 OR

```text
OR(a, b) = max(a, b)
```

### 13.3 NOT

```text
NOT(a) = 1 - a
```

### 13.4 Fuzzy Value

FV is the composite fuzzy value of the complete rule condition after evaluating its AST.

### 13.5 Confidence Factor

CF is fixed, author-assigned, and constrained to `[0,1]`.

### 13.6 Confidence Value

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

It will include:

1. Dataset selection and source documentation.
2. Data understanding.
3. Data cleaning.
4. Missing-value handling.
5. Categorical encoding when required.
6. Feature selection.
7. Scaling appropriate to the real data.
8. K-Means training.
9. Elbow Method.
10. Silhouette Score.
11. Cluster visualization.
12. Cluster size and centroid profiling.
13. Interpretation using original feature scales when possible.
14. Comparison with Part A reasoning patterns.

The following must not be assumed before training:

- The correct value of K.
- Cluster labels.
- Cluster meanings.
- Which cluster represents academic risk.

Cluster labels are not ground truth.

## 18. Part A and Part B Coherence

The two parts are connected through:

- The Student Academic Advisor domain.
- Similar conceptual student-performance features when supported by the dataset.
- Final report interpretation.

They are not connected by:

- Feeding cluster IDs directly into the Expert System.
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
├── tests/
│   ├── expert_system/
│   └── ml_pipeline/
├── docs/
│   ├── project-management/
│   ├── diagrams/
│   └── report/
├── run_demo.py
├── README.md
└── requirements.txt
```

No raw-input or fuzzification module is included at this stage.

## 20. Required Test Coverage

Part A tests must cover:

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

Part B tests will be defined after selecting the dataset and final preprocessing pipeline.

## 21. Remaining Open Decisions

The following remain open until dataset research and real data analysis:

- Final dataset.
- Dataset source and license.
- Available columns.
- Part A fuzzy predicates.
- Whether raw-to-fuzzy conversion is needed.
- Membership-function shapes and breakpoints, if adopted.
- Missing-value strategy.
- Encoding strategy.
- Scaling method.
- Outlier handling.
- K-Means feature set.
- Final K.
- Cluster interpretations.
- Rule Base content.
- Number of Production Rules.
- Conclusion names.
- CF values and their justification.
- Final academic recommendations.
- Final Part A/Part B comparison method.

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
- Mandatory raw-to-fuzzy conversion.
- Mandatory programmatic diagram generation.
- Raw Input inside the Knowledge Base.
- Working Memory inside the Knowledge Base.
- Premature Dataset, K, or cluster-label assumptions.
- GUI, API, database, agents, ANN, or deployment complexity.

## 23. Approval

Architecture v3.1 is approved as the implementation baseline.

No project code has been written at this stage.

Any future architectural change must be discussed and approved before implementation.