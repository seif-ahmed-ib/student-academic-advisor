# Inference Network Diagram

Course: **Basic of AI Programming Skills (DSC 311)**

Project: **Student Academic Advisor**

Status: **Approved**

## 1. Purpose

This document accompanies the Part A inference-network artifact. The network is a visual representation of the six approved production rules in `student_academic_advisor/expert_system/knowledge_base/rules.json`. It does not introduce new rules, conclusions, confidence factors, or dependencies.

## 2. Official Diagram Convention

The diagram uses the convention required by the official project description:

- A square represents an assertion or fact.
- A circle inside a square represents an Intermediate Conclusion.
- A plain circle represents a Final Conclusion.
- Gates labeled `AND`, `OR`, and `NOT` represent the fuzzy operators connecting premises.
- Directed arrows show the inference flow from premises through operators to conclusions.

The colors are presentation aids only. Node shape determines the official semantic type.

## 3. Initial Fuzzy Facts

The five square nodes are the approved initial O-A-V fuzzy facts:

1. `low_first_period_performance`
2. `low_second_period_performance`
3. `high_absence`
4. `low_study_time`
5. `high_failure_history`

Their values are degrees of membership in `[0, 1]`. The network does not display a specific student's values because the same structure is used for every valid inference run.

## 4. Rule-to-Network Mapping

| Rule | Condition represented by gates | Conclusion | Structural type | CF |
|---|---|---|---|---:|
| R1 | `high_absence OR low_study_time` | `engagement_concern` | Intermediate | 0.70 |
| R2 | `low_first_period_performance AND low_second_period_performance` | `persistent_low_performance` | Intermediate | 0.90 |
| R3 | `persistent_low_performance AND (high_failure_history OR engagement_concern)` | `core_academic_risk` | Intermediate | 0.85 |
| R4 | `high_absence AND NOT (low_first_period_performance OR low_second_period_performance)` | `attendance_based_support_need` | Final | 0.60 |
| R5 | `low_second_period_performance AND NOT low_first_period_performance` | `emerging_performance_support_need` | Final | 0.65 |
| R6 | `core_academic_risk OR (high_failure_history AND low_study_time)` | `compounded_academic_support_need` | Final | 0.90 |

## 5. Structural Classification

### Intermediate Conclusions

- `engagement_concern` is consumed by R3.
- `persistent_low_performance` is consumed by R3.
- `core_academic_risk` is consumed by R6.

### Final Conclusions

- `attendance_based_support_need`
- `emerging_performance_support_need`
- `compounded_academic_support_need`

These classifications are derived from rule dependencies. They are not manually authored labels in the Knowledge Base.

## 6. Dependency Check

The rule-to-rule dependency edges shown by the network are:

- R1 → R3 through `engagement_concern`.
- R2 → R3 through `persistent_low_performance`.
- R3 → R6 through `core_academic_risk`.

The deterministic topological evaluation order for the approved Knowledge Base is:

`R1 → R2 → R3 → R4 → R5 → R6`

Knowledge Base declaration order is used for deterministic tie-breaking between simultaneously available rules.

## 7. Nested Conditions

The diagram preserves the parentheses of every nested rule:

- R3 evaluates its inner `OR` before its outer `AND`.
- R4 evaluates the parenthesized `OR`, then `NOT`, then the outer `AND`.
- R6 evaluates its inner `AND` before its outer `OR`.

R5 also shows that `NOT` binds to `low_first_period_performance` before the `AND` operation.

## 8. Relationship to the Worked Example

The network is structural and contains no student-specific values. The generated report at `outputs/part-a/worked_example_por_0649.md` applies the same network to student `POR-0649` and records every premise value, fuzzy operator step, FV, CF, CV, intermediate contribution, Final Conclusion, and Knowledge Base aggregation result.

## 9. Artifacts

- `outputs/part-a/inference_network.svg` is the scalable report-quality diagram.
- `outputs/part-a/inference_network.png` is the raster version for presentations and document insertion.
- `docs/part-a/INFERENCE_NETWORK_DIAGRAM.md` documents the exact rule and dependency mapping.

Programmatic diagram generation is not claimed as an official requirement. The required deliverable is the final diagram artifact using the official node and gate conventions.
