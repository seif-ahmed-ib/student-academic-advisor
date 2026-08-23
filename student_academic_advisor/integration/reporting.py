"""Save reproducible Part A / Part B integration artifacts."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from student_academic_advisor.integration.analysis import (
    FINAL_CONCLUSIONS,
    IntegrationResult,
)


DISPLAY_NAMES = {
    "attendance_based_support_need": "Attendance-based",
    "emerging_performance_support_need": "Emerging performance",
    "compounded_academic_support_need": "Compounded academic",
}


def _format(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def save_comparison_chart(result: IntegrationResult, path: Path) -> None:
    """Plot mean Final-Conclusion CVs for each observed cluster."""
    summary = result.cluster_summary
    x_positions = np.arange(len(FINAL_CONCLUSIONS))
    width = 0.34
    figure, axis = plt.subplots(figsize=(12, 6.75))

    for index, row in summary.iterrows():
        values = [
            row[f"{conclusion}_mean_cv"]
            for conclusion in FINAL_CONCLUSIONS
        ]
        positions = x_positions + (index - (len(summary) - 1) / 2) * width
        bars = axis.bar(
            positions,
            values,
            width,
            label=(
                f"Cluster {row['cluster']}: "
                f"{str(row['profile_label']).replace('_', ' ')}"
            ),
        )
        axis.bar_label(bars, fmt="%.3f", padding=3, fontsize=9)

    maximum_value = max(
        float(summary[f"{conclusion}_mean_cv"].max())
        for conclusion in FINAL_CONCLUSIONS
    )
    axis.set_ylim(0.0, maximum_value * 1.28 if maximum_value > 0.0 else 1.0)
    axis.set_ylabel("Mean conclusion CV")
    axis.set_xticks(
        x_positions,
        [DISPLAY_NAMES[conclusion] for conclusion in FINAL_CONCLUSIONS],
    )
    axis.set_title("Expert-system support signals within K-Means clusters")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(loc="upper left")
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def render_report(result: IntegrationResult) -> str:
    """Render measured integration findings as Markdown."""
    summary = result.cluster_summary
    higher_index = int(summary["union_mean"].idxmax())
    lower_index = int(summary["union_mean"].idxmin())
    higher = summary.loc[higher_index]
    lower = summary.loc[lower_index]
    union_ratio = higher["union_mean"] / lower["union_mean"]

    lines = [
        "# Part A / Part B Integration Analysis",
        "",
        "Course: **Basic of AI Programming Skills (DSC 311)**",
        "",
        "Project: **Student Academic Advisor**",
        "",
        "Status: **Proposed for approval**",
        "",
        "## 1. Purpose and Requirement Boundary",
        "",
        "The official Part B interpretation requirement asks that the Machine "
        "Learning results be connected back to the project domain. This "
        "analysis compares the independently completed Part A Expert System "
        "and Part B K-Means results after both systems have run.",
        "",
        "The comparison is an **Implementation Decision**. Part A conclusions "
        "were not used as K-Means training features, K-Means clusters were not "
        "used as Expert System facts, and cluster labels are not treated as "
        "ground truth.",
        "",
        "## 2. Method",
        "",
        "1. Load the same 649 cleaned UCI `student-por.csv` records.",
        "2. Load the approved K=2 cluster assignments produced by Part B.",
        "3. Convert each record's G1, G2, absences, studytime, and failures "
        "values into the five approved fuzzy facts.",
        "4. Run the validated Part A forward-chaining engine for every student.",
        "5. Join both independent outputs by the original `source_row`.",
        "6. Compare cluster-level mean CVs, contribution rates, Maximum, and "
        "fuzzy Union.",
        "7. Use G3 only as a post-hoc descriptive check, never as an input.",
        "",
        "A conclusion contributes exactly when `CV > 0`, following the "
        "approved inference convention. No configurable or arbitrary threshold "
        "is introduced.",
        "",
        "## 3. Cluster and Expert-System Summary",
        "",
        "| Cluster | Observed profile | Students | G3 mean (post-hoc) | "
        "Maximum mean | Union mean |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {int(row['cluster'])} | `{row['profile_label']}` | "
            f"{int(row['student_count'])} | "
            f"{_format(row['g3_mean_post_hoc'])} | "
            f"{_format(row['maximum_mean'])} | "
            f"{_format(row['union_mean'])} |"
        )

    lines.extend(
        [
            "",
            "## 4. Final-Conclusion Mean CVs",
            "",
            "| Cluster | Attendance-based | Emerging performance | "
            "Compounded academic |",
            "|---:|---:|---:|---:|",
        ]
    )
    for _, row in summary.iterrows():
        lines.append(
            f"| {int(row['cluster'])} | "
            f"{_format(row['attendance_based_support_need_mean_cv'])} | "
            f"{_format(row['emerging_performance_support_need_mean_cv'])} | "
            f"{_format(row['compounded_academic_support_need_mean_cv'])} |"
        )

    lines.extend(
        [
            "",
            "## 5. Contribution Rates",
            "",
            "Contribution rate is the fraction of students in a cluster for "
            "whom that Final Conclusion has `CV > 0`.",
            "",
            "| Cluster | Attendance-based | Emerging performance | "
            "Compounded academic |",
            "|---:|---:|---:|---:|",
        ]
    )
    for _, row in summary.iterrows():
        lines.append(
            f"| {int(row['cluster'])} | "
            f"{row['attendance_based_support_need_contribution_rate']:.2%} | "
            f"{row['emerging_performance_support_need_contribution_rate']:.2%} | "
            f"{row['compounded_academic_support_need_contribution_rate']:.2%} |"
        )

    lines.extend(
        [
            "",
            "## 6. Main Findings",
            "",
            f"- Cluster {int(higher['cluster'])} "
            f"(`{higher['profile_label']}`) has mean Maximum "
            f"{_format(higher['maximum_mean'])} and mean Union "
            f"{_format(higher['union_mean'])}.",
            f"- Cluster {int(lower['cluster'])} "
            f"(`{lower['profile_label']}`) has mean Maximum "
            f"{_format(lower['maximum_mean'])} and mean Union "
            f"{_format(lower['union_mean'])}.",
            f"- The higher-support cluster's mean Union is "
            f"{union_ratio:.2f} times the other cluster's mean Union.",
            "- The largest separation appears in "
            "`compounded_academic_support_need`, showing that Part A's chained "
            "risk path is concentrated in the population profile that Part B "
            "describes as needing greater academic support.",
            "- `attendance_based_support_need` does not follow the same pattern. "
            "R4 specifically combines high absence with NOT low performance, "
            "so it can identify attendance concern among otherwise stronger "
            "academic records. This is a complementary rule-based insight, not "
            "a contradiction.",
            "",
            "## 7. Post-Hoc G3 Check",
            "",
            f"- Pearson correlation between G3 and Maximum: "
            f"`{_format(result.g3_maximum_correlation)}`.",
            f"- Pearson correlation between G3 and Union: "
            f"`{_format(result.g3_union_correlation)}`.",
            "",
            "The negative correlations indicate that stronger Part A support "
            "signals tend to accompany lower final grades. This is descriptive "
            "evidence only. G3 was excluded from Part A premises and K-Means "
            "training and is not used to claim predictive accuracy.",
            "",
            "## 8. How the Two Parts Form One Advisor",
            "",
            "- Part A advises at the individual-student level using explicit, "
            "explainable rules and a complete inference trace.",
            "- Part B discovers population-level student profiles without "
            "receiving expert labels.",
            "- The post-hoc comparison shows broad agreement for compounded "
            "academic need while also revealing a targeted attendance pattern "
            "that clustering alone does not express as a rule.",
            "",
            "Together, the two parts provide complementary individual reasoning "
            "and population pattern discovery within one Student Academic "
            "Advisor domain.",
            "",
            "## 9. Limitations",
            "",
            "- K-Means clusters are descriptive groups, not validated risk labels.",
            "- The Expert System membership functions and CFs are documented "
            "project decisions, not learned parameters.",
            "- Both parts use related student features, so association is "
            "expected; the comparison does not prove causality.",
            "- Pearson correlations are post-hoc descriptive statistics and "
            "must not be presented as classification performance.",
            "",
            "## 10. Reproducible Artifacts",
            "",
            "- `outputs/integration/student_level_comparison.csv`",
            "- `outputs/integration/cluster_expert_summary.csv`",
            "- `outputs/integration/summary.json`",
            "- `outputs/integration/mean_conclusion_cv_by_cluster.png`",
            "",
        ]
    )
    return "\n".join(lines)


def save_integration_outputs(
    result: IntegrationResult,
    output_directory: str | Path,
    report_path: str | Path,
) -> None:
    """Save tables, measured summary, chart, and Markdown report."""
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    result.student_comparison.to_csv(
        output / "student_level_comparison.csv", index=False
    )
    result.cluster_summary.to_csv(
        output / "cluster_expert_summary.csv", index=False
    )
    summary = {
        "student_count": len(result.student_comparison),
        "cluster_count": len(result.cluster_summary),
        "comparison_type": "post-hoc descriptive comparison",
        "part_a_used_for_kmeans_training": False,
        "clusters_treated_as_ground_truth": False,
        "contribution_convention": "CV > 0; no configurable threshold",
        "g3_usage": "post-hoc descriptive check only",
        "g3_maximum_correlation": result.g3_maximum_correlation,
        "g3_union_correlation": result.g3_union_correlation,
    }
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    save_comparison_chart(
        result, output / "mean_conclusion_cv_by_cluster.png"
    )
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_report(result), encoding="utf-8")
