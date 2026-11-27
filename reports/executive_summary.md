# EduPro Executive Summary

## Project purpose
EduPro is a student-centric analytics and recommendation system. It identifies learner behaviour patterns, segments learners using unsupervised machine learning, and recommends courses based on learner preferences and similar learners.

## Dataset
The supplied workbook contains 3,000 users, 60 courses, 60 teachers and 10,000 transactions. The transaction period runs from 2025-01-01 to 2025-12-30. Data quality checks found no missing values, duplicate rows or broken user/course/teacher references in the supplied sheets.

## Analytical approach
Transactions are joined to course and learner attributes and aggregated by UserID. Engineered features include total enrollments, unique courses, total and average spend, preferred category and level, average enrolled-course rating, category diversity, enrollment frequency and learning depth index. Numeric features are standardized before clustering.

## Segmentation results
K-Means selected **K=2** from the tested range K=2 to K=8 using the silhouette score. The best silhouette score was **0.5020**. Ward hierarchical clustering achieved **0.5007**. The resulting two segments are:

| segment_name            |   Learners |   Learner_Share_Pct |   Avg_Enrollments |   Avg_Category_Diversity |
|:------------------------|-----------:|--------------------:|------------------:|-------------------------:|
| Highly Engaged Learners |        455 |               15.17 |            13.382 |                    8.714 |
| Occasional Learners     |       2545 |               84.83 |             1.537 |                    1.48  |

## Recommendation approach
Recommendations combine preferred category, preferred level, course rating, popularity among learners in the same segment and overall popularity. Courses already enrolled in by the learner are excluded.

## Stakeholder value
- More relevant course discovery.
- Clearer understanding of learner engagement patterns.
- Segment-aware course communication and learning paths.
- A foundation for future recommendation experiments.

## Measurement limitations
Recommendation scores are heuristic relevance estimates. Recommendation precision requires labelled relevance data or a defined offline evaluation protocol. Engagement lift requires post-recommendation outcomes or an experiment; historical transactions alone cannot establish causal lift.
