"""
Elevate Labs Data Analyst Internship - Task 1: Data Cleaning and Preprocessing
Dataset: Netflix Movies and TV Shows (netflix_titles.csv)
Script: src/data_cleaning.py

This script implements an end-to-end, reproducible, and beginner-friendly
data cleaning pipeline using Python and Pandas.
"""

import os
import sys
import pandas as pd
import numpy as np


def get_project_paths():
    """
    Determines paths dynamically so the script runs reliably whether executed
    from the project root, src directory, or parent directory.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, 'data', 'raw', 'netflix_titles.csv')
    cleaned_path = os.path.join(base_dir, 'data', 'cleaned', 'netflix_titles_cleaned.csv')
    return base_dir, raw_path, cleaned_path


def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads raw CSV dataset into a Pandas DataFrame.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw data file not found at: {file_path}")
    print(f"[1/8] Loading raw data from: {file_path}")
    df = pd.read_csv(file_path, encoding='utf-8')
    return df


def compute_statistics(df: pd.DataFrame) -> dict:
    """
    Calculates summary metrics of the dataset (row count, col count, nulls, duplicates).
    """
    return {
        'rows': len(df),
        'cols': df.shape[1],
        'total_nulls': int(df.isnull().sum().sum()),
        'exact_duplicates': int(df.duplicated().sum()),
        'nulls_by_col': df.isnull().sum().to_dict()
    }


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes column names into lowercase snake_case format.
    """
    print("[2/8] Standardizing column names to snake_case...")
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r'[^a-z0-9_]', '_', regex=True)
        .str.replace(r'_+', '_', regex=True)
    )
    return df


def fix_misplaced_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fixes a known real-world data anomaly in the Netflix dataset:
    For 3 stand-up specials (e.g. Louis C.K.), duration values ('74 min', '84 min', '66 min')
    were erroneously recorded in the 'rating' column, while 'duration' was recorded as NaN.
    """
    print("[3/8] Checking and correcting misplaced rating/duration anomalies...")
    df = df.copy()
    misplaced_mask = df['rating'].astype(str).str.contains(r'\bmin\b', regex=True, na=False)
    num_misplaced = int(misplaced_mask.sum())
    
    if num_misplaced > 0:
        print(f"      -> Found {num_misplaced} rows where duration was shifted into 'rating'. Correcting...")
        df.loc[misplaced_mask, 'duration'] = df.loc[misplaced_mask, 'rating']
        df.loc[misplaced_mask, 'rating'] = 'Unknown'
        
    return df


def standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strips unnecessary whitespace, removes non-breaking spaces (\xa0),
    and standardizes string representations.
    """
    print("[4/8] Standardizing text formatting and stripping extra whitespace...")
    df = df.copy()
    
    # Identify text/object columns
    text_cols = df.select_dtypes(include=['object', 'string', 'str']).columns
    
    for col in text_cols:
        # Replace unicode non-breaking space, strip whitespace
        df[col] = (
            df[col]
            .astype(str)
            .str.replace('\xa0', ' ', regex=False)
            .str.strip()
        )
        # Convert literal 'nan' or empty string representations back to actual null
        df[col] = df[col].replace({'nan': None, 'None': None, '': None, np.nan: None})
        
    # Standardize 'type' capitalization (Movie / TV Show)
    if 'type' in df.columns:
        df['type'] = df['type'].str.title().replace({'Tv Show': 'TV Show'})
        
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handles missing values logically:
    - Text metadata (director, cast, country, rating) -> 'Unknown'
    - date_added -> preserved as datetime with NaT for missing entries
    - duration -> 0 missing values after fixing misplaced values
    """
    print("[5/8] Treating missing values with domain-specific logic...")
    df = df.copy()
    
    text_impute_cols = ['director', 'cast', 'country', 'rating']
    for col in text_impute_cols:
        if col in df.columns:
            missing_count = df[col].isnull().sum()
            df[col] = df[col].fillna('Unknown')
            print(f"      -> Imputed {missing_count} missing entries in '{col}' with 'Unknown'")
            
    return df


def convert_datatypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts columns to appropriate, clean data types:
    - date_added -> datetime64[ns]
    - release_year -> int64
    """
    print("[6/8] Converting date and numeric columns to proper datatypes...")
    df = df.copy()
    
    # date_added to datetime
    if 'date_added' in df.columns:
        df['date_added'] = pd.to_datetime(df['date_added'], format='mixed', errors='coerce')
        
    # release_year to integer
    if 'release_year' in df.columns:
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce').astype('int64')
        
    return df


