# Part A Worked Fuzzy-Inference Example

Course: **Basic of AI Programming Skills (DSC 311)**
Project: **Student Academic Advisor**
Student: **POR-0649**

> All values below are rendered from the validated input, the loaded Knowledge Base, and the live inference trace. Calculations retain full precision internally and are rounded only for display.

## 1. Raw Input

| Field | Value |
|---|---:|
| G1 | 10 |
| G2 | 11 |
| Absences | 4 |
| Study time code | 1 |
| Previous failures | 0 |

## 2. Initial O-A-V Fuzzy Facts

| Object | Attribute | Value | Origin |
|---|---|---:|---|
| POR-0649 | `low_first_period_performance` | 0.666667 | INITIAL |
| POR-0649 | `low_second_period_performance` | 0.333333 | INITIAL |
| POR-0649 | `high_absence` | 0.25 | INITIAL |
| POR-0649 | `low_study_time` | 1 | INITIAL |
| POR-0649 | `high_failure_history` | 0 | INITIAL |

## 3. Structural Dependency Resolution

- Rule edges: R1 → R3, R2 → R3, R3 → R6.
- Deterministic evaluation order: **R1 → R2 → R3 → R4 → R5 → R6**.
- Intermediate Conclusions: `engagement_concern`, `persistent_low_performance`, `core_academic_risk`.
- Final Conclusions: `attendance_based_support_need`, `emerging_performance_support_need`, `compounded_academic_support_need`.

## 4. Live Rule Trace Summary

A rule is evaluated when its premises are available, fired when `FV > 0`, and contributes when `CV > 0`. No configurable firing threshold is used.

| Order | Rule | Premise values | FV | CF | CV | Fired | Contributes | Derived conclusion |
|---:|---|---|---:|---:|---:|---|---|---|
| 1 | R1 | `high_absence` = 0.25, `low_study_time` = 1 | 1 | 0.7 | 0.7 | Yes | Yes | `engagement_concern` = 0.7 |
| 2 | R2 | `low_first_period_performance` = 0.666667, `low_second_period_performance` = 0.333333 | 0.333333 | 0.9 | 0.3 | Yes | Yes | `persistent_low_performance` = 0.3 |
| 3 | R3 | `persistent_low_performance` = 0.3, `high_failure_history` = 0, `engagement_concern` = 0.7 | 0.3 | 0.85 | 0.255 | Yes | Yes | `core_academic_risk` = 0.255 |
| 4 | R4 | `high_absence` = 0.25, `low_first_period_performance` = 0.666667, `low_second_period_performance` = 0.333333 | 0.25 | 0.6 | 0.15 | Yes | Yes | `attendance_based_support_need` = 0.15 |
| 5 | R5 | `low_second_period_performance` = 0.333333, `low_first_period_performance` = 0.666667 | 0.333333 | 0.65 | 0.216667 | Yes | Yes | `emerging_performance_support_need` = 0.216667 |
| 6 | R6 | `core_academic_risk` = 0.255, `high_failure_history` = 0, `low_study_time` = 1 | 0.255 | 0.9 | 0.2295 | Yes | Yes | `compounded_academic_support_need` = 0.2295 |

## 5. Detailed FV, CF, and CV Calculations

### Step 1 — R1

- Description: Either weak attendance or weak study effort contributes an engagement-related support signal.
- Condition: `high_absence OR low_study_time`
- Premises: `high_absence` = 0.25, `low_study_time` = 1
- Operator calculations:
1. `OR(0.25, 1) = 1`
- Activation degree / FV: `1`
- Author-assigned CF: `0.7`
- CV: `FV × CF = 1 × 0.7 = 0.7`
- Evaluated: **Yes**; Fired: **Yes**; Contributes: **Yes**.
- Conclusion: `engagement_concern` = `0.7`.

### Step 2 — R2

- Description: Two sequential academic periods supporting low-performance concern indicate persistence across periods.
- Condition: `low_first_period_performance AND low_second_period_performance`
- Premises: `low_first_period_performance` = 0.666667, `low_second_period_performance` = 0.333333
- Operator calculations:
1. `AND(0.666667, 0.333333) = 0.333333`
- Activation degree / FV: `0.333333`
- Author-assigned CF: `0.9`
- CV: `FV × CF = 0.333333 × 0.9 = 0.3`
- Evaluated: **Yes**; Fired: **Yes**; Contributes: **Yes**.
- Conclusion: `persistent_low_performance` = `0.3`.

