import unittest
from dashboard.data_loader import build_data
from Src.recommender import recommend_courses


class EduProPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_data()

    def test_expected_dataset_sizes(self):
        self.assertEqual(len(self.data["users"]), 3000)
        self.assertEqual(len(self.data["courses"]), 60)
        self.assertEqual(len(self.data["transactions"]), 10000)

    def test_transaction_references_are_valid(self):
        self.assertTrue(set(self.data["transactions"]["UserID"]).issubset(set(self.data["users"]["UserID"])))
        self.assertTrue(set(self.data["transactions"]["CourseID"]).issubset(set(self.data["courses"]["CourseID"])))

    def test_every_user_has_a_learner_profile(self):
        self.assertEqual(self.data["learners"]["UserID"].nunique(), self.data["users"]["UserID"].nunique())

    def test_recommendations_exclude_previously_taken_courses(self):
        user_id = str(self.data["learners"].iloc[0]["UserID"])
        recommendations = recommend_courses(
            user_id, self.data["learners"], self.data["enriched"],
            self.data["popularity"], self.data["course_user"], limit=8
        )
        taken = set(self.data["course_user"].loc[
            self.data["course_user"]["UserID"].astype(str) == user_id, "CourseID"
        ].astype(str))
        suggested = set(recommendations["CourseID"].astype(str))
        self.assertTrue(taken.isdisjoint(suggested))

    def test_cluster_evaluation_is_available(self):
        self.assertGreaterEqual(self.data["best_k"], 2)
        self.assertTrue(len(self.data["cluster_eval"]) > 0)
        self.assertTrue(-1 <= self.data["hierarchical_silhouette"] <= 1)


if __name__ == "__main__":
    unittest.main()
