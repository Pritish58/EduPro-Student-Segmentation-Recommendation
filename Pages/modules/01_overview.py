import streamlit as st
import plotly.express as px
import pandas as pd

def render(D):
    st.subheader("EduPro platform overview")
    users, courses, tx, learners = D["users"], D["courses"], D["transactions"], D["learners"]
    cols = st.columns(4)
    values = [users.UserID.nunique(), courses.CourseID.nunique(), len(tx), float(tx.Amount.fillna(0).sum())]
    labels = ["Learners", "Courses", "Enrollments", "Total learner spend"]
    for c, label, value in zip(cols, labels, values):
        c.metric(label, f"₹{value:,.0f}" if label == "Total learner spend" else f"{value:,}")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Learner segment distribution")
        counts = learners.groupby("segment_name").UserID.nunique().reset_index(name="Learners")
        st.plotly_chart(px.bar(counts, x="segment_name", y="Learners", color="segment_name"), use_container_width=True)
    with right:
        st.markdown("#### Enrollments by course category")
        cat = D["enriched"].groupby("CourseCategory").size().reset_index(name="Enrollments").sort_values("Enrollments", ascending=False)
        st.plotly_chart(px.bar(cat.head(10), x="CourseCategory", y="Enrollments"), use_container_width=True)
    st.markdown("#### Learner map (PCA projection)")
    st.plotly_chart(px.scatter(learners, x="pca_x", y="pca_y", color="segment_name",
        hover_data=["UserID","total_enrollments","total_spend"]), use_container_width=True)
