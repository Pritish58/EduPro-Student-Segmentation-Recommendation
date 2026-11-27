import streamlit as st

def render(D):
    st.subheader("Data explorer")
    options = {"Users":D["users"], "Teachers":D["teachers"], "Courses":D["courses"],
        "Transactions":D["transactions"], "Learner profiles":D["learners"],
        "Enriched transactions":D["enriched"]}
    name = st.selectbox("Select dataset", list(options))
    df = options[name]
    st.caption(f"{len(df):,} rows · {len(df.columns):,} columns")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download selected table (CSV)", df.to_csv(index=False).encode("utf-8"),
        file_name=name.lower().replace(" ","_")+".csv", mime="text/csv")
