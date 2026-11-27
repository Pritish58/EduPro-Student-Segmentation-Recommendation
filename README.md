# EduPro — Student Segmentation and Personalized Course Recommendation System

**Unified Mentor Internship Project**

EduPro is a learner-centric data science application. It discovers behavioural student segments and recommends relevant courses and learning journeys. Its purpose is not course-demand forecasting.

## Project structure

```text
EduPro/
├── dashboard/
│   └── data_loader.py
├── Data/
│   ├── raw/
│   └── Processed/
├── Models/
├── Notebooks/
│   ├── 01_Data_Understanding_and_EDA.ipynb
│   ├── 02_Learner_Features_and_Segmentation.ipynb
│   └── 03_Personalized_Recommendations_and_Evaluation.ipynb
├── Pages/
│   └── modules/
│       ├── 01_overview.py
│       ├── 02_learner_analytics.py
│       ├── 03_segments.py
│       ├── 04_recommendations.py
│       ├── 05_learner_profile.py
│       ├── 06_course_intelligence.py
│       ├── 07_model_performance.py
│       ├── 08_data_explorer.py
│       └── 09_learning_journey.py
├── reports/
│   ├── research_paper.md
│   ├── data_quality_and_eda_findings.md
│   ├── executive_summary.md
│   └── research_paper_outline.md
├── Src/
│   ├── features.py
│   ├── segmentation.py
│   └── recommender.py
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Dataset requirements

Put the original, unchanged Excel workbook only in `Data/raw/`. Do not manually put cleaned exports in `Data/raw/`. The workbook supplied for this project is already placed in `Data/raw/EduPro_Online_Platform.xlsx`. It contains the `Users`, `Teachers`, `Courses`, and `Transactions` sheets. The workbook must contain sheets:

- **Users:** `UserID`, `Age`, `Gender`
- **Courses:** `CourseID`, `CourseCategory`, `CourseType`, `CourseLevel`, `CourseRating`
- **Transactions:** `UserID`, `CourseID`, `TransactionDate`, `Amount`

Optional course fields: `CourseName`, `CoursePrice`, `CourseDuration`. A `TransactionID` column is optional. A Teachers sheet is optional.

## How to manage Raw and Processed data

- `Data/raw/` is the source-of-truth folder. Keep the original Excel workbook here and do not overwrite it.
- `Data/Processed/` contains generated CSV outputs. Do not manually edit these files; regenerate them by rerunning Notebook 02 after any data or cleaning-rule changes.
- Notebook 01 reads the original workbook from `Data/raw/` for inspection and EDA.
- Notebook 02 runs the cleaning and feature-engineering pipeline, then saves:
  - `users_cleaned.csv`
  - `courses_cleaned.csv`
  - `transactions_cleaned.csv`
  - `enrollments_enriched.csv`
  - `learner_profiles_segmented.csv`
  - `course_popularity.csv`
  - `cluster_evaluation.csv`
  - `cluster_profiles.csv`
  - `intra_cluster_similarity.csv`
  - `teacher_expertise_summary.csv`
- Trained artifacts are saved in `Models/`: `kmeans_model.joblib`, `feature_scaler.joblib`, and `model_metadata.json`.

Recommended workflow: place the source workbook in `Data/raw/` → run Notebook 01 → run Notebook 02 → check the generated CSV files in `Data/Processed/` → run Notebook 03 and the Streamlit dashboard. If the source workbook is replaced with a newer version, rerun the notebooks in order so processed files stay synchronized.

## Methodology mapped to the project brief

1. Learner-level aggregation of transactions by `UserID`.
2. Feature engineering:
   - Total courses enrolled and unique courses
   - Average courses per category
   - Enrollment frequency
   - Preferred category, level and course type
   - Average enrolled-course rating
   - Average spending per learner and per enrollment
   - Category diversity score
   - Learning depth index (advanced-course share relative to beginner and advanced enrollments)
3. Numerical feature standardization.
4. K-Means learner segmentation.
5. Hierarchical clustering (Ward linkage) as validation.
6. Elbow/silhouette selection support through candidate K evaluation and silhouette comparison.
7. PCA projection for cluster visualization.
8. Personalized recommendations using:
   - Content/category and level fit
   - Similar learner segment popularity
   - Rating-weighted relevance
   - Overall course popularity
9. Exclusion of courses already enrolled in by the learner.

## Dashboard modules

- Platform overview
- Learner analytics
- Behavioural segments and comparison
- Personalized recommendations with category and level filters
- Learning journey suggestions
- Individual learner profile and enrollment history
- Course intelligence
- Model evaluation
- Dataset explorer and CSV export

## Cell-wise Jupyter notebooks

The `Notebooks/` folder contains three guided notebooks, organized cell by cell:

1. `01_Data_Understanding_and_EDA.ipynb` — workbook loading, schema checks, missing values, duplicates, distributions and category/enrollment exploration.
2. `02_Learner_Features_and_Segmentation.ipynb` — learner aggregation, engineered features, scaling, K-Means, silhouette-based K selection, Ward validation and PCA.
3. `03_Personalized_Recommendations_and_Evaluation.ipynb` — learner selection, personalized recommendations, already-enrolled-course exclusion, score explanation and evaluation limitations.

Run the notebooks from the project root in VS Code or Jupyter. Install dependencies first, then open a notebook and use **Run All** (or execute cells one at a time). Keep the original workbook in `Data/raw/`; generated CSV files belong in `Data/Processed/`.

## Quick start on Windows

You can double-click `run_edupro.bat`. It creates `.venv` if needed, installs the listed packages, and starts the Streamlit dashboard. Alternatively, use the commands below.

## Run locally (Windows / VS Code)

```powershell
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install -r requirements.txt
streamlit run app.py
```

## Tests\n\nRun the automated pipeline checks from the project root:\n\n```powershell\npy -m unittest discover -s tests -v\n```\n\n## Evaluation and honest reporting

- **Silhouette score:** cluster cohesion/separation proxy.
- **Intra-cluster similarity:** the pipeline reports mean pairwise cosine similarity within each segment in `Data/Processed/intra_cluster_similarity.csv`.
- **Recommendation precision:** requires labelled relevant/not-relevant examples or a documented offline holdout protocol.
- **Engagement lift:** requires post-recommendation engagement outcomes or an experiment. Historical data alone cannot establish causal lift.

Do not fabricate scores or results. The supplied Excel workbook is included in `Data/raw/` and has been processed to generate the CSV outputs and model artifacts in this project. The dashboard also refreshes the processed exports and model artifacts when it loads. Keep personally identifiable learner data out of public GitHub repositories.


## Dashboard deployment note

The dashboard uses Streamlit's explicit `st.navigation` pages, so the page list is controlled by `app.py` and is not duplicated by automatic discovery of the `Pages/` directory.

For local use, keep the original workbook in `Data/raw/`. The app builds fresh learner analytics and refreshes the CSV outputs in `Data/Processed/`.

For hosted deployments where the original Excel workbook is intentionally not committed, include the generated CSV files in `Data/Processed/` and the model metadata in `Models/`. The data loader can then start from those processed tables. Do not commit personal learner names, email addresses, or other direct identifiers.


## Sidebar navigation

The page implementation files live in `Pages/modules/`, not directly in `Pages/`. This is intentional: Streamlit automatically discovers top-level Python files in a `Pages/` directory. Keeping the modules one level down leaves only the main `app` entry in the automatic sidebar and preserves the single custom `EduPro Navigation` menu shown below it.
