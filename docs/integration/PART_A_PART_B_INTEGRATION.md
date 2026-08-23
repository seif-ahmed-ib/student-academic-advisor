# Part A / Part B Integration Analysis

Course: **Basic of AI Programming Skills (DSC 311)**

Project: **Student Academic Advisor**

Status: **Proposed for approval**

## 1. Purpose and Requirement Boundary

The official Part B interpretation requirement asks that the Machine Learning results be connected back to the project domain. This analysis compares the independently completed Part A Expert System and Part B K-Means results after both systems have run.

The comparison is an **Implementation Decision**. Part A conclusions were not used as K-Means training features, K-Means clusters were not used as Expert System facts, and cluster labels are not treated as ground truth.

## 2. Method

1. Load the same 649 cleaned UCI `student-por.csv` records.
2. Load the approved K=2 cluster assignments produced by Part B.
3. Convert each record's G1, G2, absences, studytime, and failures values into the five approved fuzzy facts.
4. Run the validated Part A forward-chaining engine for every student.
5. Join both independent outputs by the original `source_row`.
6. Compare cluster-level mean CVs, contribution rates, Maximum, and fuzzy Union.
7. Use G3 only as a post-hoc descriptive check, never as an input.

A conclusion contributes exactly when `CV > 0`, following the approved inference convention. No configurable or arbitrary threshold is introduced.

## 3. Cluster and Expert-System Summary

| Cluster | Observed profile | Students | G3 mean (post-hoc) | Maximum mean | Union mean |
|---:|---|---:|---:|---:|---:|
| 0 | `stronger_academic_profile` | 332 | 14.033133 | 0.118409 | 0.128029 |
| 1 | `higher_academic_support_need_profile` | 317 | 9.678233 | 0.386468 | 0.459942 |

## 4. Final-Conclusion Mean CVs

| Cluster | Attendance-based | Emerging performance | Compounded academic |
|---:|---:|---:|---:|
| 0 | 0.091114 | 0.029367 | 0.011928 |
| 1 | 0.060489 | 0.11551 | 0.330542 |

## 5. Contribution Rates

Contribution rate is the fraction of students in a cluster for whom that Final Conclusion has `CV > 0`.

| Cluster | Attendance-based | Emerging performance | Compounded academic |
|---:|---:|---:|---:|
| 0 | 31.33% | 12.35% | 4.82% |
| 1 | 23.97% | 42.90% | 86.12% |

## 6. Main Findings

- Cluster 1 (`higher_academic_support_need_profile`) has mean Maximum 0.386468 and mean Union 0.459942.
- Cluster 0 (`stronger_academic_profile`) has mean Maximum 0.118409 and mean Union 0.128029.
- The higher-support cluster's mean Union is 3.59 times the other cluster's mean Union.
- The largest separation appears in `compounded_academic_support_need`, showing that Part A's chained risk path is concentrated in the population profile that Part B describes as needing greater academic support.
- `attendance_based_support_need` does not follow the same pattern. R4 specifically combines high absence with NOT low performance, so it can identify attendance concern among otherwise stronger academic records. This is a complementary rule-based insight, not a contradiction.

## 7. Post-Hoc G3 Check

- Pearson correlation between G3 and Maximum: `-0.536862`.
- Pearson correlation between G3 and Union: `-0.536041`.

The negative correlations indicate that stronger Part A support signals tend to accompany lower final grades. This is descriptive evidence only. G3 was excluded from Part A premises and K-Means training and is not used to claim predictive accuracy.

## 8. How the Two Parts Form One Advisor

- Part A advises at the individual-student level using explicit, explainable rules and a complete inference trace.
- Part B discovers population-level student profiles without receiving expert labels.
- The post-hoc comparison shows broad agreement for compounded academic need while also revealing a targeted attendance pattern that clustering alone does not express as a rule.

Together, the two parts provide complementary individual reasoning and population pattern discovery within one Student Academic Advisor domain.

## 9. Limitations

- K-Means clusters are descriptive groups, not validated risk labels.
- The Expert System membership functions and CFs are documented project decisions, not learned parameters.
- Both parts use related student features, so association is expected; the comparison does not prove causality.
- Pearson correlations are post-hoc descriptive statistics and must not be presented as classification performance.

## 10. Reproducible Artifacts

- `outputs/integration/student_level_comparison.csv`
- `outputs/integration/cluster_expert_summary.csv`
- `outputs/integration/summary.json`
- `outputs/integration/mean_conclusion_cv_by_cluster.png`
