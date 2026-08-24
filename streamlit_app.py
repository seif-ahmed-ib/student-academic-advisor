from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from student_academic_advisor.expert_system.fuzzification import (
    fuzzify_student,
)
from student_academic_advisor.expert_system.inference_engine import (
    run_inference,
)
from student_academic_advisor.expert_system.raw_input import RawStudentInput
from student_academic_advisor.expert_system.validation import (
    load_knowledge_base,
)
from student_academic_advisor.integration.analysis import (
    analyze_integration,
)
from student_academic_advisor.ml_pipeline.clustering import (
    evaluate_k_candidates,
    fit_final_kmeans,
    select_k_by_silhouette,
)
from student_academic_advisor.ml_pipeline.data_preparation import (
    prepare_student_data,
)
from student_academic_advisor.ml_pipeline.reporting import (
    build_cluster_profiles,
    derive_profile_labels,
)


PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH = PROJECT_ROOT / "data/raw/uci_student_performance/student-por.csv"
ASSIGNMENTS_PATH = PROJECT_ROOT / "outputs/ml/cluster_assignments.csv"
INFERENCE_NETWORK_PATH = PROJECT_ROOT / "outputs/part-a/inference_network.png"


st.set_page_config(
    page_title="Student Academic Advisor",
    page_icon="🎓",
    layout="wide",
)


def run_student_advisor(
    student_id: str,
    g1: int,
    g2: int,
    absences: int,
    studytime: int,
    failures: int,
):
    """Reuse the tested Part A pipeline for one student."""
    student = RawStudentInput(
        object_id=student_id,
        g1=g1,
        g2=g2,
        absences=absences,
        studytime=studytime,
        failures=failures,
    )

    initial_facts = fuzzify_student(student)
    rules = load_knowledge_base()
    result = run_inference(initial_facts, rules)

    return student, initial_facts, rules, result


@st.cache_data(show_spinner=False)
def run_kmeans_analysis(dataset_path: str):
    """Reuse the tested Part B pipeline for presentation."""
    prepared = prepare_student_data(dataset_path)
    metrics = evaluate_k_candidates(prepared.scaled_features)
    selected_k = select_k_by_silhouette(metrics)
    clustering = fit_final_kmeans(
        prepared.scaled_features,
        selected_k,
    )
    profile_labels = derive_profile_labels(
        clustering.centers_scaled,
    )
    profiles = build_cluster_profiles(
        prepared.cleaned_data,
        clustering.labels,
        profile_labels,
    )

    metrics_df = pd.DataFrame(
        [
            {
                "K": metric.k,
                "Inertia": metric.inertia,
                "Silhouette Score": metric.silhouette,
            }
            for metric in metrics
        ]
    )

    selected_metric = next(
        metric for metric in metrics if metric.k == selected_k
    )

    audit = {
        "Original Rows": prepared.audit.original_rows,
        "Cleaned Rows": prepared.audit.cleaned_rows,
        "Duplicate Rows Removed": prepared.audit.duplicate_rows_removed,
        "Missing Rows Removed": prepared.audit.missing_rows_removed,
    }

    return (
        metrics_df,
        profiles,
        audit,
        selected_k,
        selected_metric.silhouette,
    )


@st.cache_data(show_spinner=False)
def run_integration_analysis(
    dataset_path: str,
    assignments_path: str,
):
    """Reuse the tested Part A / Part B integration analysis."""
    result = analyze_integration(
        dataset_path,
        assignments_path,
    )

    return (
        result.cluster_summary.copy(),
        result.g3_maximum_correlation,
        result.g3_union_correlation,
        len(result.student_comparison),
    )


