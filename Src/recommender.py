"""Cluster-aware course recommendation scoring."""
import pandas as pd

def recommend_courses(uid, learners, enriched, popularity, course_user, category=None, level=None, limit=8):
    found = learners[learners.UserID.astype(str) == str(uid)]
    if found.empty:
        return pd.DataFrame()
    learner = found.iloc[0]
    taken = set(course_user.loc[course_user.UserID.astype(str)==str(uid), "CourseID"].astype(str))
    candidates = popularity[~popularity.CourseID.astype(str).isin(taken)].copy()
    if category and category != "All":
        candidates = candidates[candidates.category.astype(str)==category]
    if level and level != "All":
        candidates = candidates[candidates.level.astype(str)==level]
    if candidates.empty:
        return candidates
    peers = set(learners.loc[learners.segment_id==learner.segment_id, "UserID"].astype(str))
    peer_tx = enriched[enriched.UserID.astype(str).isin(peers)]
    peer_counts = peer_tx.CourseID.value_counts()
    max_peer = max(float(peer_counts.max()) if not peer_counts.empty else 1, 1)
    candidates["category_match"] = (candidates.category.astype(str)==str(learner.preferred_category)).astype(float)
    candidates["level_match"] = (candidates.level.astype(str)==str(learner.preferred_level)).astype(float)
    candidates["rating_norm"] = candidates.avg_rating.fillna(0).clip(0,5)/5
    candidates["peer_popularity"] = candidates.CourseID.map(peer_counts).fillna(0)/max_peer
    candidates["pop_norm"] = candidates.enrollments/max(float(candidates.enrollments.max()),1)
    candidates["match_score"] = (0.30*candidates.category_match + 0.20*candidates.level_match +
        0.25*candidates.rating_norm + 0.20*candidates.peer_popularity + 0.05*candidates.pop_norm)*100
    return candidates.sort_values(["match_score","avg_rating","enrollments"], ascending=False).head(limit)
