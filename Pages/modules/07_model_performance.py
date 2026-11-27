import streamlit as st
import pandas as pd
import plotly.express as px

def render(D):
    st.subheader("Model evaluation and validation")
    a,b,c = st.columns(3)
    a.metric("Selected K", D["best_k"])
    b.metric("Hierarchical silhouette", f'{D["hierarchical_silhouette"]:.4f}')
    c.metric("PCA variance (2 components)", f'{sum(D["pca_variance"])*100:.1f}%')
    scores = pd.DataFrame(D["cluster_eval"])
    if not scores.empty:
        st.dataframe(scores, use_container_width=True, hide_index=True)
        st.plotly_chart(px.line(scores, x="k", y="silhouette", markers=True, title="Silhouette score by cluster count"), use_container_width=True)
    st.markdown("#### Intra-cluster similarity")
    st.dataframe(D["intra_cluster_similarity"], use_container_width=True, hide_index=True)
    st.markdown("**Evaluation interpretation**")
    st.write("- Silhouette score estimates separation and cohesion of clusters.")
    st.write("- Ward hierarchical clustering is used as a validation comparison.")
    st.write("- PCA is used for visualization, not as the clustering feature space.")
    st.warning("Recommendation precision needs labelled relevance judgments or a defined offline test. Engagement lift cannot be claimed causally without post-recommendation outcome data or an experiment.")
