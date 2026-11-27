from pathlib import Path
import warnings
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DATA_DIRS = [ROOT / "Data" / "raw"]


# ============================================================
# 1. LOAD ORIGINAL EXCEL WORKBOOK
# ============================================================

def _read_workbook():
    files = []

    for folder in DATA_DIRS:
        files.extend(folder.glob("*.xlsx"))
        files.extend(folder.glob("*.xls"))

    if not files:
        raise FileNotFoundError(
            f"No Excel workbook found in {', '.join(map(str, DATA_DIRS))}. "
            "Add the EduPro workbook containing Users, Courses and Transactions sheets."
        )

    files = sorted(files)

    with pd.ExcelFile(files[0]) as book:
        sheet_names = list(book.sheet_names)

        sheets = {
            name.strip().lower(): pd.read_excel(book, sheet_name=name)
            for name in sheet_names
        }

    def get(name):
        for key, value in sheets.items():
            if key == name.lower() or name.lower() in key:
                return value.copy()

        raise ValueError(
            f"Required sheet '{name}' not found. "
            f"Available sheets: {sheet_names}"
        )

    users = get("Users")
    courses = get("Courses")
    transactions = get("Transactions")

    teachers = next(
        (
            frame.copy()
            for key, frame in sheets.items()
            if "teacher" in key
        ),
        pd.DataFrame(columns=["TeacherID"])
    )

    return users, courses, transactions, teachers


# ============================================================
# 2. DATA CLEANING HELPERS
# ============================================================

def _clean_columns(df):
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _ensure(df, columns, defaults=None):
    defaults = defaults or {}

    for col in columns:
        if col not in df.columns:
            df[col] = defaults.get(col, np.nan)

    return df


# ============================================================
# 3. LOAD PROCESSED CSV DATA
# ============================================================

def _load_processed_data():

    processed_dir = ROOT / "Data" / "Processed"

    required_files = [
        "users_cleaned.csv",
        "courses_cleaned.csv",
        "transactions_cleaned.csv",
        "enrollments_enriched.csv",
        "learner_profiles_segmented.csv",
        "course_popularity.csv",
    ]

    missing = [
        name
        for name in required_files
        if not (processed_dir / name).exists()
    ]

    if missing:
        raise FileNotFoundError(
            "The original Excel workbook was not found in Data/raw, "
            "and the processed tables are incomplete. "
            f"Missing files in Data/Processed: {', '.join(missing)}. "
            "Keep the original workbook in Data/raw or include the generated CSV files."
        )

    def read_csv(name, parse_dates=None):

        path = processed_dir / name

        if not path.exists():
            return pd.DataFrame()

        frame = pd.read_csv(path)

        for column in parse_dates or []:
            if column in frame.columns:
                frame[column] = pd.to_datetime(
                    frame[column],
                    errors="coerce"
                )

        return frame

    users = read_csv("users_cleaned.csv")
    courses = read_csv("courses_cleaned.csv")

    transactions = read_csv(
        "transactions_cleaned.csv",
        ["TransactionDate"]
    )

    enriched = read_csv(
        "enrollments_enriched.csv",
        ["TransactionDate"]
    )

    learners = read_csv(
        "learner_profiles_segmented.csv",
        ["first_enrollment", "last_enrollment"]
    )

    popularity = read_csv("course_popularity.csv")
    teachers = read_csv("teacher_expertise_summary.csv")
    cluster_eval_df = read_csv("cluster_evaluation.csv")
    cluster_profiles = read_csv("cluster_profiles.csv")
    intra_cluster_similarity = read_csv("intra_cluster_similarity.csv")

    metadata_path = ROOT / "Models" / "model_metadata.json"

    metadata = {}

    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as file:
            metadata = json.load(file)

    model_path = ROOT / "Models" / "kmeans_model.joblib"
    scaler_path = ROOT / "Models" / "feature_scaler.joblib"

    model = (
        joblib.load(model_path)
        if model_path.exists()
        else None
    )

    scaler = (
        joblib.load(scaler_path)
        if scaler_path.exists()
        else None
    )

    course_user = (
        enriched[["UserID", "CourseID"]].drop_duplicates()
        if {"UserID", "CourseID"}.issubset(enriched.columns)
        else pd.DataFrame(columns=["UserID", "CourseID"])
    )

    selected_k = metadata.get(
        "selected_k",
        learners["segment_id"].nunique()
        if "segment_id" in learners.columns
        else 1
    )

    best_k = int(selected_k)

    hierarchical_silhouette = float(
        metadata.get("hierarchical_silhouette", 0.0)
    )

    pca_variance = metadata.get(
        "pca_variance",
        [0.0, 0.0]
    )

    feature_columns = metadata.get(
        "feature_columns",
        []
    )

    return {
        "users": users,
        "courses": courses,
        "transactions": transactions,
        "teachers": teachers,
        "enriched": enriched,
        "learners": learners,
        "popularity": popularity,
        "course_user": course_user,
        "best_k": best_k,
        "hierarchical_silhouette": hierarchical_silhouette,
        "pca_variance": pca_variance,
        "cluster_eval": cluster_eval_df.to_dict("records"),
        "scaler": scaler,
        "kmeans_model": model,
        "feature_columns": feature_columns,
        "cluster_profiles": cluster_profiles,
        "intra_cluster_similarity": intra_cluster_similarity,
        "data_source": "processed_csv",
    }


