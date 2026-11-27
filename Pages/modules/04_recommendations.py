import streamlit as st
from Src.recommender import recommend_courses

def render(D):
    st.subheader("Personalized course recommendations")
    learners, courses = D["learners"], D["courses"]
    ids = sorted(learners.UserID.astype(str).unique())
    if not ids:
        st.info("No learner profiles found.")
        return
    uid = st.selectbox("Select learner", ids)
    categories = ["All"] + sorted(courses.CourseCategory.dropna().astype(str).unique())
    levels = ["All"] + sorted(courses.CourseLevel.dropna().astype(str).unique())
    a,b = st.columns(2)
    category = a.selectbox("Filter category", categories)
    level = b.selectbox("Filter level", levels)
    profile = learners[learners.UserID.astype(str)==uid].iloc[0]
    st.info(f"Segment: {profile.segment_name} · Preferred category: {profile.preferred_category} · Preferred level: {profile.preferred_level}")
    recs = recommend_courses(uid, learners, D["enriched"], D["popularity"], D["course_user"], category, level)
    if recs.empty:
        st.warning("No unseen courses match these filters.")
    else:
        for _, row in recs.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row.course_name}**")
                st.caption(f"{row.category} · {row.level} · {row.course_type}")
                st.write(f"Rating: {row.avg_rating if row.avg_rating==row.avg_rating else 0:.2f}/5 | Enrollments: {int(row.enrollments)} | Price: ₹{row.price:,.0f}")
                st.progress(min(float(row.match_score)/100,1.0), text=f"Relevance estimate: {row.match_score:.1f}%")
    st.caption("Score weights: category 30%, level 20%, rating 25%, same-segment popularity 20%, overall popularity 5%. This is a heuristic relevance score, not a measured probability.")
