"""Incident Knowledge Assistant Streamlit application."""
import streamlit as st
from src.config import APPLICATION_VERSION, INITIAL_SIDEBAR_STATE, LAYOUT, PAGE_ICON, PAGE_TITLE
from src.conversation_memory import ConversationMemory
from src.document_upload import parse_uploads
from src.logger import get_logger
from src.rag_pipeline import RAGPipeline
from src.retriever import Retriever
from src.runtime import readiness_status, safe_user_error

logger = get_logger()
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT, initial_sidebar_state=INITIAL_SIDEBAR_STATE)

@st.cache_resource(show_spinner=True)
def load_pipeline():
    logger.info("Loading RAG Pipeline")
    pipeline = RAGPipeline()
    logger.info("RAG Pipeline loaded successfully")
    return pipeline

st.sidebar.title("🤖 Incident Knowledge Assistant")
st.sidebar.markdown("---")
st.sidebar.success("RAG application")
st.sidebar.info("• Semantic Search\n\n• FAISS Vector Database\n\n• Sentence Transformers\n\n• Groq LLM\n\n• Streamlit UI")
st.sidebar.caption(f"Version {APPLICATION_VERSION}")
st.sidebar.markdown("---")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = ConversationMemory()
if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []
if "uploaded_pipeline" not in st.session_state:
    st.session_state.uploaded_pipeline = None

try:
    base_pipeline = load_pipeline()
except Exception:
    logger.exception("RAG pipeline initialization failed")
    st.error(safe_user_error("Unable to initialize the AI Assistant. Please try again later."))
    st.stop()

with st.sidebar.expander("📄 Session Document Upload"):
    st.caption("TXT, MD or CSV • max 5 files • 1 MB each")
    uploads = st.file_uploader("Upload documents", type=["txt", "md", "csv"], accept_multiple_files=True)
    if st.button("Index Uploaded Documents", use_container_width=True):
        try:
            parsed = parse_uploads(uploads)
            if not parsed:
                st.warning("Select at least one document.")
            else:
                st.session_state.uploaded_documents = parsed
                texts = [item.text for item in parsed]
                st.session_state.uploaded_pipeline = RAGPipeline(
                    retriever=Retriever.from_documents(texts),
                    llm=base_pipeline.llm,
                )
                st.success(f"Indexed {len(parsed)} document(s) for this session.")
        except Exception as exc:
            logger.warning("Document upload rejected: %s", type(exc).__name__)
            st.error(safe_user_error(str(exc)))
    if st.session_state.uploaded_documents:
        st.caption(f"Session index: {len(st.session_state.uploaded_documents)} document(s)")
        if st.button("Remove Uploaded Documents", use_container_width=True):
            st.session_state.uploaded_documents = []
            st.session_state.uploaded_pipeline = None
            st.rerun()

pipeline = st.session_state.uploaded_pipeline or base_pipeline
status = readiness_status(pipeline, APPLICATION_VERSION)
if status.status != "ready":
    st.error("The AI Assistant is currently not ready.")
    st.stop()

st.title("🤖 Incident Knowledge Assistant")
st.caption("Ask questions about incidents using the RAG knowledge base.")
if st.session_state.uploaded_documents:
    st.info("Session documents are active. They are ephemeral and do not modify the persistent knowledge base.")

question = st.text_area("Enter your question", height=120, placeholder="Example: How can I reset my password?")
col1, col2 = st.columns([1, 1])
with col1:
    ask_button = st.button("🔍 Ask Assistant", use_container_width=True)
with col2:
    clear_button = st.button("🗑 Clear Chat", use_container_width=True)

if clear_button:
    st.session_state.chat_history = []
    st.session_state.conversation_memory.clear()
    st.rerun()

if ask_button:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching knowledge base..."):
            try:
                history = st.session_state.conversation_memory.format_for_prompt()
                result = pipeline.ask(question=question, conversation_history=history)
                st.session_state.chat_history.append(result)
                st.session_state.conversation_memory.add(result["question"], result["answer"])
            except Exception:
                logger.exception("RAG execution failed")
                st.error(safe_user_error("Unable to process the request. Please try again."))

if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("Conversation")
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"### ❓ Question\n{chat['question']}")
        st.markdown(f"### 🤖 Answer\n{chat['answer']}")
        with st.expander("Retrieved Documents", expanded=False):
            st.write(f"Documents Retrieved: {chat['document_count']}")
            for index, document in enumerate(chat["documents"], start=1):
                st.markdown(f"**Document {index}**")
                st.write(document["document"])
                st.caption(f"Distance: {document['distance']:.4f}")
        with st.expander("Context Used", expanded=False):
            st.text(chat["context"])
        st.markdown("---")

st.sidebar.caption(f"Memory: {len(st.session_state.conversation_memory)}/5 turns")
st.sidebar.caption("Incident Knowledge Assistant")
st.sidebar.caption("AI/LLM Integration - Part 4")
st.sidebar.caption("Developed by Pramod Prakash Jadhav")
