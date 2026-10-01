# Data Cleaning Summary

## Dataset
**Netflix Movies and TV Shows** (`netflix_titles.csv`)  
*Source:* Public Netflix Catalog Dataset (Kaggle / Shivam Bansal)  
*Raw File Location:* `data/raw/netflix_titles.csv`  
*Cleaned File Location:* `data/cleaned/netflix_titles_cleaned.csv`  

---

## Cleaning Operations

### 1. Missing-Value Handling
A column-by-column missing value audit revealed **4,307** missing values distributed across six columns. Missing data was treated using context-aware, domain-appropriate logic rather than arbitrary zero-filling or indiscriminate row dropping:

- **`director` (2,634 missing values | 29.91%)**: Film and television production records frequently lack listed directors in catalog metadata, especially for television series and international programs. Imputed with `"Unknown"` to maintain complete text searchability without data loss.
- **`cast` (825 missing values | 9.37%)**: Missing cast metadata occurs predominantly in documentaries, animated productions, voiceover works, and news programming. Imputed with `"Unknown"`.
- **`country` (831 missing values | 9.44%)**: Production countries omitted from source distribution feeds. Imputed with `"Unknown"`.
- **`rating` (4 missing values | 0.05%)**: Genuinely unrated titles missing age classification. Imputed with `"Unknown"`. *(See misplaced data correction below).*
- **`duration` (3 missing values | 0.03%)**: All 3 nulls were caused by a known column-shift error where duration was placed into `rating`. Once corrected, `duration` has **0** missing values.
- **`date_added` (10 missing values | 0.11%)**: Ten records lack addition timestamps. Valid dates were converted to `datetime64[ns]`, while missing entries were preserved as `NaT` (Not-a-Time). Preserving `NaT` maintains temporal data type integrity while avoiding synthetic date fabrication.

### 2. Duplicate Removal
The raw dataset contained 0 exact full-row duplicates (`df.duplicated().sum() == 0`). However, an in-depth audit following whitespace normalization revealed **4 duplicate records**:

1. **Hidden Identical Duplicate**: Title `s6530` (*Consequences*, 2014) contained a trailing non-breaking space character (`\xa0`) in the title string, preventing standard string-matching detection. Once stripped, `s6530` was 100% identical in all attributes (director, cast, country, date added, duration, rating, and description) to `s3372`.
2. **Re-released Catalog Entries**: Three titles (*Esperando la carroza*, *Love in a Puff*, and *Sin senos sí hay paraíso*) had duplicate entries resulting from catalog re-licensing with minor metadata variations.
3. **Deduplication Strategy**: Duplicate records were resolved by sorting descending by `date_added` and retaining the most recently updated entry per `(title, type)`. This prevents double-counting content in downstream exploratory analysis.
- **Duplicate rows removed:** **4** records (catalog reduced from 8,807 to 8,803 rows).

### 3. Text Standardization
String attributes across all object columns were standardized:
- Stripped extraneous leading and trailing whitespace characters.
- Replaced hidden Unicode non-breaking space characters (`\xa0` / `U+00A0`) with standard spaces.
- Standardized `type` column values to Title Case (`"Movie"`, `"TV Show"`).
- Cleaned string representations of empty or literal `"nan"` values.

### 4. Column-Name Standardization
Column headers were standardized programmatically to uniform `snake_case` (lowercase with underscores) with any leading/trailing spaces stripped:
`['show_id', 'type', 'title', 'director', 'cast', 'country', 'date_added', 'release_year', 'rating', 'duration', 'listed_in', 'description']`

### 5. Date Conversion
The `date_added` column was originally stored as an inconsistent object/string (e.g., `'September 25, 2021'` alongside entries containing leading spaces like `' January 11, 2019'`). 
- Stripped whitespace across all 8,797 valid dates.
- Converted into standard Pandas `datetime64[ns]` using `pd.to_datetime(..., format='mixed')`.
- Verified all valid dates parsed cleanly into standard chronological format (`YYYY-MM-DD`).

### 6. Data-Type Corrections
- `date_added`: Converted from `object` (string) to `datetime64[ns]`.
- `release_year`: Validated as clean integer `int64` with historical range bounds verified [1925, 2021].
- `duration`: Verified consistent structure (`X min` for movies, `X Season` / `X Seasons` for TV shows).
- `rating`: Corrected column-shift anomalies and standardized to text `object`.

### 7. Data-Quality Validation
Rigorous automated integrity assertions were executed:
- **Identifier Uniqueness:** Confirmed `show_id` is 100% unique across all 8,803 records.
- **Null Audit:** Verified 0 unexpected nulls across all text columns (`title`, `type`, `director`, `cast`, `country`, `rating`, `duration`).
- **Temporal Integrity:** Verified `date_added` contains only valid timestamps and 10 preserved `NaT` entries.
- **Plausibility Check:** Verified `release_year` bounds are logically sound.
- **Duplicate Verification:** Confirmed 0 duplicate records remain.

---

## Before vs After Comparison

The following table presents actual calculated statistics directly derived from the dataset:

| Metric | Raw Dataset (Before) | Cleaned Dataset (After) | Change / Impact |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 8,807 | 8,803 | -4 duplicate records removed |
| **Total Columns** | 12 | 12 | Standardized schema |
| **Exact Duplicate Rows** | 0 | 0 | None present initially |
| **Duplicate Titles / Records** | 4 | 0 | Masked & re-release duplicates resolved |
| **Total Missing Values** | 4,307 | 10 | 4,297 nulls treated with domain logic |
| **Missing in `director`** | 2,634 (29.91%) | 0 (0.00%) | Imputed with `"Unknown"` |
| **Missing in `cast`** | 825 (9.37%) | 0 (0.00%) | Imputed with `"Unknown"` |
| **Missing in `country`** | 831 (9.44%) | 0 (0.00%) | Imputed with `"Unknown"` |
| **Missing in `rating`** | 4 (0.05%) | 0 (0.00%) | Imputed with `"Unknown"` |
| **Misplaced `duration` in `rating`** | 3 (0.03%) | 0 (0.00%) | Relocated to `duration` |
| **Missing in `duration`** | 3 (0.03%) | 0 (0.00%) | Restored from misplaced ratings |
| **Missing in `date_added`** | 10 (0.11%) | 10 (0.11%) | Preserved as `NaT` in `datetime64[ns]` |
| **`date_added` Data Type** | `object` (string) | `datetime64[ns]` | Standardized temporal type |
| **`release_year` Data Type** | `int64` | `int64` | Validated integer type |

---

## Final Result
The resulting dataset (`data/cleaned/netflix_titles_cleaned.csv`) is clean, structured, and fully prepared for downstream exploratory data analysis, business intelligence dashboards, and statistical modeling. 

All transformations are fully reproducible via `src/data_cleaning.py` and interactively documented in `notebooks/Task_1_Data_Cleaning.ipynb`.

