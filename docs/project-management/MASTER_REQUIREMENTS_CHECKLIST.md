# Student Academic Advisor - Master Requirements Checklist

Course: **Basic of AI Programming Skills (DSC 311)**
Domain: **Student Academic Advisor**
Part B choice: **K-Means Clustering**

## Source of Truth

The following official files are binding:

1. `DSC-311-Group-Project-Cover-Sheets-(HNU--Summer2026).pdf`
2. `AI_Skills_Project_Description.pdf`

Anything not stated in those files must be labeled as an optional enhancement or an internal workflow decision.

## Current Decisions

- [x] Domain: Student Academic Advisor
- [x] Part A: Fuzzy rule-based expert system
- [x] Part B: K-Means clustering
- [x] Part A and Part B must form one coherent project
- [x] Git and GitHub are mandatory internal workflow tools, not official course requirements
- [x] Stable releases go to `main`; ongoing work goes to `develop`
- [ ] Final dataset selected and approved
- [ ] Second knowledge-representation technique selected
- [ ] Inference strategy selected and documented
- [ ] Rule-base storage format selected
- [ ] Final-conclusion aggregation method selected

## Part A - Knowledge Representation

- [ ] Represent facts and domain knowledge in a structured form.
- [ ] Use at least two distinct knowledge-representation techniques.
- [ ] Use production rules; they are mandatory.
- [ ] Pair production rules with at least one of:
  - [ ] Frame-based representation
  - [ ] Object-Attribute-Value triplets
  - [ ] Hierarchical/semantic network representation
- [ ] If frames are selected, include slots, default values, and value restrictions.
- [ ] If O-A-V is selected, express facts as `(object, attribute, value)`.
- [ ] If a semantic network is selected, represent `is-a` or `part-of` relationships.
- [ ] Keep the knowledge base separate from inference logic.
- [ ] Do not hide conclusions in general-purpose hard-coded `if/else` logic.
- [ ] Keep the rule base understandable to a domain expert who does not code.

## Part A - Rule Base

- [ ] Create a substantial, non-trivial set of production rules.
- [ ] Ensure the rules cover the Student Academic Advisor domain.
- [ ] Include at least one nested/parenthesized premise.
- [ ] Correctly apply precedence: `NOT`, then `AND`, then `OR`.
- [ ] Include at least one chained rule.
- [ ] Use one rule's conclusion as another rule's premise.
- [ ] Clearly distinguish intermediate conclusions from final conclusions.
- [ ] Ensure every intermediate conclusion is consumed by another rule.
- [ ] Ensure final conclusions are not consumed by other rules.

## Part A - Inference Engine

- [ ] Implement a working inference engine.
- [ ] Implement forward chaining, backward chaining, or both.
- [ ] State clearly which inference strategy is implemented.
- [ ] Resolve rule dependencies correctly.
- [ ] Evaluate a prerequisite rule before any dependent rule.
- [ ] Use topological ordering for dependency resolution.
- [ ] Detect circular dependencies.
- [ ] Do not silently evaluate circular dependencies.
- [ ] Provide explainability for every reached conclusion.
- [ ] Show which rules fired.
- [ ] Show the order in which rules fired.

## Part A - Fuzzy Logic

- [ ] Represent key domain facts as fuzzy values in `[0, 1]`.
- [ ] Do not represent all key facts as simple Boolean values.
- [ ] Implement fuzzy `AND` as minimum.
- [ ] Implement fuzzy `OR` as maximum.
- [ ] Implement fuzzy `NOT` as `1 - value`.
- [ ] Calculate the Fuzzy Value (FV) of every rule premise.
- [ ] Assign a fixed author-defined Confidence Factor (CF) to every rule.
- [ ] Keep every CF in `[0, 1]`.
- [ ] Calculate `CV = FV * CF` for every rule.
- [ ] Aggregate all final-conclusion CVs at knowledge-base level.
- [ ] Implement the Maximum Method and/or the Union Method.
- [ ] For Maximum Method, calculate `CV(KB) = max(final CVs)`.
- [ ] If Union Method is implemented, calculate `U(a,b) = a + b - a*b`.
- [ ] Fold Union values one at a time when combining more than two values.

## Part A - Inference Network Diagram

- [ ] Produce a diagram of the rule network.
- [ ] Draw an assertion/fact as a square.
- [ ] Draw an intermediate conclusion as a circle inside a square.
- [ ] Draw a final conclusion as a plain circle.
- [ ] Label connecting gates as `AND`, `OR`, or `NOT`.
- [ ] Show at least one complete path from facts to an intermediate conclusion to a final conclusion.
- [ ] Include at least one fully worked inference example in the report.
- [ ] Show every FV, CF, and CV calculation in that example.

