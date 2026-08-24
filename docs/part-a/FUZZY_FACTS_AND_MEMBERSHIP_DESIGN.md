# Fuzzy Facts and Membership Function Design

Course: **Basic of AI Programming Skills (DSC 311)**

Project: **Student Academic Advisor**

Dataset: **UCI Student Performance — `student-por.csv`**

Design version: **1.0**

Status: **Approved**

Approval date: **2026-08-19**

External review result: **APPROVE — no required corrections**

## 1. Purpose and Boundary

This document proposes how one student's approved raw attributes are converted into
initial fuzzy O-A-V facts with values in `[0,1]` for Part A.

This document defines no:

- Production rules
- Intermediate or final conclusions
- Confidence factors
- Rule dependencies
- Inference results
- K-Means value of `k`
- Cluster meanings

## 2. Requirement and Decision Classification

### Official requirement

At least the key domain facts in Part A must use fuzzy values in `[0,1]` rather
than being only true or false. The official fuzzy operators remain:

- AND = minimum
- OR = maximum
- NOT = `1 - value`
- `CV = FV × CF`

### Approved implementation decision

Adopt a small raw-to-fuzzy conversion layer because the selected dataset contains
raw grades, absence counts, and ordered codes rather than membership degrees.

This conversion layer is not itself an official requirement. It is the adopted
project mechanism for producing explainable initial fuzzy facts from real dataset
records.

### Architectural consequence

The following previously optional components are now adopted project components:

- `student_academic_advisor/expert_system/raw_input.py` for one student's validated
  raw measurements
- `student_academic_advisor/expert_system/fuzzification.py` for pure
  membership-function calculations

Both remain outside the Knowledge Base and outside the Inference Engine. The
Knowledge Base continues to contain rule data only, and Working Memory continues to
contain fuzzy O-A-V facts only.

This adoption requires a small, explicit architecture revision from v3.1 to
v3.2. It must not be introduced silently.

## 3. Primary Sources and Evidence

1. `student.txt` defines the source meanings and valid codes for `G1`, `G2`,
   `absences`, `studytime`, and `failures`.