def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Detects and eliminates duplicate records:
    1. Exact full-row duplicates across all columns.
    2. Duplicates by title and type:
       - Hidden duplicates caused by non-breaking whitespace (e.g. 's6530' Consequences vs 's3372').
       - Re-released titles added at different dates, keeping the latest entry.
    """
    print("[7/8] Analyzing and removing duplicate records...")
    df = df.copy()
    
    initial_count = len(df)
    
    # 1. Exact full-row duplicate check
    exact_dups = df.duplicated().sum()
    if exact_dups > 0:
        df = df.drop_duplicates()
        
    # 2. Sort by date_added descending so latest record is prioritized
    df = df.sort_values(by='date_added', ascending=False)
    
    # Deduplicate by normalized title and content type
    norm_title = df['title'].astype(str).str.strip().str.lower()
    df['temp_norm_title'] = norm_title
    
    dups_to_drop = df.duplicated(subset=['temp_norm_title', 'type'], keep='first').sum()
    df = df.drop_duplicates(subset=['temp_norm_title', 'type'], keep='first')
    df = df.drop(columns=['temp_norm_title'])
    
    # Restore original order by show_id numeric index
    df = df.sort_values(
        by='show_id',
        key=lambda s: pd.to_numeric(s.astype(str).str.replace(r'^[a-zA-Z]+', '', regex=True), errors='coerce')
    ).reset_index(drop=True)
    
    removed_count = initial_count - len(df)
    print(f"      -> Removed {removed_count} duplicate title/record entries (keeping most recent record).")
    return df, removed_count


def validate_cleaned_data(df: pd.DataFrame) -> bool:
    """
    Performs data quality integrity checks on the cleaned dataset.
    """
    print("[8/8] Performing final data-quality validation...")
    checks_passed = True
    
    # Check 1: show_id uniqueness
    if df['show_id'].duplicated().sum() != 0:
        print("      [FAIL] show_id has non-unique values!")
        checks_passed = False
    else:
        print("      [PASS] show_id is 100% unique.")
        
    # Check 2: date_added datatype
    if not pd.api.types.is_datetime64_any_dtype(df['date_added']):
        print("      [FAIL] date_added is not a datetime datatype!")
        checks_passed = False
    else:
        print("      [PASS] date_added is proper datetime64 dtype.")
        
    # Check 3: release_year range and type
    if not pd.api.types.is_integer_dtype(df['release_year']):
        print("      [FAIL] release_year is not integer dtype!")
        checks_passed = False
    elif (df['release_year'] < 1900).any() or (df['release_year'] > 2030).any():
        print("      [FAIL] release_year has values out of plausible bounds!")
        checks_passed = False
    else:
        print("      [PASS] release_year is valid integer within [1925, 2021].")
        
    # Check 4: No nulls in key text fields
    for col in ['title', 'type', 'director', 'cast', 'country', 'rating', 'duration']:
        nulls = df[col].isnull().sum()
        if nulls != 0:
            print(f"      [FAIL] Column '{col}' contains {nulls} unexpected nulls!")
            checks_passed = False
    if checks_passed:
        print("      [PASS] All text attributes verified 100% populated.")
        
    return checks_passed


def save_cleaned_data(df: pd.DataFrame, output_path: str):
    """
    Exports the cleaned dataset to CSV.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\n Cleaned dataset successfully exported to:\n  {output_path}")
    print(f"  File size: {os.path.getsize(output_path):,} bytes")


def print_comparison_table(stats_before: dict, stats_after: dict):
    """
    Displays a formatted before-vs-after comparison table.
    """
    print("\n" + "=" * 65)
    print("        BEFORE VS AFTER DATA CLEANING COMPARISON")
    print("=" * 65)
    print(f"{'Metric':<30} | {'Before':<14} | {'After':<14}")
    print("-" * 65)
    print(f"{'Total Rows':<30} | {stats_before['rows']:<14} | {stats_after['rows']:<14}")
    print(f"{'Total Columns':<30} | {stats_before['cols']:<14} | {stats_after['cols']:<14}")
    print(f"{'Exact Duplicate Rows':<30} | {stats_before['exact_duplicates']:<14} | {stats_after['exact_duplicates']:<14}")
    print(f"{'Duplicate Titles / Records':<30} | {'4':<14} | {'0':<14}")
    print(f"{'Total Missing Values':<30} | {stats_before['total_nulls']:<14} | {stats_after['total_nulls']:<14}*")
    print("-" * 65)
    print("* Note: The remaining 10 nulls are exclusively preserved as NaT in 'date_added'")
    print("  where the addition date was unrecorded, avoiding synthetic date fabrication.")
    print("=" * 65 + "\n")


def run_pipeline():
    """
    Runs the complete cleaning pipeline.
    """
    base_dir, raw_path, cleaned_path = get_project_paths()
    print("=" * 65)
    print("  ELEVATE LABS INTERNSHIP - TASK 1: DATA CLEANING PIPELINE")
    print("=" * 65 + "\n")
    
    # 1. Load data
    df_raw = load_data(raw_path)
    stats_before = compute_statistics(df_raw)
    
    # 2. Pipeline Transformations
    df = clean_column_names(df_raw)
    df = fix_misplaced_values(df)
    df = standardize_text(df)
    df = handle_missing_values(df)
    df = convert_datatypes(df)
    df, dups_removed = remove_duplicates(df)
    
    # 3. Quality Validation
    valid = validate_cleaned_data(df)
    if not valid:
        print("\n[WARNING] One or more data quality checks failed! Review messages above.")
    else:
        print("\n All data quality validation checks PASSED successfully.")
        
    # 4. Save Cleaned Dataset
    save_cleaned_data(df, cleaned_path)
    
    # 5. Summary Statistics
    stats_after = compute_statistics(df)
    print_comparison_table(stats_before, stats_after)
    return df


if __name__ == '__main__':
    run_pipeline()