## Part B - Domain and Algorithm

- [x] Choose one algorithm: K-Means clustering.
- [ ] Use data from the same Student Academic Advisor domain as Part A.
- [ ] Group students using relevant performance features.
- [ ] Select a sensible number of clusters.
- [ ] Justify the selected number of clusters.
- [ ] Interpret each cluster in the academic domain.
- [ ] Do not assume cluster meaning before training and analysis.

## Part B - Data Preparation

- [ ] State and document the dataset source.
- [ ] Describe the dataset clearly.
- [ ] Inspect and handle missing values.
- [ ] Encode categorical features when needed.
- [ ] Normalize/scale numeric features when needed.
- [ ] Confirm that selected data belongs to the Student Academic Advisor domain.
- [ ] Obtain TA approval for a comparable alternative dataset when required.

## Part B - Model Implementation

- [ ] Implement K-Means correctly.
- [ ] Use a standard library such as scikit-learn.
- [ ] Train the model on the prepared feature matrix.
- [ ] Produce a cluster assignment for every included data point.

## Part B - Evaluation and Interpretation

- [ ] Justify the number of clusters using appropriate evidence.
- [ ] Use the Elbow Method and/or Silhouette Score.
- [ ] Visualize and/or describe the clusters.
- [ ] Analyze cluster centers and feature distributions before naming clusters.
- [ ] Explain whether clusters represent meaningful real-world student groups.
- [ ] Connect the clustering results to the Student Academic Advisor domain.
- [ ] Explain the relationship between Part B results and Part A recommendations.

## Deliverables

- [ ] Submit Part A source code.
- [ ] Include the expert system.
- [ ] Include the inference engine.
- [ ] Include the fuzzy-logic module.
- [ ] Submit Part B source code.
- [ ] Include the K-Means implementation.
- [ ] Submit a short written report.
- [ ] Include the domain description in the report.
- [ ] Include the knowledge-representation choices.
- [ ] Include the full rule base.
- [ ] Include at least one fully worked inference example.
- [ ] Show FV, CF, and CV in the worked example.
- [ ] Include the inference network diagram.
- [ ] Explain the ML approach and data used.
- [ ] Present the ML results.
- [ ] Interpret the results and connect them to the domain.

## Cover Sheet and Administration

- [ ] Select `Student Academic Advisor` on the cover sheet.
- [ ] Type team information; do not handwrite it.
- [ ] Order team member IDs by ID.
- [ ] Write full names in Arabic.
- [ ] Keep only attendance signatures handwritten.
- [ ] Confirm that the team does not exceed the six rows available on the cover sheet.

## Individual / Viva Preparation

The official files specify individual marks but do not define the exact viva format.

- [ ] Prepare every member for Part A individual assessment (4 marks).
- [ ] Prepare every member for Part B individual assessment (5 marks).
- [ ] Explain the selected knowledge representations.
- [ ] Explain facts, intermediate conclusions, and final conclusions.
- [ ] Evaluate nested fuzzy conditions manually.
- [ ] Explain topological ordering and cycle detection.
- [ ] Calculate FV, CF, CV, Maximum, and Union manually.
- [ ] Explain the rule trace and fired-rule order.
- [ ] Explain why scaling matters for K-Means.
- [ ] Explain how K was selected.
- [ ] Interpret clusters using actual results rather than assumptions.
- [ ] Explain how Part A and Part B form one coherent advisor.

## Internal Git Workflow - Not an Official Course Requirement

- [x] Initialize the local Git repository.
- [x] Create and push `main`.
- [x] Create and push `develop`.
- [x] Add an initial `README.md` and `.gitignore`.
- [ ] Work on `develop` during implementation.
- [ ] Commit only reviewed, coherent changes.
- [ ] Merge approved milestones into `main`.
- [ ] Keep secrets, virtual environments, caches, and temporary files out of Git.

## Explicitly Not Required by the Official Files

The following must remain optional unless the TA issues new requirements:

- GUI or web application
- API
- Database
- Authentication
- Docker
- Deployment
- Dashboard
- A fixed minimum number of rules
- A specific dataset
- JSON or YAML rule storage
- Git or GitHub
- Directly feeding K-Means cluster labels into the inference engine

## Approval Rule

A phase is approved only after:

1. Its output is tested or manually verified.
2. It is checked against this requirements list.
3. Required and optional work are clearly separated.
4. Any architectural change is recorded and discussed before implementation.
