# Feature Selection Decisions

Course: **Basic of AI Programming Skills (DSC 311)**

Project: **Student Academic Advisor**

Dataset: **UCI Student Performance — `student-por.csv`**

Decision version: **1.1**

Status: **Approved**

Approval date: **2026-08-19**

## 1. Purpose and Boundary

This document proposes which raw dataset attributes should support Part A and
Part B. The proposal is based on the approved dataset audit and observed values in
`student-por.csv`.

This document does not define:

- Fuzzy predicates or membership-function boundaries
- Production-rule content or confidence factors
- A final scaling method
- Candidate or final values of `k`
- Cluster labels or meanings
- Machine-learning results

## 2. Selection Principles

The proposed features should:

1. Represent academic performance, engagement, effort, and prior difficulty.
2. Be understandable to a student and defendable in the viva.
3. Support a meaningful connection between the Expert System and K-Means.
4. Avoid allowing demographic or sensitive attributes to determine academic advice.
5. Keep the K-Means distance space small and interpretable.
6. Avoid using the final outcome as an input when it is more useful for evaluating
   and interpreting the discovered groups.

These are implementation principles. They are not additional official requirements.

## 3. Proposed Shared Core Features

The following five raw attributes are proposed as the shared conceptual feature set
for Part A and Part B:

| Feature | Dataset meaning | Part A role | Part B role | Reason |
|---|---|---|---|---|
| `G1` | First-period grade, 0–20 | Key academic input | K-Means input | Represents the student's earlier measured performance |
| `G2` | Second-period grade, 0–20 | Key academic input | K-Means input | Represents more recent performance before the final grade |
| `absences` | Number of school absences | Key engagement input | K-Means input | Represents observable attendance behavior |
| `studytime` | Ordered weekly study-time category, 1–4 | Key effort input | K-Means input | Represents an actionable study-habit factor |
| `failures` | Coded count of previous class failures, 0–3 in the file | Key history input | K-Means input | Represents accumulated academic difficulty |

The Expert System and K-Means will share the meaning of these raw attributes, but
they will not share inference or model code. Part A converts the five raw values
into the five initial facts approved in
`docs/part-a/FUZZY_FACTS_AND_MEMBERSHIP_DESIGN.md`. Part B uses a separately
prepared and scaled numerical matrix.

## 4. Evidence from the Selected Dataset

### 4.1 Observed distributions

| Feature | Observed range | Median | Relevant observation |
|---|---:|---:|---|
| `G1` | 0–19 | 11 | Approximately symmetric; one zero value |
| `G2` | 0–19 | 11 | Seven zero values; slightly left-skewed |
| `absences` | 0–32 | 2 | Right-skewed; 244 students have zero absences |
| `studytime` | 1–4 | 2 | Category 2 is most common; category 4 has 35 records |
| `failures` | 0–3 | 0 | Zero-inflated; 549 students have no recorded failures |

All five features contain valid information despite their different distributions.
No feature will be removed merely because its distribution is skewed.

### 4.2 Core-feature relationships

Observed Spearman correlations in `student-por.csv` include:

| Pair | Correlation |
|---|---:|
| `G1` and `G2` | 0.893 |
| `failures` and `G1` | -0.432 |
| `failures` and `G2` | -0.436 |
| `studytime` and `G1` | 0.271 |
| `studytime` and `G2` | 0.259 |
| `absences` and `G1` | -0.170 |
| `absences` and `G2` | -0.164 |

`G1` and `G2` are strongly related. Retaining both is deliberate because academic
performance is the main focus and the two periods preserve progression information.
However, later model review must verify that this pair does not reduce the clusters
to grade bands with no additional advising value.

## 5. Treatment of `G3`

`G3` is the final course grade and is not proposed as:

- A K-Means training feature
- A premise available to an early academic-advising rule

Instead, it is proposed as a **post-hoc interpretation attribute**. After K-Means
has formed clusters without seeing `G3`, the project may compare final-grade
distributions across clusters to help describe the discovered profiles.

Reasons:

1. `G3` is the final outcome, while an advisor should ideally act earlier.
2. `G3` is strongly related to `G1` and `G2`.
3. Including all three grades could make Euclidean distance overly dominated by
   repeated grade information.
4. Holding `G3` out gives the project a useful external descriptive variable without
   treating it as a supervised target or ground-truth cluster label.

This does not turn Part B into classification. Cluster identities remain unsupervised
and must be interpreted only after training.

## 6. Context-Only Attributes

The following attributes may be used only for descriptive checks or later,
explicitly justified advising context. They are not proposed as K-Means inputs:

| Feature | Proposed treatment | Reason |
|---|---|---|
| `school` | Post-hoc profile check | Detect whether a cluster is disproportionately associated with one source school |
| `sex` | Optional post-hoc fairness check only | Sensitive demographic attribute; should not determine advice |
| `age` | Descriptive profile only | Demographic context, not a core academic behavior |
| `schoolsup` | Deferred Part A context | Indicates support already received and may reflect prior intervention rather than underlying need |
| `famsup` | Deferred Part A context | Family support context; not a direct academic measure |
| `higher` | Deferred Part A context | May help tailor advice, but is highly imbalanced and should not drive clustering |
| `internet` | Deferred Part A context | May support resource-aware advice, but can act as a socioeconomic proxy |

