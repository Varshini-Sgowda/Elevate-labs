# Elevate Labs Internship — Task 1: Data Cleaning and Preprocessing

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458)
![Status](https://img.shields.io/badge/Status-Completed-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

This repository contains the complete submission for **Task 1: Data Cleaning and Preprocessing** as part of the **Elevate Labs Data Analyst Internship**. The objective is to take a messy, real-world raw dataset, identify and remedy data quality issues, apply logical missing value treatments and type conversions, and produce an analysis-ready tabular dataset with full reproducibility.

---

## 📌 Table of Contents
1. [Objective](#-objective)
2. [Dataset Description](#-dataset-description)
3. [Tools & Technologies](#-tools--technologies)
4. [Project Structure](#-project-structure)
5. [Data Cleaning Pipeline](#-data-cleaning-pipeline)
6. [Before vs. After Comparison](#-before-vs-after-comparison)
7. [How to Run](#-how-to-run)
8. [Output Files](#-output-files)
9. [Key Learnings & Takeaways](#-key-learnings--takeaways)
10. [Conclusion](#-conclusion)
11. [Internship Requirement Checklist](#-internship-requirement-checklist)

---

## 🎯 Objective
Real-world datasets rarely arrive clean. They are often burdened with missing entries, inconsistent string representations, duplicate records, non-standard column names, and improper data types. 

The primary goal of this project is to build a robust, reproducible data cleaning workflow using **Python** and **Pandas** to:
- Standardize column naming conventions into uniform `snake_case`.
- Audit, analyze, and impute missing data logically without naive zero-filling.
- Uncover and fix subtle real-world anomalies (including column-shift errors and hidden non-breaking space characters).
- Normalize text fields, strip stray whitespaces, and standardize casing.
- Parse date strings into standard chronological `datetime64[ns]` formats.
- Identify and eliminate exact and semantic duplicate catalog entries.
- Conduct automated data quality validation before exporting the final clean dataset.

---

## 📊 Dataset Description
The project uses the globally benchmarked **Netflix Movies and TV Shows** dataset (`netflix_titles.csv`), sourced publicly from Kaggle (curated by Shivam Bansal).

- **Raw Dimensions:** 8,807 rows × 12 columns
- **Domain:** Media and entertainment catalog metadata
- **File Format:** CSV (UTF-8 encoded)

### Schema Overview:
| Column | Description | Initial Type |
| :--- | :--- | :--- |
| `show_id` | Unique alphanumeric identifier for each record | `object` (string) |
| `type` | Content format (`Movie` or `TV Show`) | `object` (string) |
| `title` | Title of the production | `object` (string) |
| `director` | Director(s) of the title | `object` (string) |
| `cast` | Actors / performers featured | `object` (string) |
| `country` | Country or countries of production | `object` (string) |
| `date_added` | Date added to Netflix | `object` (string) |
| `release_year` | Year of initial release | `int64` |
| `rating` | Content maturity classification | `object` (string) |
| `duration` | Length in minutes (movies) or seasons (TV shows) | `object` (string) |
| `listed_in` | Associated genres / categories | `object` (string) |
| `description` | Summary plot synopsis | `object` (string) |

---

## 🛠 Tools & Technologies
- **Python (3.10+)**: Primary programming language for scripting and execution.
- **Pandas**: Core tabular data processing, transformation, and validation library.
- **NumPy**: Numerical operations and missing data handling (`np.nan`).
- **Matplotlib**: Generation of data quality audit and distribution visualizations.
- **Jupyter Notebook**: Interactive, step-by-step documentation and presentation.

---

## 📂 Project Structure
```text
elevate-labs-task-1/
│
├── data/
│   ├── raw/
│   │   └── netflix_titles.csv              # Untouched raw dataset (8,807 rows)
│   └── cleaned/
│       └── netflix_titles_cleaned.csv      # Production-grade cleaned dataset (8,803 rows)
│
├── notebooks/
│   └── Task_1_Data_Cleaning.ipynb         # Fully executed Jupyter Notebook with outputs
│
├── src/
│   └── data_cleaning.py                   # Modular, reusable Python cleaning pipeline
│
├── reports/
│   └── cleaning_summary.md                # Comprehensive data cleaning operations summary
│
├── screenshots/
│   ├── README.md                          # Visualizations guide
│   ├── missing_values_analysis.png        # Missing values chart
│   ├── content_type_distribution.png      # Catalog breakdown chart
│   └── before_vs_after_summary.png        # Executive comparison infographic
│
├── requirements.txt                       # Project dependencies
├── README.md                              # Main documentation and submission report
└── .gitignore                             # Environment and temporary file exclusions
```

---

## ⚙ Data Cleaning Pipeline
The cleaning process is organized into sequential, modular steps executed programmatically in `src/data_cleaning.py` and demonstrated interactively in `notebooks/Task_1_Data_Cleaning.ipynb`:

### Step 1: Initial Inspection & Schema Standardization
- Assessed dataset structure, shape (`8,807` rows, `12` columns), memory usage, and dtypes.
- Transformed all column names to clean, uniform `snake_case` with lowercase characters, eliminating leading/trailing whitespace and non-alphanumeric characters.

### Step 2: Anomaly Detection & Column-Shift Correction
- **Real-World Anomaly Found:** Detected 3 stand-up comedy specials (`show_id`: `s5542`, `s5795`, `s5814`) where the `duration` column was `NaN` because duration values (`'74 min'`, `'84 min'`, `'66 min'`) had been shifted into the `rating` column.
- **Correction:** Relocated the durations to `duration` and reset `rating` to `'Unknown'`. This completely resolved the 3 missing values in `duration`.

### Step 3: Logical Missing-Value Treatment
- **`director` (2,634 nulls / 29.91%)**: Imputed with `'Unknown'` rather than dropping rows, preserving 30% of the dataset for genre and country analysis.
- **`cast` (825 nulls / 9.37%)**: Imputed with `'Unknown'` (predominantly documentaries and animated titles).
- **`country` (831 nulls / 9.44%)**: Imputed with `'Unknown'`.
- **`rating` (4 nulls / 0.05%)**: Imputed with `'Unknown'`.
- **`date_added` (10 nulls / 0.11%)**: Preserved as `NaT` (Not-a-Time) within a native `datetime64[ns]` column to maintain datetime typing without fabricating artificial dates.

### Step 4: Text Normalization & Whitespace Cleansing
- Replaced hidden Unicode non-breaking spaces (`\xa0` / `U+00A0`) with standard spaces across all text columns.
- Stripped leading, trailing, and redundant internal whitespace across all string columns.
- Standardized `type` to Title Case (`"Movie"`, `"TV Show"`).

### Step 5: Datatype Conversions
- Converted `date_added` from inconsistent string format into standard `datetime64[ns]` using `pd.to_datetime(format='mixed')`.
- Validated `release_year` as `int64` and verified that all values fall within valid historical limits (`1925` to `2021`).

### Step 6: Duplicate Detection & Catalog Deduplication
- **Initial Check:** Exact full-row duplicate check showed `0` duplicates in the raw dataset.
- **Deep Audit After Normalization:** 
  1. Identified that title `s6530` (*Consequences*, 2014) was a 100% identical duplicate of `s3372` in every attribute, masked only by a trailing non-breaking space (`\xa0`) in the raw title.
  2. Identified 3 re-released titles (*Esperando la carroza*, *Love in a Puff*, *Sin senos sí hay paraíso*) with duplicate entries.
- **Resolution:** Sorted by `date_added` descending and retained the most recently updated entry per `(title, type)`, removing **4 duplicate records** and preventing double-counting in catalog analytics.

### Step 7: Automated Quality Validation
- Asserted `show_id` uniqueness (100% unique).
- Verified `date_added` is valid `datetime64`.
- Verified 0 unexpected nulls across all text columns.
- Verified 0 duplicate entries remaining.

---

## 📈 Before vs. After Comparison
The table below reflects exact numbers calculated directly from the dataset:

| Attribute / Metric | Raw Dataset (Before) | Cleaned Dataset (After) | Status / Notes |
| :--- | :--- | :--- | :--- |
| **Total Rows** | **8,807** | **8,803** | 4 duplicate records eliminated |
| **Total Columns** | **12** | **12** | Normalized `snake_case` headers |
| **Exact Duplicate Rows** | 0 | 0 | None present initially |
| **Duplicate Catalog Records** | 4 | 0 | Masked `\xa0` duplicate & re-releases resolved |
| **Total Missing Values** | **4,307** | **10** | 4,297 treated; 10 preserved as `NaT` |
| - Missing `director` | 2,634 (29.91%) | 0 (0.00%) | Imputed with `'Unknown'` |
| - Missing `cast` | 825 (9.37%) | 0 (0.00%) | Imputed with `'Unknown'` |
| - Missing `country` | 831 (9.44%) | 0 (0.00%) | Imputed with `'Unknown'` |
| - Missing `rating` | 4 (0.05%) | 0 (0.00%) | Imputed with `'Unknown'` |
| - Misplaced `duration` | 3 (0.03%) | 0 (0.00%) | Relocated to `duration` |
| - Missing `duration` | 3 (0.03%) | 0 (0.00%) | 100% populated after correction |
| - Missing `date_added` | 10 (0.11%) | 10 (0.11%) | Preserved as `NaT` in `datetime64[ns]` |
| **`date_added` Data Type** | `object` (string) | `datetime64[ns]` | Formatted chronological timestamps |
| **`release_year` Data Type** | `int64` | `int64` | Verified integer values (1925–2021) |

---

## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/elevate-labs-task-1.git
cd elevate-labs-task-1
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Python Cleaning Pipeline
Execute the automated cleaning script directly:
```bash
python src/data_cleaning.py
```
*The script will load the raw data, execute all cleaning steps, display the comparison table, and save `data/cleaned/netflix_titles_cleaned.csv`.*

### 5. Run the Interactive Jupyter Notebook
Launch the notebook to inspect the step-by-step analysis:
```bash
jupyter notebook notebooks/Task_1_Data_Cleaning.ipynb
```
*(All cell outputs, previews, and visualizations are also pre-rendered for instant viewing directly on GitHub).*

---

## 📤 Output Files
- **Cleaned Dataset:** `data/cleaned/netflix_titles_cleaned.csv` (8,803 rows × 12 columns, UTF-8 encoded).
- **Executive Summary Report:** `reports/cleaning_summary.md` (Detailed methodology, logic, and metrics).
- **Pre-rendered Notebook:** `notebooks/Task_1_Data_Cleaning.ipynb` (Fully executed notebook with 19 code outputs and plots).
- **Visual Assets:** `screenshots/` containing exported publication-quality figures.

---

## 💡 Key Learnings & Takeaways
1. **Never Impute Blindly:** Missing values in text attributes should never be filled with 0 or dropped without assessment. Dropping rows with missing directors would have discarded nearly 30% of the dataset.
2. **Beware of Hidden Inconsistencies:** Real-world duplicates are often masked by non-breaking whitespace (`\xa0`) or minor typographical discrepancies that evade simple `df.duplicated()` calls.
3. **Column-Shift Anomalies:** Visual and distribution audits are essential for uncovering misplaced values (such as duration values placed in rating columns).
4. **Preserve Datatype Authenticity:** Preserving missing dates as `NaT` within a `datetime64` column maintains strict data typing without fabricating misleading temporal information.

---

## 🏁 Conclusion
Through this data preprocessing project, the Netflix Titles dataset was transformed from an inconsistent, null-heavy raw CSV into a clean, verified, and structured asset. The pipeline adheres to professional data engineering best practices and is 100% reproducible.

---

## 📋 Internship Requirement Checklist
- [x] Missing values identified and handled
- [x] Duplicate records identified and removed
- [x] Text values standardized
- [x] Date formats standardized
- [x] Column names cleaned
- [x] Data types checked and corrected
- [x] Data quality validated
- [x] Cleaned dataset exported
- [x] Cleaning summary created
- [x] GitHub-ready README created
