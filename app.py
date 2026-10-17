"""Label History: how FDA drug labels changed over time, and which labels mention a topic."""
import streamlit as st
from fastembed import TextEmbedding

from pipeline.gold import MODEL
from pipeline.search import load, search

st.set_page_config(page_title="Label History")
con = st.cache_resource(load)()
embedder = st.cache_resource(TextEmbedding)(MODEL)

st.title("Label History")
st.caption("FDA drug labels, their versions, and what changed. A learning project, not medical advice.")

labels = con.execute("SELECT set_id, brand_name, generic_name FROM dim_label ORDER BY generic_name, brand_name").df()
names = {r.set_id: f"{r.generic_name} · {r.brand_name}" for r in labels.itertuples()}
choice = st.selectbox("Label", list(names), format_func=names.get)

st.subheader("Versions")
st.dataframe(con.execute("""SELECT version, valid_from, valid_to, is_current
                            FROM fact_label_version WHERE set_id = ? ORDER BY version""", [choice]).df())

st.subheader("What changed")
changes = con.execute("""SELECT version, section FROM fact_section_change
                         WHERE set_id = ? AND change_type = 'CHANGED' ORDER BY version DESC""", [choice]).df()
if changes.empty:
    st.write("No section has changed yet. Changes appear once the label gets a new version.")
else:
    st.dataframe(changes)

st.subheader("Search the current labels")
query = st.text_input("Which labels talk about ...", "liver injury")
if query:
    vector = next(iter(embedder.query_embed(query))).tolist()
    for row in search(con, vector).itertuples():
        shared = f" (same text in {row.labels_sharing - 1} other labels)" if row.labels_sharing > 1 else ""
        st.markdown(f"**{row.generic_name} · {row.brand_name}** — {row.section}, version {row.version}, "
                    f"match {row.score:.2f}{shared}")
        with st.expander("Section text"):
            st.write(row.text or "(empty)")
