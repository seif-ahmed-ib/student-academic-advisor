# Student Academic Advisor - Master Requirements Checklist

Course: **Basic of AI Programming Skills (DSC 311)**
Domain: **Student Academic Advisor**
Part B choice: **K-Means Clustering**
Checklist version: **2.0**
Audit date: **2026-08-23**

## Status Legend

- `[x]` Implemented and supported by a repository artifact or test.
- `[ ]` Still requires a team, administrative, presentation, or release action.
- Items labeled **Optional** are not official project requirements.

## Binding Sources

1. `DSC-311-Group-Project-Cover-Sheets-(HNU--Summer2026).pdf`
2. `AI_Skills_Project_Description.pdf`

No Git, deployment, GUI, fixed rule count, fixed dataset, or Streamlit requirement
is inferred from these files.

## Approved Project Decisions

- [x] Domain: Student Academic Advisor.
- [x] Part A: fuzzy rule-based Expert System.
- [x] Part B: K-Means clustering.
- [x] Dataset: UCI Student Performance, primary file `student-por.csv`.
- [x] Shared concepts: `G1`, `G2`, `absences`, `studytime`, and `failures`.
- [x] Second Knowledge Representation technique: O-A-V triplets.
- [x] Inference strategy: forward chaining.
- [x] External rule storage: JSON with separate rule fields.
- [x] Final aggregation: both Maximum and fuzzy Union.
- [x] Final K-Means value: `K=2`, selected from measured evidence.
- [x] Part A and Part B connected through post-hoc domain interpretation without
  training-time coupling.

## Part A - Knowledge Representation (2 marks)

- [x] Represent facts and domain knowledge structurally.
- [x] Use two distinct techniques: Production Rules and O-A-V triplets.
- [x] Express fuzzy facts as `(object, attribute, value)`.
- [x] Keep the Knowledge Base separate from inference logic.
- [x] Store six readable Production Rules in
  `student_academic_advisor/expert_system/knowledge_base/rules.json`.
- [x] Keep rule `id`, `condition`, `conclusion`, `cf`, and `description` separate.
- [x] Parse readable conditions into an AST instead of hard-coding domain
  conclusions in engine `if/else` statements.
- [x] Keep the rule base readable by a non-programming domain expert.

## Part A - Rule Base

- [x] Provide a compact, non-trivial six-rule domain network.
- [x] Include nested/parenthesized conditions in R3, R4, and R6.
- [x] Enforce precedence `NOT > AND > OR`; parentheses override it.
- [x] Include chained dependencies R1 -> R3, R2 -> R3, and R3 -> R6.
- [x] Derive Intermediate and Final status structurally.
- [x] Intermediate Conclusions:
  `engagement_concern`, `persistent_low_performance`, and `core_academic_risk`.
- [x] Final Conclusions:
  `attendance_based_support_need`,
  `emerging_performance_support_need`, and
  `compounded_academic_support_need`.
- [x] Reject duplicate Rule IDs and duplicate conclusion producers.
- [x] Reject unknown fact references and base/derived name collisions.

## Part A - Inference Engine (1 mark)

- [x] Implement deterministic forward chaining.
- [x] Derive dependencies from parsed rule conditions.
- [x] Topologically order rules before evaluation.
- [x] Use Knowledge Base declaration order for deterministic tie-breaking.
- [x] Detect self-dependencies and circular dependency paths.
- [x] Refuse to infer when Knowledge Base validation fails.
- [x] Evaluate every rule once after its premises become available.
- [x] Propagate producing-rule CVs through Intermediate Conclusions.
- [x] Preserve zero-valued derived facts as defined facts.
- [x] Capture which rules were evaluated/fired and their exact order.

## Part A - Fuzzy Logic (2 marks)

- [x] Represent five key domain facts with membership values in `[0,1]`.
- [x] Implement `AND = minimum`.
- [x] Implement `OR = maximum`.
- [x] Implement `NOT = 1 - value`.
- [x] Calculate one FV for every evaluated rule condition.
- [x] Store one author-assigned CF in `[0,1]` for every rule.
- [x] Calculate `CV = FV * CF` without early rounding.
- [x] Define `fired` as `FV > 0` and `contributes` as `CV > 0`.
- [x] Introduce no arbitrary configurable threshold.
- [x] Aggregate structurally Final CVs with Maximum.
- [x] Aggregate structurally Final CVs with pairwise fuzzy Union.
- [x] Exclude Intermediate CVs from final Knowledge Base aggregation.

## Part A - Inference Network Diagram (1 mark)

- [x] Produce PNG and SVG inference-network artifacts.
- [x] Use squares for initial assertions/facts.
- [x] Use circles inside squares for Intermediate Conclusions.
- [x] Use plain circles for Final Conclusions.
- [x] Use labeled AND, OR, and NOT gates.
- [x] Match the exact six-rule Knowledge Base and dependency structure.
- [x] Preserve nested-condition groupings.
- [x] Provide a complete `POR-0649` worked example.
- [x] Show every premise value, operator step, FV, CF, CV, derived conclusion,
  Maximum, and Union calculation.

## Part B - Data Preparation (2 marks)

- [x] Source and describe the UCI Student Performance dataset.
- [x] Record DOI, license, selected subject file, delimiter, shape, and source
  data dictionary.
