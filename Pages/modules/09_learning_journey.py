import streamlit as st
from Src.recommender import recommend_courses

def render(D):
    st.subheader("Personalized learning journey")
    learners = D["learners"]
    ids = sorted(learners.UserID.astype(str).unique())
    if not ids:
        st.info("No learner profiles found.")
        return
    uid = st.selectbox("Select learner", ids, key="journey_user")
    p = learners[learners.UserID.astype(str)==uid].iloc[0]
    st.write(f"**Learner segment:** {p.segment_name}")
    st.write(f"**Learning preference:** {p.preferred_category} · {p.preferred_level}")
    recs = recommend_courses(uid, learners, D["enriched"], D["popularity"], D["course_user"], limit=6)
    if recs.empty:
        st.info("No additional courses available.")
    else:
        st.caption("Suggested sequence based on learner fit and segment patterns; it is not a verified prerequisite map.")
        for i, (_, r) in enumerate(recs.iterrows(), 1):
            st.markdown(f"**Step {i}: {r.course_name}**")
            st.caption(f"{r.category} · {r.level} · Match estimate {r.match_score:.1f}%")
            if i < len(recs): st.markdown("↓")