def plot_k_evaluation(metrics_df: pd.DataFrame):
    """Create readable K evaluation plots with exact integer K ticks."""
    k_values = metrics_df["K"].to_numpy()

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    axes[0].plot(
        k_values,
        metrics_df["Inertia"].to_numpy(),
        marker="o",
    )
    axes[0].set_title("Elbow Method / Inertia")
    axes[0].set_xlabel("Number of clusters (K)")
    axes[0].set_ylabel("Inertia")
    axes[0].set_xticks(k_values)
    axes[0].set_xlim(k_values.min() - 0.25, k_values.max() + 0.25)
    axes[0].grid(alpha=0.25)

    axes[1].plot(
        k_values,
        metrics_df["Silhouette Score"].to_numpy(),
        marker="o",
    )
    axes[1].set_title("Silhouette Score")
    axes[1].set_xlabel("Number of clusters (K)")
    axes[1].set_ylabel("Silhouette Score")
    axes[1].set_xticks(k_values)
    axes[1].set_xlim(k_values.min() - 0.25, k_values.max() + 0.25)
    axes[1].grid(alpha=0.25)

    figure.tight_layout()
    return figure


def plot_integration_mean_cvs(conclusion_df: pd.DataFrame):
    """Create a grouped bar chart for mean Final-Conclusion CVs."""
    value_columns = [
        "Attendance-based",
        "Emerging Performance",
        "Compounded Academic",
    ]
    clusters = conclusion_df["Cluster"].astype(str).tolist()
    x_positions = np.arange(len(clusters))
    width = 0.24

    figure, axis = plt.subplots(figsize=(10, 5))

    for index, column in enumerate(value_columns):
        offsets = x_positions + (index - 1) * width
        bars = axis.bar(
            offsets,
            conclusion_df[column].to_numpy(),
            width,
            label=column,
        )
        axis.bar_label(
            bars,
            fmt="%.3f",
            padding=3,
            fontsize=8,
        )

    axis.set_title("Mean Expert-System Conclusion CV by K-Means Cluster")
    axis.set_xlabel("Cluster")
    axis.set_ylabel("Mean CV")
    axis.set_xticks(x_positions, clusters)
    axis.grid(axis="y", alpha=0.25)
    axis.legend()
    figure.tight_layout()
    return figure


st.title("🎓 Student Academic Advisor")
st.caption("Explainable Fuzzy Expert System + K-Means Student Analysis")

st.info(
    "Streamlit is an optional presentation layer. It reuses the tested "
    "Part A, Part B, and integration modules; it does not duplicate the "
    "academic reasoning or clustering logic."
)

(
    overview_tab,
    advisor_tab,
    kmeans_tab,
    integration_tab,
    about_tab,
) = st.tabs(
    [
        "Project Overview",
        "Individual Student Advisor",
        "Part B — K-Means",
        "Part A / Part B Integration",
        "About / Sources / Limitations",
    ]
)


