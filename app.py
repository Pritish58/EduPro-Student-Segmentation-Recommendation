import importlib
import streamlit as st
from dashboard.runtime import load_project_data

st.set_page_config(
    page_title="EduPro | Student Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { max-width: 1500px; padding-top: 1.25rem; padding-bottom: 2rem; }
    .edupro-hero {
        padding: 1.3rem 1.6rem;
        border-radius: 16px;
        background: linear-gradient(115deg, #14243d, #24517c 65%, #3676a8);
        color: #ffffff;
        margin-bottom: 1.1rem;
    }
    .edupro-hero h1 { font-size: 2rem; margin: 0; font-weight: 750; }
    .edupro-hero p { margin: .35rem 0 0; color: #dcecff; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,.2); }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="edupro-hero"><h1>EduPro Intelligence</h1>'
    '<p>Student segmentation · Learner behaviour · Personalized course recommendations</p></div>',
    unsafe_allow_html=True,
)

try:
    DATA = load_project_data()
except Exception as exc:
    st.error("EduPro could not load its data.")
    st.markdown(
        "Check that the original workbook is in **Data/raw/**, or that the "
        "generated CSV files are present in **Data/Processed/**."
    )
    st.exception(exc)
    st.stop()

def make_page(module_name):
    def show_page():
        module = importlib.import_module(module_name)
        module.render(DATA)

    # Give every callable a unique name for Streamlit page identity.
    show_page.__name__ = "show_" + module_name.rsplit(".", 1)[-1]
    show_page.__qualname__ = show_page.__name__
    return show_page

page_definitions = [
    ("Overview", "Pages.modules.01_overview", "🏠"),
    ("Learner Analytics", "Pages.modules.02_learner_analytics", "📊"),
    ("Segments", "Pages.modules.03_segments", "🧩"),
    ("Recommendations", "Pages.modules.04_recommendations", "🎯"),
    ("Learner Profile", "Pages.modules.05_learner_profile", "👤"),
    ("Course Intelligence", "Pages.modules.06_course_intelligence", "📚"),
    ("Model Performance", "Pages.modules.07_model_performance", "📈"),
    ("Data Explorer", "Pages.modules.08_data_explorer", "🗂️"),
    ("Learning Journey", "Pages.modules.09_learning_journey", "🧭"),
]

navigation_pages = [
    st.Page(
        make_page(module_name),
        title=title,
        icon=icon,
        default=(index == 0),
    )
    for index, (title, module_name, icon) in enumerate(page_definitions)
]

selected_page = st.navigation(navigation_pages, position="sidebar")

st.sidebar.divider()
st.sidebar.caption(
    f'{DATA["users"]["UserID"].nunique():,} learners · '
    f'{DATA["courses"]["CourseID"].nunique():,} courses · '
    f'{len(DATA["transactions"]):,} transactions'
)
st.sidebar.caption("Unified Mentor internship project")

selected_page.run()
