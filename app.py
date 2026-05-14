from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from ingest import ingest
from rag_chain import load_chain

st.set_page_config(page_title="Legal Aid Lite", page_icon="⚖️")
st.title("⚖️ Legal Aid Lite")
st.caption("Upload a contract and ask questions in plain English")

uploaded_file = st.file_uploader("Upload a contract PDF", type="pdf")
if uploaded_file:
    os.makedirs("contracts", exist_ok=True)
    save_path = f"contracts/{uploaded_file.name}"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())
    if st.button("Index this document"):
        with st.spinner("Reading and indexing..."):
            ingest(save_path)
        st.success("Document indexed! Ask your questions below.")

st.divider()

question = st.text_input("Ask a question about the contract",
                          placeholder="What happens if I miss the payment deadline?")

if st.button("Analyse") and question:
    if not os.path.exists("legal_index"):
        st.error("Please upload and index a document first.")
    else:
        with st.spinner("Analysing contract..."):
            chain = load_chain()
            result = chain.invoke({"query": question})
        st.markdown("### Answer")
        st.write(result["result"])
        with st.expander("View source excerpts from contract"):
            for doc in result["source_documents"]:
                st.markdown(f"> {doc.page_content}")
                st.caption(f"Page {doc.metadata.get('page', '?')}")