with overview_tab:
    st.header("Project Overview")

    st.markdown(
        """
        This project combines two independent AI approaches within the
        **Student Academic Advisor** domain.

        ### Part A — Fuzzy Expert System

        - Production Rules + Object-Attribute-Value facts.
        - Deterministic forward chaining.
        - Fuzzy AND / OR / NOT reasoning.
        - FV, CF, and CV calculations.
        - Explainable rule-by-rule inference trace.

        ### Part B — K-Means Clustering

        - UCI Student Performance dataset.
        - Five selected academic features.
        - StandardScaler before clustering.
        - K evaluated from 2 through 10.
        - Inertia and Silhouette analysis.
        - Final student cluster interpretation.

        ### Integration

        Part A and Part B remain independent implementations. Their outputs are
        compared **post-hoc** to show how individual rule-based support signals
        relate to population-level K-Means profiles.
        """
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dataset Records", "649")
    col2.metric("Production Rules", "6")
    col3.metric("Selected K", "2")
    col4.metric("Silhouette Score", "0.2717")

    st.subheader("Project Flow")
    st.code(
        "Raw Student Data\n"
        "   ↓\n"
        "Part A: Fuzzification → Rules → Forward Chaining → Conclusions\n"
        "   +\n"
        "Part B: Data Preparation → StandardScaler → K-Means → Profiles\n"
        "   ↓\n"
        "Post-hoc Integration and Interpretation"
    )


with advisor_tab:
    st.header("Individual Student Advisor")

    st.write(
        "Enter one student's academic information. The values are passed "
        "directly through the tested Part A pipeline."
    )

    with st.form("student_advisor_form"):
        student_id = st.text_input(
            "Student ID",
            value="POR-0649",
        )

        col1, col2 = st.columns(2)

        with col1:
            g1 = st.number_input(
                "G1 — First Period Grade",
                min_value=0,
                max_value=20,
                value=10,
                step=1,
            )

            absences = st.number_input(
                "Absences",
                min_value=0,
                max_value=93,
                value=4,
                step=1,
            )

            failures = st.selectbox(
                "Previous Failures",
                options=[0, 1, 2, 3],
                index=0,
            )

        with col2:
            g2 = st.number_input(
                "G2 — Second Period Grade",
                min_value=0,
                max_value=20,
                value=11,
                step=1,
            )

            studytime = st.selectbox(
                "Study Time Category",
                options=[1, 2, 3, 4],
                index=0,
                help=(
                    "1: <2 hours, 2: 2–5 hours, "
                    "3: 5–10 hours, 4: >10 hours"
                ),
            )

        submitted = st.form_submit_button(
            "Run Academic Advisor",
            type="primary",
        )

    if submitted:
        try:
            student, initial_facts, rules, result = run_student_advisor(
                student_id=student_id.strip() or "DEMO-001",
                g1=int(g1),
                g2=int(g2),
                absences=int(absences),
                studytime=int(studytime),
                failures=int(failures),
            )

            st.success("Inference completed successfully.")

            st.subheader("1. Raw Student Input")
            raw_df = pd.DataFrame(
                [
                    {
                        "Student ID": student.object_id,
                        "G1": student.g1,
                        "G2": student.g2,
                        "Absences": student.absences,
                        "Study Time": student.studytime,
                        "Failures": student.failures,
                    }
                ]
            )
            st.dataframe(
                raw_df,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("2. Initial Fuzzy Facts")
            fuzzy_df = pd.DataFrame(
                [
                    {
                        "Attribute": fact.attribute,
                        "Fuzzy Value": fact.value,
                        "Origin": fact.origin.value,
                    }
                    for fact in initial_facts
                ]
            )
            st.dataframe(
                fuzzy_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Fuzzy Value": st.column_config.NumberColumn(
                        format="%.6f"
                    )
                },
            )

            st.subheader("3. Rule Inference Trace")
            trace_df = pd.DataFrame(
                [
                    {
                        "Order": entry.evaluation_order,
                        "Rule": entry.rule_id,
                        "Condition": entry.condition_text,
                        "FV": entry.fv,
                        "CF": entry.cf,
                        "CV": entry.cv,
                        "Conclusion": entry.conclusion_attribute,
                        "Fired": entry.fired,
                        "Contributes": entry.contributes,
                    }
                    for entry in result.trace.entries
                ]
            )
            st.dataframe(
                trace_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "FV": st.column_config.NumberColumn(format="%.6f"),
                    "CF": st.column_config.NumberColumn(format="%.2f"),
                    "CV": st.column_config.NumberColumn(format="%.6f"),
                },
            )

            st.subheader("4. Final Conclusions")
            final_df = pd.DataFrame(
                [
                    {
                        "Conclusion": fact.attribute,
                        "CV": fact.value,
                    }
                    for fact in result.final_conclusions
                ]
            )
            st.dataframe(
                final_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "CV": st.column_config.NumberColumn(format="%.6f")
                },
            )

            metric1, metric2 = st.columns(2)
            metric1.metric(
                "Maximum Aggregation",
                f"{result.aggregation.maximum:.6f}",
            )
            metric2.metric(
                "Fuzzy Union",
                f"{result.aggregation.union:.6f}",
            )

            with st.expander("Dependency / Evaluation Order"):
                evaluation_order = [
                    rule.id
                    for rule in result.dependency_resolution.ordered_rules
                ]
                st.code(" → ".join(evaluation_order))

            st.subheader("5. Inference Network Diagram")
            if INFERENCE_NETWORK_PATH.exists():
                st.image(
                    str(INFERENCE_NETWORK_PATH),
                    caption=(
                        "Inference network: facts, intermediate conclusions, "
                        "final conclusions, and explicit logical gates."
                    ),
                    use_container_width=True,
                )
            else:
                st.warning(
                    "Inference Network Diagram was not found at "
                    f"{INFERENCE_NETWORK_PATH}."
                )

        except (TypeError, ValueError) as error:
            st.error(str(error))


