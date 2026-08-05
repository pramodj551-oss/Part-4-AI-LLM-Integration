"""
==========================================================
Incident Knowledge Assistant (RAG)

app.py

Author : Pramod Prakash Jadhav
==========================================================
"""

import streamlit as st

from src.logger import get_logger
from src.rag_pipeline import RAGPipeline

from src.config import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
)

logger = get_logger()

# ======================================================
# Streamlit Configuration
# ======================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
)

# ======================================================
# Cache Pipeline
# ======================================================

@st.cache_resource(show_spinner=True)
def load_pipeline():
    """
    Load the RAG pipeline only once.
    """

    logger.info(
        "Loading RAG Pipeline..."
    )

    pipeline = RAGPipeline()

    logger.info(
        "Pipeline loaded successfully."
    )

    return pipeline
    # ======================================================
# Sidebar
# ======================================================

st.sidebar.title("🤖 Incident Knowledge Assistant")

st.sidebar.markdown("---")

st.sidebar.success(
    "Production-ready RAG Pipeline"
)

st.sidebar.info(
    """
    • Semantic Search

    • FAISS Vector Database

    • Sentence Transformers

    • Ollama LLM

    • Streamlit Dashboard
    """
)

st.sidebar.markdown("---")

# ======================================================
# Session State
# ======================================================

if "chat_history" not in st.session_state:

    st.session_state.chat_history = []

# ======================================================
# Load Pipeline
# ======================================================

try:

    pipeline = load_pipeline()

except Exception as error:

    st.error(
        "Unable to initialize the AI Assistant."
    )

    st.exception(error)

    st.stop()
    # ======================================================
# Main Interface
# ======================================================

st.title("🤖 Incident Knowledge Assistant")

st.caption(
    "Ask questions about incidents using the RAG knowledge base."
)

question = st.text_area(
    "Enter your question",
    height=120,
    placeholder="Example: How can I reset my password?",
)

col1, col2 = st.columns([1, 1])

with col1:

    ask_button = st.button(
        "🔍 Ask Assistant",
        use_container_width=True,
    )

with col2:

    clear_button = st.button(
        "🗑 Clear Chat",
        use_container_width=True,
    )

if clear_button:

    st.session_state.chat_history = []

    st.rerun()

# ======================================================
# Execute RAG Query
# ======================================================

if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching knowledge base..."
        ):

            try:

                result = pipeline.ask(
                    question=question
                )

                st.session_state.chat_history.append(
                    result
                )

            except Exception as error:

                logger.exception(
                    "RAG execution failed."
                )

                st.error(str(error))
                # ======================================================
# Display Conversation
# ======================================================

if st.session_state.chat_history:

    st.markdown("---")

    st.subheader("Conversation")

    for chat in reversed(
        st.session_state.chat_history
    ):

        st.markdown(
            f"### ❓ Question\n{chat['question']}"
        )

        st.markdown(
            f"### 🤖 Answer\n{chat['answer']}"
        )

        with st.expander(
            "Retrieved Documents",
            expanded=False,
        ):

            st.write(
                f"Documents Retrieved: "
                f"{chat['document_count']}"
            )

            for index, document in enumerate(
                chat["documents"],
                start=1,
            ):

                st.markdown(
                    f"**Document {index}**"
                )

                st.write(
                    document["document"]
                )

                st.caption(
                    f"Distance: "
                    f"{document['distance']:.4f}"
                )

        with st.expander(
            "Context Used",
            expanded=False,
        ):

            st.text(
                chat["context"]
            )

        st.markdown("---")

# ======================================================
# Footer
# ======================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Incident Knowledge Assistant"
)

st.sidebar.caption(
    "AI/LLM Integration - Part 4"
)

st.sidebar.caption(
    "Developed by Pramod Prakash Jadhav"
)
