from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a legal assistant helping non-lawyers understand contracts.
Use ONLY the contract excerpts below. Answer in plain, simple English.
If you spot penalty clauses, deadlines, or hidden fees — highlight them clearly.

Contract excerpts:
{context}

Question: {question}

Plain-English Answer:"""
)

def load_chain():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local(
        "legal_index", embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    return chain