with kmeans_tab:
    st.header("Part B — K-Means Clustering")

    st.write(
        "This page executes the tested Part B K-Means pipeline using the "
        "approved UCI Student Performance dataset."
    )

    try:
        (
            metrics_df,
            profiles_df,
            audit,
            selected_k,
            selected_silhouette,
        ) = run_kmeans_analysis(str(DATASET_PATH))

        st.success("K-Means analysis completed successfully.")

        st.subheader("1. Dataset and Data Preparation")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cleaned Students", audit["Cleaned Rows"])
        col2.metric("Missing Rows Removed", audit["Missing Rows Removed"])
        col3.metric(
            "Duplicate Rows Removed",
            audit["Duplicate Rows Removed"],
        )
        col4.metric("Scaling", "StandardScaler")

        st.write("Training features:")
        st.code("G1, G2, absences, studytime, failures")

        st.info(
            "Data preparation includes required-column validation, numeric "
            "conversion, duplicate checks, missing-value checks, feature "
            "selection, and StandardScaler transformation before K-Means."
        )

        st.info(
            "G3 is NOT used for K-Means training. It is reserved only for "
            "post-hoc interpretation."
        )

        audit_df = pd.DataFrame(
            [
                {
                    "Check": key,
                    "Value": value,
                }
                for key, value in audit.items()
            ]
        )
        st.dataframe(
            audit_df,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("2. K Evaluation")

        metric1, metric2 = st.columns(2)
        metric1.metric("Selected K", selected_k)
        metric2.metric(
            "Selected Silhouette Score",
            f"{selected_silhouette:.6f}",
        )

        displayed_metrics = metrics_df.copy()
        displayed_metrics["Selected"] = (
            displayed_metrics["K"] == selected_k
        )
        st.dataframe(
            displayed_metrics,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Inertia": st.column_config.NumberColumn(format="%.4f"),
                "Silhouette Score": st.column_config.NumberColumn(
                    format="%.6f"
                ),
            },
        )

        k_figure = plot_k_evaluation(metrics_df)
        st.pyplot(k_figure, use_container_width=True)
        plt.close(k_figure)

        st.caption(
            "Candidate values are exactly K = 2 through K = 10. The final K "
            "is selected using the highest observed Silhouette Score; smaller "
            "K breaks an exact tie."
        )

        st.subheader("3. Cluster Profiles")

        readable_profiles = profiles_df.copy()
        readable_profiles["profile_label"] = (
            readable_profiles["profile_label"]
            .str.replace("_", " ", regex=False)
        )
        readable_profiles = readable_profiles.rename(
            columns={
                "cluster": "Cluster",
                "profile_label": "Profile",
                "G1": "G1 Mean",
                "G2": "G2 Mean",
                "absences": "Absences Mean",
                "studytime": "Study Time Mean",
                "failures": "Failures Mean",
                "student_count": "Student Count",
                "g3_mean": "G3 Mean (Post-hoc)",
                "g3_median": "G3 Median (Post-hoc)",
            }
        )
        st.dataframe(
            readable_profiles,
            use_container_width=True,
            hide_index=True,
            column_config={
                "G1 Mean": st.column_config.NumberColumn(format="%.4f"),
                "G2 Mean": st.column_config.NumberColumn(format="%.4f"),
                "Absences Mean": st.column_config.NumberColumn(format="%.4f"),
                "Study Time Mean": st.column_config.NumberColumn(format="%.4f"),
                "Failures Mean": st.column_config.NumberColumn(format="%.4f"),
                "G3 Mean (Post-hoc)": st.column_config.NumberColumn(
                    format="%.4f"
                ),
                "G3 Median (Post-hoc)": st.column_config.NumberColumn(
                    format="%.2f"
                ),
            },
        )

        st.subheader("4. Interpretation")
        st.markdown(
            """
            - Cluster 0 is interpreted as the **stronger academic profile**.
            - Cluster 1 is interpreted as the
              **higher academic support need profile**.
            - These names are post-training descriptions, not ground-truth
              labels.
            - The moderate Silhouette Score shows meaningful but overlapping
              groups rather than perfect separation.
            """
        )

    except (OSError, TypeError, ValueError) as error:
        st.error(f"Part B could not be displayed: {error}")