Using any deferred Part A context attribute in a final rule will require a specific
domain justification during rule-base design. Its presence in this table does not
approve a rule or a conclusion.

## 7. Attributes Excluded from Core Modelling

### 7.1 Demographic, family, or socioeconomic context

Excluded from both the core Part A facts and K-Means training:

- `address`
- `famsize`
- `Pstatus`
- `Medu`
- `Fedu`
- `Mjob`
- `Fjob`
- `guardian`

These fields may describe background but are not necessary for the minimal academic
advising objective. Several are sensitive, difficult for the student to change, or
likely to make cluster interpretation demographic rather than academic.

### 7.2 School-choice and historical context

Excluded:

- `reason`
- `nursery`
- `traveltime`

`reason` and `nursery` are not direct current academic indicators. `traveltime` may
affect a student, but its four broad categories provide less direct advising value
than attendance and study time. It can be reconsidered only if later evidence shows
a genuine gap in the core feature set.

### 7.3 Existing activities and paid support

Excluded from core modelling:

- `paid`
- `activities`

`paid` is subject-specific and highly imbalanced in the Portuguese file: 610 `no`
and 39 `yes`. `activities` is broad and does not specify the intensity or academic
effect of the activity.

### 7.4 Personal, lifestyle, and health attributes

Excluded:

- `romantic`
- `famrel`
- `freetime`
- `goout`
- `Dalc`
- `Walc`
- `health`

Although some may correlate with performance, including them would broaden the
system into personal, behavioral, or health judgement that is unnecessary for the
minimal academic advisor and harder to defend responsibly.

## 8. Preprocessing Implications

### 8.1 Missing values and duplicates

The selected file has:

- No missing values
- No empty strings
- No exact duplicate rows

Therefore, the planned preprocessing must check and report these conditions but
must not invent imputation or duplicate-removal operations.

### 8.2 Encoding

The five proposed K-Means inputs are already numeric. Therefore, no nominal-category
encoding is required for the initial core feature matrix.

`studytime` is an ordered category rather than an exact number of hours. Treating its
codes as ordered numerical values is a simplifying modelling assumption that must be
stated in the report. The final scaling stage must not describe it as exact hours.

### 8.3 Scaling

Scaling is required before K-Means because the five features use different ranges
and units. The exact scaling method remains deferred until the preprocessing design
stage compares the course-taught approach with the observed skew and zero inflation.

### 8.4 Outliers and valid extremes

- `absences` has 21 observations above the standard upper IQR boundary of 15.
- `failures` is zero-inflated, so an IQR rule marks every non-zero value as unusual.
- `studytime = 4` is a valid documented category even though a mechanical IQR rule
  would flag its 35 records.
- Grade value `0` is inside the documented 0–20 range and must not automatically be
  treated as missing.

No row or valid category will be removed automatically. Any later outlier treatment
must be justified by both domain meaning and its effect on K-Means.

## 9. Part A and Part B Coherence

The approved architecture keeps the two implementations separate. Coherence will
come from the shared academic concepts:

| Shared concept | Part A | Part B |
|---|---|---|
| Current academic performance | Approved fuzzy facts derived from `G1` and `G2` | Scaled `G1` and `G2` inputs |
| Attendance/engagement | Approved `high_absence` fact derived from `absences` | Scaled `absences` input |
| Study effort | Approved `low_study_time` fact derived from `studytime` | Scaled `studytime` input |
| Prior academic difficulty | Approved `high_failure_history` fact derived from `failures` | Scaled `failures` input |
| Final outcome | Not an early premise | `G3` used only for post-hoc cluster description |

Agreement between the Expert System and a cluster profile must be reported as an
observed comparison, not forced in advance.

## 10. Decision Classification

### Official requirement context

- Apply K-Means to data from the same domain as Part A.
- Clearly source and describe the dataset.
- Handle missing values, encode categorical features, and normalize or scale numeric
  features as needed.
- Justify the number of clusters and visualize or describe the clusters.
- Interpret what the resulting clusters represent in the project domain.
- Use fuzzy values for at least key domain facts in Part A.

The official requirements do not explicitly prescribe a feature-selection method,
these exact five attributes, the use of `G3`, or the exclusion of demographic
attributes. Those are project implementation decisions proposed here. Interpreting
clusters only after observing the fitted results is also a project research-integrity
decision; the official document requires interpretation but does not state that
sequence in those exact words.

### Proposed implementation decisions

- Shared core: `G1`, `G2`, `absences`, `studytime`, and `failures`.
- Use the five core attributes as the initial K-Means input matrix.
- Keep `G3` out of K-Means training and use it only for post-hoc interpretation.
- Do not concatenate the Mathematics and Portuguese datasets.
- Do not include demographic, family, lifestyle, or health attributes in core
  academic advice or clustering.
- Require scaling, while deferring the exact scaler.
- Do not apply nominal encoding to the initial five-feature matrix.
- Do not remove valid values using an automatic IQR rule.

### Optional or deferred decisions

- Whether context fields such as `schoolsup`, `famsup`, `higher`, or `internet`
  support a specific production rule
- Whether a derived grade-trend fact is useful
- Exact scaling method
- Any justified outlier transformation
- Candidate and final values of `k`
- Cluster meanings and names

## 11. Approval

This document fixes the initial feature scope. Any later change to the five shared
core features must be discussed, justified with evidence, and recorded as a new
architecture or feature-decision version rather than changed silently.