- [x] Use 649 Portuguese-course records with 33 raw columns.
- [x] Check missing values, empty strings, and exact duplicates.
- [x] Report zero missing rows and zero exact duplicate rows in the selected file.
- [x] Avoid fabricated imputation or deletion when no such cleaning is needed.
- [x] Select `G1`, `G2`, `absences`, `studytime`, and `failures`.
- [x] Explain why nominal encoding is unnecessary for the selected matrix.
- [x] State that `studytime` is an ordinal code, not exact hours.
- [x] Scale all five training features with `StandardScaler`.
- [x] Retain valid extremes instead of mechanically deleting them as outliers.
- [x] Exclude `G3` from training and reserve it for post-hoc description.

## Part B - Model Implementation (2 marks)

- [x] Implement K-Means using scikit-learn.
- [x] Fit models on the scaled five-feature matrix.
- [x] Evaluate candidate values `K=2` through `K=10`.
- [x] Use `random_state=42` and `n_init=20` for reproducibility.
- [x] Select and fit the final `K=2` model.
- [x] Produce one cluster assignment for every one of the 649 retained rows.
- [x] Save assignments, profiles, metrics, chart, and reproducibility metadata.
- [x] Provide an executable Part B Jupyter notebook with saved outputs.

## Part B - Evaluation (1 mark)

- [x] Report inertia for every candidate K.
- [x] Report Silhouette Score for every candidate K.
- [x] Include the Elbow and Silhouette visualization.
- [x] Justify K=2 using the highest observed Silhouette Score (`0.2716647`) and
  parsimony.
- [x] State that the score indicates overlapping rather than perfectly separated
  natural groups.
- [x] Interpret clusters only after fitting and inspecting original-scale profiles.
- [x] Describe Cluster 0 as the stronger academic profile (332 students).
- [x] Describe Cluster 1 as the higher academic-support-need profile (317 students).
- [x] Treat profile names as descriptive, not ground-truth labels.
- [x] Use G3 only as a post-hoc descriptive check.
- [x] Connect the observed population patterns to the Student Academic Advisor
  domain.

## Part A / Part B Coherence

- [x] Use the same five academic concepts in independently prepared forms.
- [x] Do not feed Expert System memberships or conclusions into K-Means training.
- [x] Do not feed cluster IDs into the Expert System.
- [x] Join independent outputs post-hoc by `source_row` for 649 students.
- [x] Compare cluster-level Final CVs, contribution rates, Maximum, and Union.
- [x] Report broad alignment in compounded support need.
- [x] Explain the complementary R4 attendance pattern rather than hiding it.
- [x] Avoid causality, prediction-accuracy, or ground-truth claims.

## Deliverables

- [x] Part A source code: facts, parser, Knowledge Base, dependency resolver,
  fuzzy logic, inference engine, trace, and aggregation.
- [x] Part B source code: data preparation, K-Means, evaluation, reporting, and
  reproducible pipeline entry point.
- [x] Full external Production Rule Knowledge Base.
- [x] Worked inference example with FV, CF, and CV.
- [x] Inference Network Diagram in PNG and SVG.
- [x] K-Means metrics, cluster profiles, assignments, and visualization.
- [x] Executable Part B notebook with saved outputs.
- [x] Part A / Part B integration analysis and chart.
- [x] Short written report in Markdown covering every required topic.
- [ ] Export the final report to the submission format requested by the TA and
  visually inspect the exported pages.

## Cover Sheet and Administration

- [ ] Select `Student Academic Advisor` on the official Cover Sheet.
- [ ] Insert the real team IDs in ascending order.
- [ ] Insert every full name in Arabic using typed text.
- [ ] Keep only attendance signatures handwritten.
- [ ] Confirm the final team count does not exceed six.
- [ ] Attach or submit the Cover Sheet using the TA's required procedure.

These items remain open because team identities and the submission procedure must
not be invented.

## Individual Assessment / Viva

The official Cover Sheet allocates 4 individual marks in Part A and 5 individual
marks in Part B, but does not prescribe the exact viva questions.

- [ ] Every member can explain Production Rules and O-A-V facts.
- [ ] Every member can manually evaluate nested fuzzy conditions.
- [ ] Every member can calculate FV, CF, CV, Maximum, and Union.
- [ ] Every member can explain forward chaining, topological ordering, cycles,
  Intermediate Conclusions, and the live trace.
- [ ] Every member can explain data preparation, scaling, K-Means, inertia,
  Silhouette Score, K=2, cluster profiles, and limitations.
- [ ] Every member can explain why Part A and Part B are coherent but independent.
- [ ] Conduct a final mock viva.

## Internal Git/GitHub Workflow - Not an Official Requirement

- [x] Initialize the repository and use `main`, `develop`, feature branches, and
  Pull Requests.
- [x] Keep virtual environments, caches, and temporary archives out of Git.
- [x] Commit tested milestones and retain reproducible outputs.
- [x] Maintain a clean `develop` branch after merged work.
- [ ] Complete the final audit and merge it into `develop`.
- [ ] Merge the approved release from `develop` into `main`.
- [ ] Tag the final release if the team chooses to use release tags.

## Optional Enhancements - Not Required

- [ ] Streamlit presentation interface.
- [ ] Public deployment.
- [ ] Additional automated CI workflow.
- [ ] Extra fuzzy predicates or rules beyond the approved six-rule design.
- [ ] Additional cluster experiments beyond the reported rubric evidence.

Optional items must not delay the remaining official submission and viva work.