with integration_tab:
    st.header("Part A / Part B Integration")

    st.write(
        "This page compares the independent outputs of the Fuzzy Expert "
        "System and K-Means after both analyses have already been completed."
    )

    st.info(
        "Part A results are NOT used to train K-Means, and K-Means clusters "
        "are NOT used as Expert System facts. The comparison is post-hoc only."
    )

    try:
        (
            integration_summary,
            g3_maximum_correlation,
            g3_union_correlation,
            compared_students,
        ) = run_integration_analysis(
            str(DATASET_PATH),
            str(ASSIGNMENTS_PATH),
        )

        st.success(
            "Part A / Part B integration analysis completed successfully."
        )

        st.subheader("1. Comparison Scope")
        col1, col2 = st.columns(2)
        col1.metric("Compared Students", compared_students)
        col2.metric("Clusters", len(integration_summary))

        st.subheader("2. Expert-System Signals by Cluster")

        summary_table = integration_summary[
            [
                "cluster",
                "profile_label",
                "student_count",
                "maximum_mean",
                "union_mean",
                "g3_mean_post_hoc",
            ]
        ].copy()
        summary_table["profile_label"] = (
            summary_table["profile_label"]
            .str.replace("_", " ", regex=False)
        )
        summary_table = summary_table.rename(
            columns={
                "cluster": "Cluster",
                "profile_label": "Profile",
                "student_count": "Students",
                "maximum_mean": "Mean Maximum",
                "union_mean": "Mean Union",
                "g3_mean_post_hoc": "G3 Mean (Post-hoc)",
            }
        )
        st.dataframe(
            summary_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Mean Maximum": st.column_config.NumberColumn(
                    format="%.6f"
                ),
                "Mean Union": st.column_config.NumberColumn(format="%.6f"),
                "G3 Mean (Post-hoc)": st.column_config.NumberColumn(
                    format="%.4f"
                ),
            },
        )

        union_by_cluster = integration_summary.set_index("cluster")[
            "union_mean"
        ]
        higher_union = float(union_by_cluster.max())
        lower_union = float(union_by_cluster.min())
        union_ratio = higher_union / lower_union

        st.metric(
            "Higher-support Cluster Mean Union / Stronger Cluster Mean Union",
            f"{union_ratio:.2f}×",
        )

        st.subheader("3. Final-Conclusion Mean CVs")

        conclusion_df = integration_summary[
            [
                "cluster",
                "attendance_based_support_need_mean_cv",
                "emerging_performance_support_need_mean_cv",
                "compounded_academic_support_need_mean_cv",
            ]
        ].copy()
        conclusion_df = conclusion_df.rename(
            columns={
                "cluster": "Cluster",
                "attendance_based_support_need_mean_cv": "Attendance-based",
                "emerging_performance_support_need_mean_cv": (
                    "Emerging Performance"
                ),
                "compounded_academic_support_need_mean_cv": (
                    "Compounded Academic"
                ),
            }
        )
        st.dataframe(
            conclusion_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Attendance-based": st.column_config.NumberColumn(
                    format="%.6f"
                ),
                "Emerging Performance": st.column_config.NumberColumn(
                    format="%.6f"
                ),
                "Compounded Academic": st.column_config.NumberColumn(
                    format="%.6f"
                ),
            },
        )

        integration_figure = plot_integration_mean_cvs(conclusion_df)
        st.pyplot(integration_figure, use_container_width=True)
        plt.close(integration_figure)

        st.subheader("4. Contribution Rates")

        contribution_numeric = integration_summary[
            [
                "cluster",
                "attendance_based_support_need_contribution_rate",
                "emerging_performance_support_need_contribution_rate",
                "compounded_academic_support_need_contribution_rate",
            ]
        ].copy()
        contribution_numeric = contribution_numeric.rename(
            columns={
                "cluster": "Cluster",
                "attendance_based_support_need_contribution_rate": (
                    "Attendance-based"
                ),
                "emerging_performance_support_need_contribution_rate": (
                    "Emerging Performance"
                ),
                "compounded_academic_support_need_contribution_rate": (
                    "Compounded Academic"
                ),
            }
        )

        contribution_display = contribution_numeric.copy()
        for column in (
            "Attendance-based",
            "Emerging Performance",
            "Compounded Academic",
        ):
            contribution_display[column] = contribution_display[column].map(
                lambda value: f"{value:.2%}"
            )

        st.dataframe(
            contribution_display,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Contribution Rate = percentage of students in a cluster for whom "
            "the Final Conclusion has CV > 0. No configurable threshold is "
            "introduced."
        )

        st.subheader("5. Post-hoc G3 Check")

        metric1, metric2 = st.columns(2)
        metric1.metric(
            "G3 vs Maximum Correlation",
            f"{g3_maximum_correlation:.6f}",
        )
        metric2.metric(
            "G3 vs Union Correlation",
            f"{g3_union_correlation:.6f}",
        )

        st.warning(
            "These correlations are descriptive only. Correlation does not "
            "prove causation, and G3 was not used as an input to Part A or "
            "K-Means training."
        )

        st.subheader("6. Interpretation")
        st.markdown(
            f"""
            - The higher-support K-Means cluster has a mean fuzzy Union about
              **{union_ratio:.2f}×** the stronger cluster's mean Union.
            - The strongest separation appears in the
              **compounded academic support** conclusion.
            - Attendance-based support follows a different pattern because its
              rule targets high absence when grade concern is limited.
            - The two AI parts therefore provide complementary views:
              individual explainable reasoning and population-level pattern
              discovery.
            """
        )

    except (OSError, TypeError, ValueError) as error:
        st.error(
            f"Integration analysis could not be displayed: {error}"
        )


