"""
==========================================================
Incident Knowledge Assistant

app.py

Author : Pramod Prakash Jadhav
==========================================================

Main Streamlit Application
"""

import streamlit as st

from src.logger import get_logger
from src.rag_pipeline import RAGPipeline

logger = get_logger()


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(

    page_title="Incident Knowledge Assistant",

    page_icon="🛡️",

    layout="wide",

    initial_sidebar_state="expanded"

)


# ==========================================================
# Cache Resources
# ==========================================================

@st.cache_resource
def load_pipeline():
    """
    Load RAG pipeline once and reuse it
    across Streamlit reruns.
    """

    logger.info(
        "Loading RAG Pipeline..."
    )

    pipeline = RAGPipeline()

    logger.info(
        "RAG Pipeline loaded successfully."
    )

    return pipeline


# ==========================================================
# Initialize Pipeline
# ==========================================================

try:

    pipeline = load_pipeline()

except Exception as error:

    st.error(
        "Unable to initialize the AI Assistant."
    )

    st.exception(error)

    st.stop()


# ==========================================================
# Session State
# ==========================================================

if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


if "last_question" not in st.session_state:

    st.session_state.last_question = ""


if "last_answer" not in st.session_state:

    st.session_state.last_answer = ""


# ==========================================================
# Helper Functions
# ==========================================================

def add_chat(question, answer):
    """
    Store conversation history.
    """

    st.session_state.chat_history.append(

        {

            "question": question,

            "answer": answer

        }

    )

    st.session_state.last_question = question

    st.session_state.last_answer = answer


def clear_chat():
    """
    Clear conversation history.
    """

    st.session_state.chat_history = []

    st.session_state.last_question = ""

    st.session_state.last_answer = ""

    logger.info(
        "Chat history cleared."
  )
  # ==========================================================
# Sidebar
# ==========================================================

with st.sidebar:

    st.title("🛡 Incident Knowledge Assistant")

    st.caption(
        "AI-Powered Incident Response using RAG"
    )

    st.markdown("---")

    # ------------------------------------------------------
    # Navigation
    # ------------------------------------------------------

    page = st.radio(

        "Navigation",

        [

            "🏠 Home",

            "🔍 Incident Search",

            "📚 Knowledge Base",

            "📈 Analytics",

            "ℹ About"

        ]

    )

    st.markdown("---")

    # ------------------------------------------------------
    # Pipeline Health
    # ------------------------------------------------------

    st.subheader("System Status")

    try:

        health = pipeline.health_check()

        st.success("Pipeline Healthy")

        llm_info = health.get(
            "llm",
            {}
        )

        retriever_info = health.get(
            "retriever",
            {}
        )

        st.caption(
            f"Model : {llm_info.get('model', 'Unknown')}"
        )

        st.caption(
            f"Provider : {llm_info.get('provider', 'Unknown')}"
        )

        st.caption(
            f"Documents : "
            f"{retriever_info.get('documents', 0)}"
        )

        st.caption(
            f"Vectors : "
            f"{retriever_info.get('vectors', 0)}"
        )

    except Exception:

        st.error(
            "Pipeline Health Check Failed"
        )

    st.markdown("---")

    # ------------------------------------------------------
    # Conversation
    # ------------------------------------------------------

    st.subheader("Conversation")

    st.metric(

        "Questions Asked",

        len(
            st.session_state.chat_history
        )

    )

    if st.button(

        "🗑 Clear Chat",

        use_container_width=True

    ):

        clear_chat()

        st.success(
            "Conversation cleared."
        )

        st.rerun()

    st.markdown("---")

    # ------------------------------------------------------
    # Project Information
    # ------------------------------------------------------

    st.subheader("Project")

    st.caption(
        "Version : 1.0"
    )

    st.caption(
        "RAG + Ollama + FAISS"
    )

    st.caption(
        "Developer:"
    )

    st.caption(
        "Pramod Prakash Jadhav"
  )
  # ==========================================================
# Page Routing
# ==========================================================

try:

    if page == "🏠 Home":

        st.title(
            "🛡 Incident Knowledge Assistant"
        )

        st.markdown(
            """
Welcome to the **Incident Knowledge Assistant**.

This application uses a Retrieval-Augmented
Generation (RAG) pipeline to answer incident
response and knowledge base questions using
your internal documentation.

Use the navigation menu on the left to:

• Search incidents

• Explore the knowledge base

• View analytics

• Monitor pipeline health
"""
        )

        st.info(
            "Select **Incident Search** from the sidebar to begin."
        )

        if st.session_state.chat_history:

            st.markdown("---")

            st.subheader(
                "Recent Conversation"
            )

            recent = list(
                reversed(
                    st.session_state.chat_history[-5:]
                )
            )

            for item in recent:

                with st.expander(
                    item["question"]
                ):

                    st.markdown(
                        "**Answer**"
                    )

                    st.write(
                        item["answer"]
                    )

    elif page == "🔍 Incident Search":

        from pages.Incident_Search import (
            show_page,
        )

        show_page(
            pipeline=pipeline,
            add_chat=add_chat,
        )

    elif page == "📚 Knowledge Base":

        from pages.Knowledge_Base import (
            show_page,
        )

        show_page(
            pipeline=pipeline,
        )

    elif page == "📈 Analytics":

        from pages.Analytics import (
            show_page,
        )

        show_page(
            pipeline=pipeline,
        )

    elif page == "ℹ About":

        st.title("About")

        st.markdown(
            """
### Incident Knowledge Assistant

Production-ready Retrieval-Augmented
Generation (RAG) application.

Technology Stack

- Python

- Streamlit

- FAISS

- Sentence Transformers

- Ollama

- Retrieval-Augmented Generation

Developer

Pramod Prakash Jadhav
"""
        )

except Exception as error:

    logger.exception(
        "Application error."
    )

    st.error(
        "An unexpected error occurred."
    )

    with st.expander(
        "Technical Details"
    ):

        st.exception(error)
      # ==========================================================
# Footer
# ==========================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:

    st.caption(
        "🛡 Incident Knowledge Assistant"
    )

with col2:

    st.caption(
        "Version 1.0"
    )

with col3:

    st.caption(
        "Built with Streamlit + Ollama + FAISS"
    )


# ==========================================================
# Pipeline Summary
# ==========================================================

with st.expander(
    "Pipeline Summary"
):

    try:

        info = pipeline.get_pipeline_info()

        st.json(info)

    except Exception:

        st.info(
            "Pipeline information unavailable."
        )


# ==========================================================
# Startup Logging
# ==========================================================

logger.info("=" * 60)
logger.info(
    "Incident Knowledge Assistant started."
)
logger.info("=" * 60)


# ==========================================================
# End of Application
# ==========================================================
