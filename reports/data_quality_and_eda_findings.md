# EduPro — Dataset Quality and EDA Findings

## Dataset used
Source workbook: `Data/raw/EduPro_Online_Platform.xlsx`

| Sheet | Rows | Columns |
|---|---:|---:|
| Users | 3,000 | 5 in source workbook |
| Teachers | 60 | 7 in source workbook |
| Courses | 60 | 8 |
| Transactions | 10,000 | 7 |

The transaction dates range from **2025-01-01** to **2025-12-30**.

## Data quality checks

| Check | Result |
|---|---:|
| Duplicate user rows | 0 |
| Duplicate course rows | 0 |
| Duplicate transaction rows | 0 |
| Missing values in Users | 0 |
| Missing values in Courses | 0 |
| Missing values in Transactions | 0 |
| Transaction UserIDs absent from Users | 0 |
| Transaction CourseIDs absent from Courses | 0 |
| Transaction TeacherIDs absent from Teachers | 0 |

No missing values, duplicate rows, or broken transaction references were found in the supplied workbook. Zero transaction amounts were retained because the catalogue includes free courses. They are valid records, not missing values.

## Learner and platform overview

- Registered learners: **3,000**
- Courses: **60**
- Teachers: **60**
- Transactions/enrollments: **10,000**
- Average enrollments per learner: **3.33**
- Median enrollments per learner: **1**
- Total transaction amount: **₹911,323.47**
- Mean course catalogue rating: **3.10/5**
- Average learner age: **25.0 years**

## Most enrolled categories

- Data Science: 916 enrollments
- Finance: 864 enrollments
- Web Development: 844 enrollments
- Business: 833 enrollments
- Artificial Intelligence: 829 enrollments
- Project Management: 829 enrollments
- Design: 827 enrollments
- Cybersecurity: 819 enrollments

## Most enrolled courses

- Deep Learning: 334 enrollments
- Natural Language Processing: 321 enrollments
- Data Analysis with Python: 196 enrollments
- Social Media Strategy: 194 enrollments
- Statistical Analysis: 192 enrollments
- AI Ethics: 186 enrollments
- Machine Learning Fundamentals: 185 enrollments
- Investment Strategies: 183 enrollments

## Learner segmentation

K-Means was evaluated for K values from 2 through 8 using standardized learner-level numeric features. K=**2** achieved the highest silhouette score of **0.5012** among the tested values.

|   segment_id | segment_name            |   Learners |   Avg_Enrollments |   Avg_Unique_Courses |   Avg_Spend |   Avg_Category_Diversity |   Avg_Rating |   Avg_Learning_Depth |   Learner_Share_Pct |
|-------------:|:------------------------|-----------:|------------------:|---------------------:|------------:|-------------------------:|-------------:|---------------------:|--------------------:|
|            0 | Occasional Learners     |       2544 |             1.536 |                1.536 |     135.033 |                     1.48 |        3.138 |                0.396 |                84.8 |
|            1 | Highly Engaged Learners |        456 |            13.362 |               13.362 |    1245.18  |                     8.7  |        3.111 |                0.483 |                15.2 |

**Intra-cluster similarity (mean pairwise cosine):**

|   segment_id | segment_name            |   learners |   mean_pairwise_cosine_similarity |
|-------------:|:------------------------|-----------:|----------------------------------:|
|            0 | Occasional Learners     |       2544 |                          0.13484  |
|            1 | Highly Engaged Learners |        456 |                          0.877449 |

Ward hierarchical clustering with the same number of clusters achieved a silhouette score of **0.4998**. The first two PCA components explain **56.92%** of the standardized feature variance.

The discovered segments show a clear difference in enrollment intensity and category exploration. Segment names are descriptive interpretations assigned after inspecting cluster profiles; they are not labels supplied in the dataset.

## Recommendation approach

The recommender excludes courses already enrolled in by the selected learner. Remaining courses are ranked using:

- 30% preferred category match
- 20% preferred course-level match
- 25% course rating
- 20% popularity among learners in the same segment
- 5% overall enrollment popularity

The score is a relevance estimate, not a probability of enrollment or course completion.

## Evaluation limitations

The workbook does not contain explicit recommendation relevance labels or post-recommendation engagement outcomes. Recommendation precision is therefore not reported as a measured result. It requires labelled relevance judgments or a documented offline test protocol. Engagement lift cannot be inferred causally from historical transactions and should be tested using post-recommendation outcomes or a controlled experiment.

## Files generated

Cleaned tables, enriched enrollments, learner profiles, course popularity, cluster profiles, cluster evaluation, intra-cluster similarity, and serialized K-Means/scaler artifacts are saved under `Data/Processed/` and `Models/`.