with about_tab:
    st.header("About / Sources / Limitations")

    st.subheader("Project Boundary")
    st.markdown(
        """
        - **Official academic core:** Part A Fuzzy Expert System + Part B
          K-Means Clustering.
        - **Streamlit:** optional presentation enhancement only.
        - Part A and Part B remain independent implementations.
        - Integration is a post-hoc descriptive comparison.
        """
    )

    st.subheader("Dataset")
    st.markdown(
        """
        **UCI Student Performance dataset** — Portuguese-language course data.

        - Approved file: `student-por.csv`
        - Records: 649
        - Raw columns: 33
        - Training features: `G1`, `G2`, `absences`, `studytime`, `failures`
        - `G3`: post-hoc analysis only
        """
    )

    st.subheader("Important Limitations")
    st.markdown(
        """
        - K-Means clusters are **descriptive groups**, not ground-truth risk
          labels.
        - The Silhouette Score indicates overlapping clusters rather than
          perfect separation.
        - The Expert System membership functions and Confidence Factors are
          documented project decisions; they are not learned from data.
        - Correlation does not imply causation.
        - No classification accuracy, Precision, Recall, or F1-score is claimed
          for the K-Means model.
        - G3 is excluded from Part A premises and K-Means training.
        """
    )

    st.subheader("Reproducibility")
    st.code(
        "python -m pytest -q\n"
        "python -m student_academic_advisor.expert_system.demo\n"
        "python -m student_academic_advisor.ml_pipeline.run_pipeline\n"
        "python -m student_academic_advisor.integration.run_analysis\n"
        "python -m streamlit run streamlit_app.py"
    )