# ============================================================
# 4. GENERATE SYNTHETIC DEMO DATA
# Used only when Excel and processed CSV files are unavailable.
# ============================================================

def _build_demo_data():

    rng = np.random.default_rng(42)

    user_count = 300
    course_count = 35
    transaction_count = 1200

    categories = [
        "Data Science",
        "Programming",
        "AI & ML",
        "Business",
        "Design",
        "Cloud Computing"
    ]

    # Users
    users = pd.DataFrame({
        "UserID": [
            f"DEMO_U{i:04d}"
            for i in range(1, user_count + 1)
        ],
        "Age": rng.integers(18, 46, user_count),
        "Gender": rng.choice(
            ["Male", "Female", "Other"],
            user_count
        )
    })

    # Courses
    courses = pd.DataFrame({
        "CourseID": [
            f"DEMO_C{i:03d}"
            for i in range(1, course_count + 1)
        ],
        "CourseName": [
            f"Demo Course {i}"
            for i in range(1, course_count + 1)
        ],
        "CourseCategory": rng.choice(
            categories,
            course_count
        ),
        "CourseType": rng.choice(
            ["Online", "Recorded", "Live"],
            course_count
        ),
        "CourseLevel": rng.choice(
            ["Beginner", "Intermediate", "Advanced"],
            course_count
        ),
        "CourseRating": rng.uniform(
            3.0, 5.0, course_count
        ).round(2),
        "CoursePrice": rng.integers(
            499, 5000, course_count
        ),
        "CourseDuration": rng.integers(
            5, 60, course_count
        )
    })

    # Transactions
    transactions = pd.DataFrame({
        "TransactionID": [
            f"DEMO_TX{i:05d}"
            for i in range(1, transaction_count + 1)
        ],
        "UserID": rng.choice(
            users["UserID"],
            transaction_count
        ),
        "CourseID": rng.choice(
            courses["CourseID"],
            transaction_count
        ),
        "TransactionDate": (
            pd.Timestamp.today().normalize()
            - pd.to_timedelta(
                rng.integers(1, 366, transaction_count),
                unit="D"
            )
        ),
        "Amount": rng.integers(
            499, 5000, transaction_count
        ),
        "TeacherID": rng.choice(
            [
                f"DEMO_T{i:03d}"
                for i in range(1, 16)
            ],
            transaction_count
        ),
        "PaymentMethod": rng.choice(
            ["UPI", "Card", "Net Banking"],
            transaction_count
        )
    })

    # Teachers
    teachers = pd.DataFrame({
        "TeacherID": [
            f"DEMO_T{i:03d}"
            for i in range(1, 16)
        ],
        "Expertise": rng.choice(
            categories,
            15
        ),
        "YearsOfExperience": rng.integers(
            1, 20, 15
        ),
        "TeacherRating": rng.uniform(
            3.5, 5.0, 15
        ).round(2)
    })

    # Reuse the same feature engineering and clustering pipeline.
    original_reader = _read_workbook

    try:

        globals()["_read_workbook"] = lambda: (
            users,
            courses,
            transactions,
            teachers
        )

        result = build_data()

        result["data_source"] = "synthetic_demo"

        return result

    finally:

        globals()["_read_workbook"] = original_reader


