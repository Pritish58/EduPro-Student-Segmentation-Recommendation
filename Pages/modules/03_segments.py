import streamlit as st
import plotly.express as px

def render(D):
    st.subheader("Behavioural learner segmentation")
    learners = D["learners"]
    summary = learners.groupby(["segment_id","segment_name"]).agg(
        Learners=("UserID","nunique"), Avg_Enrollments=("total_enrollments","mean"),
        Avg_Spend=("total_spend","mean"), Avg_Rating=("avg_course_rating","mean"),
        Avg_Category_Diversity=("category_diversity","mean"),
        Avg_Learning_Depth=("learning_depth_index","mean")).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)
    left,right = st.columns(2)
    left.plotly_chart(px.bar(summary, x="segment_name", y="Learners", color="segment_name"), use_container_width=True)
    right.plotly_chart(px.scatter(learners, x="total_enrollments", y="total_spend", color="segment_name",
        hover_data=["UserID"]), use_container_width=True)
    st.caption("Segment names are post-clustering interpretations of observed cluster profiles, not predefined labels.")
