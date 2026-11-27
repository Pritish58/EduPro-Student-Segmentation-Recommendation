# Student Segmentation and Personalized Course Recommendation System for EduPro

## Abstract
Online learning platforms serve learners with different levels of engagement, subject interests and learning goals. A uniform recommendation strategy may not reflect these differences. This project develops a learner-centric analytics workflow for EduPro using user, course and transaction records. Learner-level behavioural features are engineered from historical enrollments and used for unsupervised segmentation. K-Means is selected using silhouette analysis and compared with Ward hierarchical clustering. A cluster-aware recommendation approach ranks unseen courses using preference fit, course ratings and popularity among similar learners. The supplied workbook contains 3,000 learners, 60 courses, 60 teachers and 10,000 transactions. The selected K-Means solution contains two interpretable groups, with a best silhouette score of 0.5012. The recommendation score is a transparent relevance heuristic; causal engagement lift is not claimed.

## 1. Introduction
Learners do not follow a single learning pattern. Some enroll in a small number of courses, while others explore multiple categories and build a broader learning history. A platform that recommends courses without considering these behavioural differences may provide less relevant discovery. EduPro addresses this problem by creating learner profiles, identifying behavioural segments and generating personalized course suggestions.

The objective is to understand learner behaviour rather than forecast course demand. The system is designed to support learner exploration, segment-level analysis and personalized course discovery.

## 2. Dataset Description
The source workbook contains four sheets:

| Sheet | Records | Use |
|---|---:|---|
| Users | 3,000 | UserID, age and gender for learner profiles |
| Teachers | 60 | Teacher expertise and quality context |
| Courses | 60 | Course category, type, level, price, duration and rating |
| Transactions | 10,000 | Enrollment history, date, amount, payment method and linked IDs |

The transaction period spans 2025-01-01 to 2025-12-30.

## 3. Data Preparation and Quality
The source workbook was inspected for missing values, duplicate rows and invalid relationships. No missing values or duplicate rows were found in the four supplied sheets. Every transaction UserID, CourseID and TeacherID matched a record in its corresponding reference table. Zero transaction amounts were retained because the catalogue includes free courses; they are valid values rather than missing data.

The original workbook is preserved in `Data/raw/`. Cleaned tables and learner-level outputs are stored separately in `Data/Processed/`. Direct learner names and email addresses are not included in the processed learner exports.

## 4. Feature Engineering
Transactions were aggregated by UserID and joined with course and demographic attributes. The engineered features include:
- Total enrollments and unique courses.
- Average courses per category and enrollment frequency per 30-day active period.
- Preferred course category, course level and course type.
- Average rating of enrolled courses.
- Total spend and average spend per enrollment.
- Category diversity, measured as the number of distinct categories explored.
- Learning depth index, calculated as advanced enrollments divided by beginner plus advanced enrollments.

Numeric features were standardized before clustering. PCA was used for two-dimensional visualization and not as the primary clustering feature space.

## 5. Learner Segmentation
K-Means was evaluated for K values from 2 through 8. The number of clusters with the highest silhouette score was selected. The selected value was K=2, with a silhouette score of 0.5012. Ward hierarchical clustering using the same number of groups achieved a silhouette score of 0.4998.

### 5.1 Segment profile

| segment_name            |   Learners |   Learner_Share_Pct |   Avg_Enrollments |   Avg_Unique_Courses |   Avg_Spend |   Avg_Category_Diversity |   Avg_Learning_Depth |
|:------------------------|-----------:|--------------------:|------------------:|---------------------:|------------:|-------------------------:|---------------------:|
| Occasional Learners     |       2544 |                84.8 |             1.536 |                1.536 |     135.033 |                     1.48 |                0.396 |
| Highly Engaged Learners |        456 |                15.2 |            13.362 |               13.362 |    1245.18  |                     8.7  |                0.483 |

The segments differ substantially in enrollment intensity and category exploration. Names are assigned after inspecting the observed cluster profiles and are not target labels.

### 5.2 Cluster validation
Mean pairwise cosine similarity within each segment:

|   segment_id | segment_name            |   learners |   mean_pairwise_cosine_similarity |
|-------------:|:------------------------|-----------:|----------------------------------:|
|            0 | Occasional Learners     |       2544 |                          0.13484  |
|            1 | Highly Engaged Learners |        456 |                          0.877449 |

The first two PCA components explain 56.92% of the variance in the standardized learner feature matrix. PCA provides a visual projection; it does not itself establish cluster quality.

## 6. Personalized Recommendation Method
For a selected learner, courses already present in that learner's transaction history are removed from the candidate set. Remaining courses are ranked with a weighted relevance score:

| Component | Weight |
|---|---:|
| Preferred category match | 30% |
| Preferred level match | 20% |
| Course rating | 25% |
| Popularity among learners in the same segment | 20% |
| Overall enrollment popularity | 5% |

This method combines content fit and collaborative evidence at the segment level. It is transparent and can be adjusted as additional learner feedback becomes available.

## 7. Evaluation and Limitations
Silhouette score is used to assess cluster separation and cohesion. Ward hierarchical clustering provides a second unsupervised comparison. Intra-cluster cosine similarity summarizes behavioural consistency within each group.

The workbook does not contain explicit labels stating whether a recommendation was relevant, nor does it contain post-recommendation engagement outcomes. Recommendation precision is therefore not reported as a measured result. It would require labelled relevance judgments or a properly designed temporal holdout evaluation. Engagement lift cannot be inferred causally from historical transactions; it should be tested with post-recommendation outcomes or a controlled experiment.

The dataset is a historical snapshot. Course availability, learner interests and ratings may change over time. Future work should incorporate course completion, click-through, search, feedback and time-on-platform events.

## 8. Conclusion
EduPro demonstrates a practical learner-centric workflow from data quality checks through learner-level feature engineering, unsupervised segmentation and cluster-aware course recommendation. The discovered groups provide an interpretable view of differences in enrollment intensity and category exploration. The recommendation engine uses those profiles to rank unseen courses while avoiding repeat suggestions. The project provides a foundation for future evaluation using actual recommendation feedback and engagement outcomes.
