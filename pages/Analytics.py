"""
==========================================================
Incident Knowledge Assistant (RAG)

pages/Analytics.py

Author : Pramod Prakash Jadhav
==========================================================

Analytics Dashboard
"""

import streamlit as st

from src.logger import get_logger

logger = get_logger()


# ==========================================================
# Analytics Page
# ==========================================================

def show_page(
    pipeline,
):
    """
    Display pipeline analytics.
    """

    st.title("📈 Analytics")

    st.markdown(
        """
Monitor the Retrieval-Augmented Generation (RAG)
pipeline and vector database statistics.
"""
    )

    st.markdown("---")

    # ------------------------------------------------------
    # Pipeline Information
    # ------------------------------------------------------

    st.subheader(
        "🛠 Pipeline Overview"
    )

    try:

        pipeline_info = (
            pipeline.get_pipeline_info()
        )

    except Exception as error:

        logger.exception(
            "Unable to load pipeline information."
        )

        st.error(
            "Pipeline information is unavailable."
        )

        with st.expander(
            "Technical Details"
        ):

            st.exception(error)

        return

    st.json(
        pipeline_info
    )

    st.markdown("---")

    # ------------------------------------------------------
    # Quick Summary
    # ------------------------------------------------------

    st.subheader(
        "📊 Quick Summary"
    )

    retriever_info = (
        pipeline.retriever.get_retrieval_info()
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Documents",
            retriever_info.get(
                "documents",
                0
            ),
        )

    with col2:

        st.metric(
            "Vectors",
            retriever_info.get(
                "vectors",
                0
            ),
        )

    with col3:

        st.metric(
            "Dimension",
            retriever_info.get(
                "dimension",
                0
            ),
)
          # ------------------------------------------------------
    # Retrieval Configuration
    # ------------------------------------------------------

    st.subheader(
        "⚙️ Retrieval Configuration"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Embedding Model",
            retriever_info.get(
                "embedding_model",
                "Unknown"
            ),
        )

        st.metric(
            "Default Top-K",
            retriever_info.get(
                "default_top_k",
                0
            ),
        )

    with col2:

        loaded = retriever_info.get(
            "loaded",
            False
        )

        status = (
            "Loaded"
            if loaded
            else "Not Loaded"
        )

        st.metric(
            "FAISS Index",
            status,
        )

        st.metric(
            "Vector Dimension",
            retriever_info.get(
                "dimension",
                0
            ),
        )

    st.markdown("---")

    # ------------------------------------------------------
    # Vector Store Details
    # ------------------------------------------------------

    st.subheader(
        "🗂 Vector Store Details"
    )

    details = {

        "Indexed Documents":
            retriever_info.get(
                "documents",
                0
            ),

        "Stored Vectors":
            retriever_info.get(
                "vectors",
                0
            ),

        "Embedding Dimension":
            retriever_info.get(
                "dimension",
                0
            ),

        "Embedding Model":
            retriever_info.get(
                "embedding_model",
                "Unknown"
            ),

        "Default Top-K":
            retriever_info.get(
                "default_top_k",
                0
            ),

        "Index Loaded":
            retriever_info.get(
                "loaded",
                False
            ),

    }

    st.json(details)
      # ------------------------------------------------------
    # System Health
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("🟢 System Health")

    loaded = retriever_info.get(
        "loaded",
        False
    )

    vectors = retriever_info.get(
        "vectors",
        0
    )

    documents = retriever_info.get(
        "documents",
        0
    )

    if loaded and vectors > 0 and documents > 0:

        st.success(
            "Vector Store is healthy and ready for retrieval."
        )

    else:

        st.warning(
            "Vector Store is not fully initialized."
        )

    # ------------------------------------------------------
    # Runtime Configuration
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("⚙ Runtime Configuration")

    runtime_data = {

        "Embedding Model":
            retriever_info.get(
                "embedding_model",
                "Unknown"
            ),

        "Default Top-K":
            retriever_info.get(
                "default_top_k",
                0
            ),

        "Indexed Documents":
            documents,

        "Stored Vectors":
            vectors,

        "Embedding Dimension":
            retriever_info.get(
                "dimension",
                0
            ),

        "Index Loaded":
            loaded,

    }

    st.dataframe(
        runtime_data.items(),
        use_container_width=True,
    )

    # ------------------------------------------------------
    # Analytics Notes
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("📝 Notes")

    st.info(
        """
Current analytics are generated directly from the
loaded FAISS vector store and retriever configuration.

Historical usage statistics (search history,
response times, query trends, etc.) are not yet
implemented in the current version.
"""
  )
      # ------------------------------------------------------
    # Export Analytics
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("⬇ Export Analytics")

    export_data = {
        "pipeline": pipeline_info,
        "retriever": retriever_info,
    }

    st.download_button(
        label="⬇ Download Analytics (JSON)",
        data=str(export_data),
        file_name="analytics_summary.json",
        mime="application/json",
        use_container_width=True,
    )

    # ------------------------------------------------------
    # Refresh Dashboard
    # ------------------------------------------------------

    if st.button(
        "🔄 Refresh Analytics",
        use_container_width=True,
    ):

        logger.info(
            "Refreshing analytics page."
        )

        st.rerun()

    # ------------------------------------------------------
    # Footer
    # ------------------------------------------------------

    st.markdown("---")

    st.caption(
        "📊 Analytics generated from the current RAG pipeline configuration."
    )

    logger.info(
        "Analytics page rendered successfully."
  )
