# Dataset Selection and Audit

Course: **Basic of AI Programming Skills (DSC 311)**

Project: **Student Academic Advisor**

Audit date: **2026-08-19**

Status: **Dataset approved; feature engineering and modelling decisions remain open**

## 1. Purpose

This document records the dataset selection decision and the initial audit of the
official source files. It does not define fuzzy predicates, membership functions,
production rules, K-Means features, the value of `k`, or cluster meanings.

## 2. Selected Source

- Dataset: **Student Performance**
- Provider: **UCI Machine Learning Repository**
- DOI: [10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T)
- Official page: [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student%2Bperformance)
- Creator: Paulo Cortez
- License: **Creative Commons Attribution 4.0 International (CC BY 4.0)**
- Selected file: **`student-por.csv`**
- Selected subject: **Portuguese language course**

The official project description identifies the UCI Student Performance dataset
as one of the suggested dataset starting points. Selecting it therefore avoids the
need to justify an unrelated external dataset.

## 3. Original Package Inventory

The downloaded `student.zip` package contains:

| File | Purpose |
|---|---|
| `student-mat.csv` | Mathematics course records |
| `student-por.csv` | Portuguese language course records |
| `student.txt` | Official attribute descriptions and overlap note |
| `student-merge.R` | Official example for identifying students shared by both files |

The `.csv` files use semicolons (`;`) as delimiters.

## 4. Audit Results

### 4.1 Structural comparison

| Check | Mathematics | Portuguese |
|---|---:|---:|
| Records | 395 | 649 |
| Columns | 33 | 33 |
| Integer columns | 16 | 16 |
| Categorical/text columns | 17 | 17 |
| Missing cells | 0 | 0 |
| Rows containing missing values | 0 | 0 |
| Empty strings | 0 | 0 |
| Exact duplicate rows | 0 | 0 |

Both files have the same schema.

### 4.2 Column groups

The 33 columns can be described at a high level as:

- School and demographic attributes
- Family and parental attributes
- Educational support attributes
- Study and lifestyle attributes
- Attendance data
- First-period, second-period, and final grades

The complete meanings and coded categories are defined in `student.txt` and must
remain the authoritative data dictionary.

### 4.3 Selected-file ranges

Key ranges found in `student-por.csv`:

| Attribute | Minimum | Maximum |
|---|---:|---:|
| `age` | 15 | 22 |
| `studytime` | 1 | 4 |
| `failures` | 0 | 3 |
| `famrel` | 1 | 5 |
| `freetime` | 1 | 5 |
| `goout` | 1 | 5 |
| `Dalc` | 1 | 5 |
| `Walc` | 1 | 5 |
| `health` | 1 | 5 |
| `absences` | 0 | 32 |
| `G1` | 0 | 19 |
| `G2` | 0 | 19 |
| `G3` | 0 | 19 |

All inspected values fall within the documented categorical or numerical domains,
subject to one documentation caution: the description of `failures` is ambiguous,
while the actual files consistently use values from 0 through 3. The project must
use the observed coding without inventing a different interpretation.

### 4.4 Missing values and duplicates

Neither file contains missing values, empty strings, or fully duplicated records.
Therefore:

- Missing-value checking is still part of preprocessing and must be reported.
- No imputation method will be applied unless a later derived dataset introduces a
  documented need for it.
- Missing values must not be fabricated merely to demonstrate imputation.

### 4.5 Shared students and merge risk

`student.txt` states that 382 students occur in both subject datasets. The supplied
`student-merge.R` identifies them by matching these 13 attributes:

`school`, `sex`, `age`, `address`, `famsize`, `Pstatus`, `Medu`, `Fedu`, `Mjob`,
`Fjob`, `reason`, `nursery`, and `internet`.

The audit reproduced a 382-row inner merge using those fields. Because the source
does not provide a true unique student identifier, concatenating the two subject
files would risk double-counting students. The files will therefore not be combined.

## 5. Selection Decision

The project will use **`student-por.csv`** as its primary dataset.

Reasons:

1. It contains 649 records, compared with 395 in `student-mat.csv`.
2. It has the same 33-column schema as the Mathematics file.
3. It represents both schools more evenly: 423 `GP` and 226 `MS`, compared with
   349 `GP` and 46 `MS` in the Mathematics file.
4. Its largest observed absence count is 32, compared with 75 in the Mathematics
   file, reducing the immediate influence of an extreme value during exploratory
   analysis while still requiring scaling.
5. Using one subject file avoids the documented duplicate-student problem.

`student-mat.csv` is retained only as part of the original source package and as a
reference for the audit. It will not be combined with the selected dataset or used
to train the project's K-Means model.

## 6. Relevant Data Risks

### 6.1 Strong grade relationships

In `student-por.csv`, the observed Pearson correlations are:

| Pair | Correlation |
|---|---:|
| `G1` and `G2` | 0.865 |
| `G1` and `G3` | 0.826 |
| `G2` and `G3` | 0.919 |

Using all three grades in K-Means may cause grade information to dominate the
distance calculation. Whether `G3` is excluded from clustering and retained for
post-hoc interpretation remains a feature-selection decision, not an approved fact
at this stage.

### 6.2 Mixed data types

K-Means uses distance calculations, but the dataset contains numerical, ordinal,
binary, and nominal attributes. Consequently:

- Features must be selected for a clear academic-advising purpose.
- Selected nominal attributes require justified encoding.
- Selected numerical features require scaling.
- Integer category codes must not automatically be treated as continuous quantities.
- The complete 33-column dataset must not be passed blindly to K-Means.

### 6.3 Dataset scope

The records concern secondary-school students from two Portuguese schools and two
specific courses. Results must not be presented as universally valid for all
students, universities, or countries.

### 6.4 Sensitive or weakly actionable attributes

The dataset includes demographic, family, relationship, and alcohol-consumption
attributes. Their inclusion in advising rules or clustering must be justified by
the project purpose. Avoiding sensitive or weakly actionable fields is a design
caution, not an additional official requirement.

## 7. Decision Classification

### Official requirement context

- Use a suitable public student dataset for Part B.
- Perform and document the required data-understanding and preprocessing work.
- Apply K-Means and justify `k` using actual analysis.
- Interpret clusters only after training.

### Approved implementation decisions

- Use the UCI Student Performance dataset.
- Use `student-por.csv` as the primary file.
- Do not concatenate the Mathematics and Portuguese files.
- Report that the raw selected file contains no missing values or exact duplicates.
- Do not invent an imputation operation.

### Deferred decisions

- Final K-Means feature set
- Treatment of `G1`, `G2`, and `G3`
- Encoding methods for selected categorical features
- Scaling method
- Outlier-handling decisions
- Fuzzy predicates and membership functions
- Production-rule content and confidence factors
- Candidate values of `k`
- Final value of `k`
- Cluster meanings and labels
- Exact empirical comparison between Part A and Part B

## 8. Reproducibility Checksums

SHA-256 checksums of the inspected source files:

| File | SHA-256 |
|---|---|
| `student-mat.csv` | `e47f9ee225e1ee6e69b7564e6dac7123e80b8486677fe111f351964cef5dec80` |
| `student-por.csv` | `a7594a11d7771c0efe1a740824e0e833da9c4cad07c39a9766a874575563fb3f` |
| `student.txt` | `f8d3e734e237071312790ca667330c66d75e706317f8d5e2125c479d70e962c1` |
| `student-merge.R` | `a04f4ef19551c319428f642269c125faa21c521045946beead1c32e656269d31` |

## 9. Approval

The source and primary file are approved. Data preprocessing and model decisions
remain intentionally unapproved until the next analysis stages provide evidence.