# ============================================================
# 5. MAIN DATA PROCESSING AND ML PIPELINE
# ============================================================

def build_data():

    try:

        source_tables = _read_workbook()

    except FileNotFoundError:

        try:
            return _load_processed_data()

        except FileNotFoundError:
            return _build_demo_data()

    users, courses, tx, teachers = [
        _clean_columns(x)
        for x in source_tables
    ]

    # Ensure required columns exist.
    _ensure(
        users,
        ["UserID", "Age", "Gender"]
    )

    _ensure(
        courses,
        [
            "CourseID",
            "CourseName",
            "CourseCategory",
            "CourseType",
            "CourseLevel",
            "CourseRating",
            "CoursePrice",
            "CourseDuration"
        ]
    )

    _ensure(
        tx,
        [
            "UserID",
            "CourseID",
            "TransactionDate",
            "Amount",
            "TransactionID"
        ]
    )

    _ensure(
        tx,
        ["TeacherID", "PaymentMethod"]
    )

    _ensure(
        teachers,
        [
            "TeacherID",
            "Expertise",
            "YearsOfExperience",
            "TeacherRating"
        ]
    )

    # Remove duplicate and missing IDs.
    users = (
        users.dropna(subset=["UserID"])
        .drop_duplicates("UserID")
    )

    courses = (
        courses.dropna(subset=["CourseID"])
        .drop_duplicates("CourseID")
    )

    tx = tx.dropna(
        subset=["UserID", "CourseID"]
    ).copy()

    # Keep only required learner fields.
    users = users[
        ["UserID", "Age", "Gender"]
    ].copy()

    teachers = teachers[
        [
            "TeacherID",
            "Expertise",
            "YearsOfExperience",
            "TeacherRating"
        ]
    ].copy()

    # Clean categorical fields.
    for col in [
        "CourseName",
        "CourseCategory",
        "CourseType",
        "CourseLevel"
    ]:
        courses[col] = (
            courses[col]
            .fillna("Unknown")
            .astype(str)
        )

    for col in [
        "PaymentMethod",
        "TeacherID"
    ]:
        tx[col] = (
            tx[col]
            .fillna("Unknown")
            .astype(str)
        )

    # Convert numerical and date fields.
    tx["TransactionDate"] = pd.to_datetime(
        tx["TransactionDate"],
        errors="coerce"
    )

    tx["Amount"] = pd.to_numeric(
        tx["Amount"],
        errors="coerce"
    ).fillna(0)

    courses["CourseRating"] = pd.to_numeric(
        courses["CourseRating"],
        errors="coerce"
    )

    courses["CoursePrice"] = pd.to_numeric(
        courses["CoursePrice"],
        errors="coerce"
    ).fillna(0)

    # Handle missing transaction IDs.
    if tx["TransactionID"].isna().all():

        tx["TransactionID"] = np.arange(
            1,
            len(tx) + 1
        )

    else:

        missing = tx["TransactionID"].isna()

        tx.loc[missing, "TransactionID"] = [
            f"TX{i}"
            for i in range(int(missing.sum()))
        ]

    # ========================================================
    # 6. MERGE DATA
    # ========================================================

    enriched = tx.merge(
        courses,
        on="CourseID",
        how="left",
        suffixes=("", "_course")
    )

    enriched = enriched.merge(
        users,
        on="UserID",
        how="left",
        suffixes=("", "_user")
    )

    for col in [
        "CourseCategory",
        "CourseType",
        "CourseLevel",
        "CourseName"
    ]:

        enriched[col] = (
            enriched[col]
            .fillna("Unknown")
            .astype(str)
        )

    enriched["CourseRating"] = pd.to_numeric(
        enriched["CourseRating"],
        errors="coerce"
    )

    enriched["Amount"] = pd.to_numeric(
        enriched["Amount"],
        errors="coerce"
    ).fillna(0)

    # ========================================================
    # 7. LEARNER FEATURE ENGINEERING
    # ========================================================

    grouped = enriched.groupby(
        "UserID",
        dropna=False
    )

    learners = grouped.agg(

        total_enrollments=(
            "TransactionID",
            "count"
        ),

        unique_courses=(
            "CourseID",
            "nunique"
        ),

        total_spend=(
            "Amount",
            "sum"
        ),

        avg_course_rating=(
            "CourseRating",
            "mean"
        ),

        category_diversity=(
            "CourseCategory",
            "nunique"
        ),

        preferred_category=(
            "CourseCategory",
            lambda s: (
                s.mode().iloc[0]
                if not s.mode().empty
                else "Unknown"
            )
        ),

        preferred_level=(
            "CourseLevel",
            lambda s: (
                s.mode().iloc[0]
                if not s.mode().empty
                else "Unknown"
            )
        ),

        preferred_course_type=(
            "CourseType",
            lambda s: (
                s.mode().iloc[0]
                if not s.mode().empty
                else "Unknown"
            )
        ),

        beginner_count=(
            "CourseLevel",
            lambda s: s.astype(str)
            .str.lower()
            .str.contains("beginner|basic|intro")
            .sum()
        ),

        advanced_count=(
            "CourseLevel",
            lambda s: s.astype(str)
            .str.lower()
            .str.contains("advanced|expert")
            .sum()
        ),

        first_enrollment=(
            "TransactionDate",
            "min"
        ),

        last_enrollment=(
            "TransactionDate",
            "max"
        )

    ).reset_index()

    learners["avg_spend_per_enrollment"] = (
        learners["total_spend"]
        / learners["total_enrollments"].clip(lower=1)
    )

    learners["average_courses_per_category"] = (
        learners["total_enrollments"]
        / learners["category_diversity"].clip(lower=1)
    )

    span_days = (
        learners["last_enrollment"]
        - learners["first_enrollment"]
    ).dt.days

    active_months = (
        span_days.fillna(0) / 30.0
    ).clip(lower=1)

    learners["enrollment_frequency"] = (
        learners["total_enrollments"]
        / active_months
    )

    learners["learning_depth_index"] = (
        learners["advanced_count"]
        /
        (
            learners["beginner_count"]
            + learners["advanced_count"]
        ).replace(0, np.nan)
    )

    learners["learning_depth_index"] = (
        learners["learning_depth_index"]
        .fillna(0)
    )

    learners = learners.merge(
        users[["UserID", "Age", "Gender"]],
        on="UserID",
        how="left"
    )

    learners["Age"] = pd.to_numeric(
        learners["Age"],
        errors="coerce"
    )

    learners["Gender"] = (
        learners["Gender"]
        .fillna("Unknown")
        .astype(str)
    )

    learners["avg_course_rating"] = (
        learners["avg_course_rating"]
        .fillna(courses["CourseRating"].mean())
        .fillna(0)
    )

    # Include users who have no transactions.
    missing_users = users[
        ~users["UserID"].isin(learners["UserID"])
    ][
        ["UserID", "Age", "Gender"]
    ].copy()

    if not missing_users.empty:

        defaults = {
            "total_enrollments": 0,
            "unique_courses": 0,
            "total_spend": 0,
            "avg_course_rating": float(
                courses["CourseRating"].mean() or 0
            ),
            "category_diversity": 0,
            "preferred_category": "No enrolments",
            "preferred_level": "No enrolments",
            "preferred_course_type": "No enrolments",
            "beginner_count": 0,
            "advanced_count": 0,
            "first_enrollment": pd.NaT,
            "last_enrollment": pd.NaT,
            "avg_spend_per_enrollment": 0,
            "average_courses_per_category": 0,
            "enrollment_frequency": 0,
            "learning_depth_index": 0
        }

        for col, default in defaults.items():
            missing_users[col] = default

        learners = pd.concat(
            [
                learners,
                missing_users[learners.columns]
            ],
            ignore_index=True
        )

    # ========================================================
    # 8. MACHINE LEARNING FEATURE MATRIX
    # ========================================================

    feature_cols = [
        "Age",
        "total_enrollments",
        "unique_courses",
        "total_spend",
        "avg_spend_per_enrollment",
        "avg_course_rating",
        "category_diversity",
        "average_courses_per_category",
        "enrollment_frequency",
        "learning_depth_index"
    ]

    X = learners[feature_cols].replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = (
        X.fillna(X.median(numeric_only=True))
        .fillna(0)
    )

    n = len(learners)

    # ========================================================
    # 9. K-MEANS CLUSTERING AND PCA
    # ========================================================

    if n >= 3 and X.nunique().sum() > 1:

        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(X)

        candidates = []

        max_k = min(8, n - 1)

        for k in range(2, max_k + 1):

            candidate_model = KMeans(
                n_clusters=k,
                random_state=42,
                n_init=10
            )

            labels = candidate_model.fit_predict(
                X_scaled
            )

            if len(set(labels)) > 1:

                candidates.append({
                    "k": k,
                    "silhouette": float(
                        silhouette_score(
                            X_scaled,
                            labels
                        )
                    ),
                    "inertia": float(
                        candidate_model.inertia_
                    )
                })

        best_k = (
            max(
                candidates,
                key=lambda x: x["silhouette"]
            )["k"]
            if candidates
            else 2
        )

        model = KMeans(
            n_clusters=best_k,
            random_state=42,
            n_init=10
        )

        learners["segment_id"] = (
            model.fit_predict(X_scaled)
        )

        hierarchical = AgglomerativeClustering(
            n_clusters=best_k,
            linkage="ward"
        ).fit_predict(X_scaled)

        hierarchical_silhouette = (
            float(
                silhouette_score(
                    X_scaled,
                    hierarchical
                )
            )
            if len(set(hierarchical)) > 1
            else 0.0
        )

        pca = PCA(
            n_components=2,
            random_state=42
        )

        coords = pca.fit_transform(X_scaled)

        learners["pca_x"] = coords[:, 0]
        learners["pca_y"] = coords[:, 1]

        pca_variance = (
            pca.explained_variance_ratio_.tolist()
        )

    else:

        scaler = None
        model = None

        X_scaled = np.zeros(
            (n, len(feature_cols))
        )

        learners["segment_id"] = 0
        learners["pca_x"] = 0.0
        learners["pca_y"] = 0.0

        best_k = 1
        hierarchical_silhouette = 0.0
        pca_variance = [0.0, 0.0]
        candidates = []

    # ========================================================
    # 10. SEGMENT PROFILING
    # ========================================================

    cluster_profiles = learners.groupby(
        "segment_id"
    ).agg(

        avg_enrollments=(
            "total_enrollments",
            "mean"
        ),

        avg_diversity=(
            "category_diversity",
            "mean"
        ),

        avg_depth=(
            "learning_depth_index",
            "mean"
        ),

        avg_spend=(
            "total_spend",
            "mean"
        )

    )

    ordered_ids = (
        cluster_profiles
        .sort_values("avg_enrollments")
        .index.tolist()
    )

    names = {}

    if len(ordered_ids) == 1:

        names[ordered_ids[0]] = "General Learners"

    elif len(ordered_ids) == 2:

        names[ordered_ids[0]] = "Occasional Learners"
        names[ordered_ids[1]] = "Highly Engaged Learners"

    else:

        names[ordered_ids[0]] = "Occasional Learners"
        names[ordered_ids[-1]] = "Highly Engaged Learners"

        for sid in ordered_ids[1:-1]:

            profile = cluster_profiles.loc[sid]

            if (
                profile["avg_depth"]
                >= cluster_profiles["avg_depth"].median()
            ):

                names[sid] = "Advanced Learning Focus"

            elif (
                profile["avg_diversity"]
                <= cluster_profiles["avg_diversity"].median()
            ):

                names[sid] = "Specialized Learners"

            else:

                names[sid] = "Multi-Category Learners"

    learners["segment_name"] = (
        learners["segment_id"].map(names)
    )

    # ========================================================
    # 11. INTRA-CLUSTER COSINE SIMILARITY
    # ========================================================

    if n >= 3 and X.nunique().sum() > 1:

        row_norms = np.linalg.norm(
            X_scaled,
            axis=1,
            keepdims=True
        )

        normalized = (
            X_scaled
            / np.where(row_norms == 0, 1, row_norms)
        )

    else:

        normalized = np.zeros(
            (n, len(feature_cols))
        )

    similarity_rows = []

    for sid in sorted(
        learners["segment_id"].unique()
    ):

        positions = np.flatnonzero(
            learners["segment_id"].to_numpy() == sid
        )

        count = len(positions)

        if count < 2:

            mean_similarity = 1.0

        else:

            vector_sum = normalized[
                positions
            ].sum(axis=0)

            mean_similarity = float(
                (
                    np.dot(vector_sum, vector_sum)
                    - count
                )
                / (count * (count - 1))
            )

        similarity_rows.append({

            "segment_id": int(sid),

            "segment_name": names[sid],

            "learners": int(count),

            "mean_pairwise_cosine_similarity": mean_similarity

        })

    intra_cluster_similarity = pd.DataFrame(
        similarity_rows
    )

    # ========================================================
    # 12. COURSE POPULARITY ANALYSIS
    # ========================================================

    course_user = enriched[
        ["UserID", "CourseID"]
    ].drop_duplicates()

    popularity = enriched.groupby(
        [
            "CourseID",
            "CourseName",
            "CourseCategory",
            "CourseLevel",
            "CourseType"
        ],
        dropna=False
    ).agg(

        enrollments=(
            "TransactionID",
            "count"
        ),

        avg_rating=(
            "CourseRating",
            "mean"
        ),

        price=(
            "CoursePrice",
            "mean"
        ),

        duration=(
            "CourseDuration",
            "first"
        )

    ).reset_index()

    popularity = popularity.rename(
        columns={
            "CourseName": "course_name",
            "CourseCategory": "category",
            "CourseLevel": "level",
            "CourseType": "course_type"
        }
    )

    # ========================================================
    # 13. RETURN ALL DATA
    # ========================================================

    return {

        "users": users,

        "courses": courses,

        "transactions": tx,

        "teachers": teachers,

        "enriched": enriched,

        "learners": learners,

        "popularity": popularity,

        "course_user": course_user,

        "best_k": best_k,

        "hierarchical_silhouette": hierarchical_silhouette,

        "pca_variance": pca_variance,

        "cluster_eval": candidates,

        "scaler": scaler,

        "kmeans_model": model,

        "feature_columns": feature_cols,

        "cluster_profiles": cluster_profiles.reset_index(),

        "data_source": "excel_workbook",

        "intra_cluster_similarity": intra_cluster_similarity

    }


