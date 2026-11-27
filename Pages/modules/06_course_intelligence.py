import streamlit as st

def render(D):
    st.subheader("Course catalogue intelligence")
    courses = D["courses"].copy()
    a,b,c = st.columns(3)
    categories = ["All"] + sorted(courses.CourseCategory.dropna().astype(str).unique())
    levels = ["All"] + sorted(courses.CourseLevel.dropna().astype(str).unique())
    cat = a.selectbox("Category", categories)
    level = b.selectbox("Level", levels)
    query = c.text_input("Search course")
    if cat != "All": courses = courses[courses.CourseCategory.astype(str)==cat]
    if level != "All": courses = courses[courses.CourseLevel.astype(str)==level]
    if query: courses = courses[courses.CourseName.astype(str).str.contains(query, case=False, na=False)]
    st.caption(f"{len(courses):,} courses")
    st.dataframe(courses, use_container_width=True, hide_index=True)
