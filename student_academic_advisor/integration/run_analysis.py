"""Command-line entry point for the post-hoc integration analysis."""

import argparse
from pathlib import Path

from student_academic_advisor.integration.analysis import analyze_integration
from student_academic_advisor.integration.reporting import (
    save_integration_outputs,
)


DEFAULT_DATASET = Path("data/raw/uci_student_performance/student-por.csv")
DEFAULT_ASSIGNMENTS = Path("outputs/ml/cluster_assignments.csv")
DEFAULT_OUTPUT_DIRECTORY = Path("outputs/integration")
DEFAULT_REPORT = Path("docs/integration/PART_A_PART_B_INTEGRATION.md")


def run_analysis(
    dataset: str | Path = DEFAULT_DATASET,
    assignments: str | Path = DEFAULT_ASSIGNMENTS,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
    report_path: str | Path = DEFAULT_REPORT,
) -> None:
    """Run and save the complete independent-output comparison."""
    result = analyze_integration(dataset, assignments)
    save_integration_outputs(result, output_directory, report_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare Part A and Part B student-advisor outputs"
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATASET)
    parser.add_argument(
        "--assignments", type=Path, default=DEFAULT_ASSIGNMENTS
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT_DIRECTORY
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    arguments = parser.parse_args()
    run_analysis(
        dataset=arguments.data,
        assignments=arguments.assignments,
        output_directory=arguments.output,
        report_path=arguments.report,
    )
    print("Part A / Part B integration analysis completed successfully.")
    print(f"Outputs saved to {arguments.output}.")
    print(f"Report saved to {arguments.report}.")


if __name__ == "__main__":
    main()
