import streamlit as st

def render(D):
    st.subheader("Learner profile explorer")
    learners = D["learners"]
    ids = sorted(learners.UserID.astype(str).unique())
    if not ids:
        st.info("No learner profiles found.")
        return
    uid = st.selectbox("Choose learner", ids, key="profile_uid")
    p = learners[learners.UserID.astype(str)==uid].iloc[0]
    a,b,c,d = st.columns(4)
    a.metric("Segment", p.segment_name)
    b.metric("Enrollments", int(p.total_enrollments))
    c.metric("Unique courses", int(p.unique_courses))
    d.metric("Total spend", f"₹{p.total_spend:,.0f}")
    st.write({"Age":p.Age, "Gender":p.Gender, "Preferred category":p.preferred_category,
        "Preferred level":p.preferred_level, "Average enrolled course rating":round(float(p.avg_course_rating),2),
        "Category diversity":int(p.category_diversity), "Learning depth index":round(float(p.learning_depth_index),3)})
    history = D["enriched"][D["enriched"].UserID.astype(str)==uid].sort_values("TransactionDate", ascending=False)
    st.markdown("#### Enrollment history")
    show = ["CourseID","CourseName","CourseCategory","CourseLevel","CourseRating","TransactionDate","Amount"]
    st.dataframe(history[show], use_container_width=True, hide_index=True)