2. The [UCI Student Performance page](https://archive.ics.uci.edu/dataset/320/student%2Bperformance)
   identifies `G1`, `G2`, and `G3` as first-, second-, and final-period grades on a
   0–20 scale and warns that the three grades are strongly related.
3. The original [Cortez and Silva paper](https://repositorium.uminho.pt/bitstream/1822/8024/1/student.pdf)
   defines `G3 >= 10` as passing and gives these Portuguese grade bands:
   `0–9` fail, `10–11` sufficient, `12–13` satisfactory, `14–15` good, and
   `16–20` very good/excellent.
4. The absence breakpoints below come from the selected file's observed distribution,
   not from an invented attendance policy: median `2`, third quartile `6`, and
   90th percentile `10`.

The source paper applies the grade bands to the final grade. Applying the same
0–20 scale to `G1` and `G2` is a project implementation decision for consistent
early-period reasoning, not an official rule from the paper.

## 4. Design Principles

1. Every output must be in `[0,1]`.
2. Higher output values always mean a higher degree of academic concern.
3. One initial fuzzy predicate is created per approved raw feature.
4. Positive complements are expressed with fuzzy NOT when needed rather than stored
   as duplicate initial facts.
5. Membership functions are monotonic and simple enough to calculate by hand.
6. Valid extreme values are saturated at 0 or 1 rather than rejected.
7. Invalid raw inputs are rejected explicitly rather than silently clipped.
8. Full-precision values are used internally; rounding is for display only.

Using a single concern-oriented fact per feature keeps rule conditions readable and
avoids building an unnecessary full low/medium/high partition for every variable.
The official requirements do not demand such a partition.

## 5. Approved Raw Input Schema

One Part A run accepts one validated student record:

```text
RawStudentInput:
  object_id: str
  g1: integer
  g2: integer
  absences: integer
  studytime: integer
  failures: integer
```

Validation domains:

| Field | Accepted values | Basis |
|---|---|---|
| `g1` | Integer from 0 through 20 | Source grade scale |
| `g2` | Integer from 0 through 20 | Source grade scale |
| `absences` | Integer from 0 through 93 | Source documentation |
| `studytime` | One of `1, 2, 3, 4` | Source ordered categories |
| `failures` | One of `0, 1, 2, 3` | Codes observed in the approved selected file |

The selected Portuguese file currently has maximum grades of 19 and a maximum
absence count of 32. Validation uses the documented source domains where they are
clear so that valid source-scale values are not incorrectly rejected.

The `failures` description is ambiguous, while the selected file consistently uses
0–3. The project therefore validates the observed codes and must not invent a value
4 or silently reinterpret a code.

## 6. Approved Initial Fuzzy Facts

| Raw field | Fuzzy fact attribute | Meaning of value `1` | Meaning of value `0` |
|---|---|---|---|
| `g1` | `low_first_period_performance` | Full first-period performance concern | No low-performance concern from G1 |
| `g2` | `low_second_period_performance` | Full second-period performance concern | No low-performance concern from G2 |
| `absences` | `high_absence` | Full attendance concern | No high-absence concern |
| `studytime` | `low_study_time` | Full low-study-time concern | No low-study-time concern |
| `failures` | `high_failure_history` | Full previous-failure concern | No previous-failure concern |

Each output becomes a Working Memory fact:

```text
Fact:
  object_id: RawStudentInput.object_id
  attribute: fuzzy fact attribute
  value: calculated membership degree
  origin: INITIAL
```

Raw values never enter the rule condition language directly. The Inference Engine
reads only the resulting fuzzy Working Memory facts.

## 7. Membership Functions

### 7.1 Low first-period performance

Input: `g1` on the documented 0–20 scale.

```text
low_first_period_performance(g1) =
  1                         when g1 <= 9
  (12 - g1) / 3             when 9 < g1 < 12
  0                         when g1 >= 12
```

Key values:

| `g1` | Membership |
|---:|---:|
| 9 or below | 1.000 |
| 10 | 0.667 |
| 11 | 0.333 |
| 12 or above | 0.000 |

Reasoning: 0–9 is the source paper's fail band, 10–11 is the sufficient band,
and 12 begins the satisfactory band. The transition preserves concern for a barely
passing student without treating the pass boundary as a hard Boolean cutoff.

### 7.2 Low second-period performance

Input: `g2` on the documented 0–20 scale.

```text
low_second_period_performance(g2) =
  1                         when g2 <= 9
  (12 - g2) / 3             when 9 < g2 < 12
  0                         when g2 >= 12
```

The formula and justification match G1 so that equal grades have equal membership
meaning across periods. The two facts remain separate so later rules may reason
about persistent, improving, or emerging concern without storing an unexplained
combined grade.

### 7.3 High absence

Input: `absences` as the documented absence count.

```text
high_absence(absences) =
  0                         when absences <= 2
  (absences - 2) / 8        when 2 < absences < 10
  1                         when absences >= 10
```

Key values:

| `absences` | Membership |
|---:|---:|
| 0–2 | 0.000 |
| 4 | 0.250 |
| 6 | 0.500 |
| 8 | 0.750 |
| 10 or more | 1.000 |

Reasoning: `2` is the selected dataset median, `6` is its third quartile, and `10`
is its 90th percentile. These are empirical concern anchors, not school attendance
policy limits. A later dataset change would require re-reviewing these breakpoints.

### 7.4 Low study time

Input: `studytime`, whose documented meanings are:

- `1`: less than 2 hours per week
- `2`: 2–5 hours per week
- `3`: 5–10 hours per week
- `4`: more than 10 hours per week

Because these are four discrete, unequal-width categories, use an explicit lookup
rather than pretending the values are exact hours:

| `studytime` | `low_study_time` |
|---:|---:|
| 1 | 1.000 |
| 2 | 0.500 |
| 3 | 0.000 |
| 4 | 0.000 |

Reasoning: less than two hours is full low-study-time concern, 2–5 hours is partial
concern, and categories starting at five hours are not members of the low-study-time
predicate. This does not claim that more study time always produces better outcomes.

Because categories 3 and 4 both map to zero, this single predicate deliberately
cannot distinguish adequate study time from very high study time. If a future rule
needs that distinction, it requires a separately justified predicate and design
review rather than an unrecorded change to this mapping.

### 7.5 High failure history

Input: `failures` using the selected file's observed codes `0–3`.

```text
high_failure_history(failures) = failures / 3
```

| `failures` | Membership |
|---:|---:|
| 0 | 0.000 |
| 1 | 0.333 |
| 2 | 0.667 |
| 3 | 1.000 |

Reasoning: the mapping is monotonic, transparent, and uses the full observed code
range. It does not invent a pass/fail threshold or delete the rare non-zero values.

## 8. Coverage Check on All 649 Selected Records

The approved functions were applied to the full selected file only to validate
their output coverage. This is not an inference run and produces no project result.

| Fuzzy fact | Value `0` | Partial value | Value `1` |
|---|---:|---:|---:|
| `low_first_period_performance` | 306 | 186 | 157 |
| `low_second_period_performance` | 318 | 186 | 145 |
| `high_absence` | 366 | 213 | 70 |
| `low_study_time` | 132 | 305 | 212 |
| `high_failure_history` | 549 | 86 | 14 |

The functions produce genuine partial memberships for every core concept across the
dataset. The rare failure-history values remain useful and are not treated as errors.

## 9. Worked Fuzzification Example

The last record in the approved Portuguese file, referenced here as `POR-0649`, has:

```text
G1 = 10
G2 = 11
absences = 4
studytime = 1
failures = 0
```

Calculations:

```text
low_first_period_performance = (12 - 10) / 3 = 0.666666...
low_second_period_performance = (12 - 11) / 3 = 0.333333...
high_absence = (4 - 2) / 8 = 0.25
low_study_time = lookup(1) = 1.0
high_failure_history = 0 / 3 = 0.0
```

Initial Working Memory facts, displayed to three decimal places:

```text
(POR-0649, low_first_period_performance, 0.667)
(POR-0649, low_second_period_performance, 0.333)
(POR-0649, high_absence, 0.250)
(POR-0649, low_study_time, 1.000)
(POR-0649, high_failure_history, 0.000)
```

Internally, values are not rounded before rule evaluation. This example stops at
initial facts; it does not claim that any rule fired or any conclusion was reached.

## 10. Validation and Error Policy

Before fuzzification:

1. Require all five raw fields.
2. Require the expected integer type.
3. Reject values outside the documented or approved discrete domain.
4. Report the field name, received value, and accepted domain.
5. Do not clamp, replace, or guess an invalid value.

After fuzzification:

1. Verify every output is finite and inside `[0,1]`.
2. Create all five initial facts, including zero-valued facts.
3. Preserve the same `object_id` for all facts in the run.
4. Do not place raw values in Working Memory.

Zero-valued initial facts are defined facts, not missing facts. This matches the
approved architecture's rule that zero-valued derived facts also remain defined for
downstream expressions such as NOT.

## 11. Separation of Responsibilities

| Component | Responsibility | Must not do |
|---|---|---|
| Raw input | Hold one student's five native-scale values | Contain fuzzy rule logic |
| Input validation | Enforce type and domain constraints | Silently repair invalid inputs |
| Fuzzification | Apply the five pure membership mappings | Evaluate production rules or assign CFs |
| Working Memory | Hold initial and derived fuzzy O-A-V facts | Hold raw measurements |
| Knowledge Base | Hold human-readable production-rule data | Contain raw conversion code |
| Inference Engine | Evaluate rules using Working Memory facts | Know grade or absence breakpoints |

The membership-function definitions are project configuration/design knowledge, but
their calculation logic remains separate from production-rule evaluation.

## 12. Connection to Part B

Part B will use the approved raw features:

`G1`, `G2`, `absences`, `studytime`, and `failures`.

It will not use the five fuzzy concern degrees as K-Means inputs. Feeding the fuzzy
values into K-Means would impose Part A's author-designed boundaries on an algorithm
that is supposed to discover groups from prepared raw-domain features.

Therefore:

- Part A consumes fuzzy versions of the five shared concepts.
- Part B consumes separately scaled raw versions of those concepts.
- The parts remain coherent at the domain level without code or data-pipeline
  coupling.
- Any later agreement between conclusions and clusters remains an observed result.

## 13. Tests Required If the Design Is Approved

These are implementation tests, not additional project requirements:

1. Every documented boundary returns the expected exact value.
2. Values immediately inside each linear interval return values strictly between
   0 and 1.
3. Invalid raw values are rejected and named in the error.
4. Every valid selected-dataset row produces exactly five initial facts.
5. Every produced fact remains in `[0,1]`.
6. `object_id` and `origin = INITIAL` are preserved.
7. Zero-valued facts are present rather than dropped.
8. The worked example reproduces the documented values without early rounding.

## 14. Explicitly Rejected Choices

- Asking the user to manually invent five membership degrees
- Treating raw grades or absence counts as if they were already fuzzy facts
- Storing raw measurements in the Knowledge Base
- Embedding grade or absence thresholds inside the Inference Engine
- Using `eval()` or rule conditions to perform raw numerical conversion
- Creating low, medium, and high fact partitions for every feature without need
- Using a hard firing threshold during fuzzification or inference
- Treating valid grade zero as missing
- Treating all non-zero failures as removable outliers
- Fuzzifying `G3` as an early advising premise
- Feeding Part A membership degrees into K-Means

## 15. Open Decisions

- Exact production-rule conditions and conclusions
- Whether any deferred context facts are later adopted
- Confidence factors and their justification
- Exact scaling method for Part B
- Outlier transformation, if any
- Candidate and final values of `k`
- Cluster meanings
- Whether the diagram is drawn manually or generated

## 16. Approval

The design is approved with no required mathematical, dataset, requirement-label,
or architecture corrections. The optional inline labeling suggestion was not
adopted because the section-level labels are already unambiguous. The absence
dataset-change warning was already present in Section 7.3 and was not duplicated.

`ARCHITECTURE_DECISIONS.md` must now be revised explicitly to v3.2 to record that
raw input and fuzzification have moved from optional/deferred to adopted
implementation components. No other v3.1 architecture decision changes.
