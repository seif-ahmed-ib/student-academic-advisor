# K-Means Implementation and Results

Course: **Basic of AI Programming Skills (DSC 311)**

Project: **Student Academic Advisor**

Status: **Approved from actual pipeline evidence**

## 1. Boundary

This document records Part B implementation decisions and observed results. The
official requirement is to implement and justify a clustering or classification
method. The dataset, features, scaling method, candidate values, selected K, and
cluster interpretations below are project implementation decisions.

## 2. Dataset and Preparation

- Source file: `student-por.csv` from the UCI Student Performance dataset.
- Observed shape: 649 rows and 33 columns.
- Exact duplicate rows observed: 0.
- Rows with missing values in the selected features or G3: 0.
- Selected training features: `G1`, `G2`, `absences`, `studytime`, `failures`.
- Scaling: `StandardScaler`, fitted only on the five training features.
- Encoding: none was required because the approved features are numeric or
  ordinal numeric fields.
- `G3` was excluded from training and used only for post-hoc interpretation.

The pipeline explicitly checks duplicates and missing values. It removes exact
duplicates and incomplete required rows while recording the number removed. No
rows are removed from the approved UCI file because both counts are zero.

## 3. K Evaluation

All candidates use `random_state=42` and `n_init=20`.

| K | Inertia | Silhouette Score |
|---:|---:|---:|
| 2 | 2302.167 | **0.2717** |
| 3 | 1848.916 | 0.2624 |
| 4 | 1563.691 | 0.2709 |
| 5 | 1330.206 | 0.2694 |
| 6 | 1175.209 | 0.2582 |
| 7 | 1067.264 | 0.2528 |
| 8 | 997.714 | 0.2469 |
| 9 | 925.246 | 0.2499 |
| 10 | 866.953 | 0.2555 |

## 4. Selected K

The final choice is **K = 2**. The Elbow curve decreases gradually rather than
showing one unambiguous sharp elbow. K=2 has the highest observed Silhouette
Score and is the most parsimonious choice. K=4 is close in Silhouette Score but
adds complexity without improving the measured separation.

The selected score of 0.2717 indicates overlapping student patterns rather than
perfectly separated natural groups. K=2 is the best relative candidate tested;
it is not a claim that all students belong to two objectively true categories.

## 5. Observed Cluster Profiles

The meanings were assigned only after fitting and inspecting the profiles.

| Profile | Students | G1 | G2 | Absences | Study time | Failures |
|---|---:|---:|---:|---:|---:|---:|
| Stronger academic profile | 332 | 13.380 | 13.593 | 2.401 | 2.286 | 0.012 |
| Higher academic support-need profile | 317 | 9.325 | 9.451 | 4.978 | 1.558 | 0.442 |

These names describe centroid patterns. They are not ground-truth class labels.

## 6. Post-Hoc G3 Check

`G3` did not participate in scaling, K selection, or training.

| Profile | Mean G3 | Median G3 |
|---|---:|---:|
| Stronger academic profile | 14.033 | 14.0 |
| Higher academic support-need profile | 9.678 | 10.0 |

The difference supports the academic relevance of the discovered profiles while
avoiding outcome leakage into the clustering model.

## 7. Connection to Part A

Part A produces explainable support conclusions for one student using authored
rules. Part B discovers population-level patterns without using those rules or
their conclusions as training inputs. The higher-support cluster shows the same
general concern directions used by Part A: lower period performance, lower study
time, more absences, and more prior failures. This is a post-hoc comparison, not
a forced code-level dependency and not proof that either output is ground truth.
