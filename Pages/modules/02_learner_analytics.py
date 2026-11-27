import streamlit as st
import plotly.express as px

def render(D):
    st.subheader("Learner analytics")
    learners = D["learners"]
    query = st.text_input("Search by UserID")
    view = learners[learners.UserID.astype(str).str.contains(query, case=False, na=False)] if query else learners
    a,b,c = st.columns(3)
    a.metric("Learners", f"{view.UserID.nunique():,}")
    b.metric("Average enrollments", f"{view.total_enrollments.mean():.2f}" if len(view) else "0")
    c.metric("Average spend", f"₹{view.total_spend.mean():,.2f}" if len(view) else "₹0")
    cols = ["UserID","Age","Gender","segment_name","total_enrollments","unique_courses","total_spend",
            "avg_course_rating","preferred_category","preferred_level","category_diversity","learning_depth_index"]
    st.dataframe(view[cols], use_container_width=True, hide_index=True)
    if len(view):
        st.plotly_chart(px.histogram(view, x="total_enrollments", color="segment_name", barmode="overlay"), use_container_width=True)