### Step 3 — R3

- Description: Persistent low performance is corroborated by failure history or an engagement-related concern.
- Condition: `persistent_low_performance AND (high_failure_history OR engagement_concern)`
- Premises: `persistent_low_performance` = 0.3, `high_failure_history` = 0, `engagement_concern` = 0.7
- Operator calculations:
1. `OR(0, 0.7) = 0.7`
2. `AND(0.3, 0.7) = 0.3`
- Activation degree / FV: `0.3`
- Author-assigned CF: `0.85`
- CV: `FV × CF = 0.3 × 0.85 = 0.255`
- Evaluated: **Yes**; Fired: **Yes**; Contributes: **Yes**.
- Conclusion: `core_academic_risk` = `0.255`.

### Step 4 — R4

- Description: Attendance-based support need when grade-concern membership is limited.
- Condition: `high_absence AND NOT (low_first_period_performance OR low_second_period_performance)`
- Premises: `high_absence` = 0.25, `low_first_period_performance` = 0.666667, `low_second_period_performance` = 0.333333
- Operator calculations:
1. `OR(0.666667, 0.333333) = 0.666667`
2. `NOT(0.666667) = 0.333333`
3. `AND(0.25, 0.333333) = 0.25`
- Activation degree / FV: `0.25`
- Author-assigned CF: `0.6`
- CV: `FV × CF = 0.25 × 0.6 = 0.15`
- Evaluated: **Yes**; Fired: **Yes**; Contributes: **Yes**.
- Conclusion: `attendance_based_support_need` = `0.15`.

### Step 5 — R5

- Description: A degree of support need associated with second-period concern when first-period concern is limited.
- Condition: `low_second_period_performance AND NOT low_first_period_performance`
- Premises: `low_second_period_performance` = 0.333333, `low_first_period_performance` = 0.666667
- Operator calculations:
1. `NOT(0.666667) = 0.333333`
2. `AND(0.333333, 0.333333) = 0.333333`
- Activation degree / FV: `0.333333`
- Author-assigned CF: `0.65`
- CV: `FV × CF = 0.333333 × 0.65 = 0.216667`
- Evaluated: **Yes**; Fired: **Yes**; Contributes: **Yes**.
- Conclusion: `emerging_performance_support_need` = `0.216667`.

### Step 6 — R6

- Description: Compounded academic-support need from core risk or combined failure-history and study-time concerns.
- Condition: `core_academic_risk OR (high_failure_history AND low_study_time)`
- Premises: `core_academic_risk` = 0.255, `high_failure_history` = 0, `low_study_time` = 1
- Operator calculations:
1. `AND(0, 1) = 0`
2. `OR(0.255, 0) = 0.255`
- Activation degree / FV: `0.255`
- Author-assigned CF: `0.9`
- CV: `FV × CF = 0.255 × 0.9 = 0.2295`
- Evaluated: **Yes**; Fired: **Yes**; Contributes: **Yes**.
- Conclusion: `compounded_academic_support_need` = `0.2295`.

## 6. Final Conclusions

| Final conclusion | CV |
|---|---:|
| `attendance_based_support_need` | 0.15 |
| `emerging_performance_support_need` | 0.216667 |
| `compounded_academic_support_need` | 0.2295 |

## 7. Final Knowledge Base Aggregation

- Maximum: `max(0.15, 0.216667, 0.2295) = 0.2295`
- Fuzzy Union uses `U(a, b) = a + b - a × b`:
  1. Start with `0.15`.
  2. `U(0.15, 0.216667) = 0.334167`
  3. `U(0.334167, 0.2295) = 0.486975`
- Final Union: `0.486975`

## 8. Interpretation

The strongest Final Conclusion is the conclusion whose CV equals the Maximum aggregation result. The Union value summarizes the combined support across all structurally Final Conclusions; it is not a replacement for their individual meanings.