# ============================================================
# 14. SAVE PROCESSED DATA AND MODEL ARTIFACTS
# ============================================================

def save_processed_data(data, output_dir=None):

    output_dir = (
        Path(output_dir)
        if output_dir
        else ROOT / "Data" / "Processed"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Do not export direct identifiers such as names or emails.
    users_export = data["users"][
        ["UserID", "Age", "Gender"]
    ].copy()

    teachers_export = data["teachers"].copy()

    exports = {

        "users_cleaned.csv": users_export,

        "courses_cleaned.csv": data["courses"],

        "transactions_cleaned.csv": data["transactions"],

        "enrollments_enriched.csv": data["enriched"],

        "learner_profiles_segmented.csv": data["learners"],

        "course_popularity.csv": data["popularity"],

        "teacher_expertise_summary.csv": teachers_export,

        "cluster_evaluation.csv": pd.DataFrame(
            data["cluster_eval"]
        ),

        "cluster_profiles.csv": data["cluster_profiles"],

        "intra_cluster_similarity.csv": data[
            "intra_cluster_similarity"
        ],

    }

    saved_paths = []

    for filename, frame in exports.items():

        file_path = output_dir / filename

        frame.to_csv(
            file_path,
            index=False
        )

        saved_paths.append(file_path)

    # Save ML models.
    model_dir = ROOT / "Models"

    model_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    if (
        data.get("kmeans_model") is not None
        and data.get("scaler") is not None
    ):

        joblib.dump(
            data["kmeans_model"],
            model_dir / "kmeans_model.joblib"
        )

        joblib.dump(
            data["scaler"],
            model_dir / "feature_scaler.joblib"
        )

        metadata = {

            "selected_k": int(data["best_k"]),

            "feature_columns": data["feature_columns"],

            "hierarchical_silhouette": float(
                data["hierarchical_silhouette"]
            ),

            "pca_variance": [
                float(x)
                for x in data["pca_variance"]
            ],

            "cluster_evaluation": data["cluster_eval"]

        }

        with open(
            model_dir / "model_metadata.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metadata,
                file,
                indent=2
            )

        saved_paths.extend([

            model_dir / "kmeans_model.joblib",

            model_dir / "feature_scaler.joblib",

            model_dir / "model_metadata.json"

        ])

    return saved_paths