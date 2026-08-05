"""
==========================================================
Incident Knowledge Assistant

pages/Knowledge_Base.py

Author : Pramod Prakash Jadhav
==========================================================

Knowledge Base Page
"""

import streamlit as st

from src.logger import get_logger

logger = get_logger()


# ==========================================================
# Knowledge Base Page
# ==========================================================

def show_page(pipeline):
    """
    Display knowledge base information.
    """

    st.title("📚 Knowledge Base")

    st.markdown(
        """
Browse information about the indexed knowledge base
used by the Retrieval-Augmented Generation (RAG)
pipeline.
"""
    )

    st.markdown("---")

    # ------------------------------------------------------
    # Pipeline Information
    # ------------------------------------------------------

    st.subheader("Pipeline Information")

    try:

        info = pipeline.get_pipeline_info()

        st.json(info)

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

    st.markdown("---")

    # ------------------------------------------------------
    # Knowledge Base Status
    # ------------------------------------------------------

    st.subheader("Knowledge Base Status")

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            "Retriever initialized"
        )

    with col2:

        st.success(
            "LLM initialized"
        )

    st.info(
        "Knowledge Base is ready for semantic search."
    )
    # ------------------------------------------------------
    # Search Knowledge Base
    # ------------------------------------------------------

    st.subheader("🔍 Search Knowledge Base")

    keyword = st.text_input(
        "Search by keyword",
        placeholder="Example: password, VPN, incident"
    )

    try:

        if keyword.strip():

            documents = pipeline.retriever.search_documents(
                keyword
            )

        else:

            documents = pipeline.retriever.list_documents()

    except Exception as error:

        logger.exception(
            "Knowledge Base search failed."
        )

        st.error(
            "Unable to load indexed documents."
        )

        with st.expander(
            "Technical Details"
        ):

            st.exception(error)

        return

    st.markdown("---")

    # ------------------------------------------------------
    # Indexed Documents
    # ------------------------------------------------------

    st.subheader("📄 Indexed Documents")

    if not documents:

        st.info(
            "No documents found."
        )

        return

    st.caption(
        f"{len(documents)} document(s) found."
    )

    for item in documents:

        index = item["index"]

        text = item["document"]

        preview = (
            text[:200] + "..."
            if len(text) > 200
            else text
        )

        with st.expander(
            f"Document {index}"
        ):

            st.write(preview)

            st.caption(
                f"Length : {len(text)} characters"
            )
    # ------------------------------------------------------
    # Document Preview
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("📖 Document Preview")

    document_ids = [
        item["index"]
        for item in documents
    ]

    selected_id = st.selectbox(
        "Select Document",
        options=document_ids,
        format_func=lambda x: f"Document {x}"
    )

    try:

        selected_document = (
            pipeline.retriever.get_document(
                selected_id
            )
        )

        text = selected_document[
            "document"
        ]

        st.text_area(
            "Document Content",
            value=text,
            height=300,
            disabled=True,
        )

    except Exception as error:

        logger.exception(
            "Unable to load document."
        )

        st.error(
            "Failed to load document."
        )

        with st.expander(
            "Technical Details"
        ):

            st.exception(error)

        return

    # ------------------------------------------------------
    # Document Statistics
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("📊 Document Statistics")

    words = len(text.split())

    characters = len(text)

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Words",
            words
        )

    with col2:

        st.metric(
            "Characters",
            characters
        )

    st.caption(
        f"Document ID : {selected_id}"
    )
    # ------------------------------------------------------
    # Export Knowledge Base
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("⬇ Export")

    export_text = "\n\n".join(
        item["document"]
        for item in documents
    )

    st.download_button(

        label="Download Knowledge Base",

        data=export_text,

        file_name="knowledge_base.txt",

        mime="text/plain",

        use_container_width=True,

    )

    # ------------------------------------------------------
    # Refresh View
    # ------------------------------------------------------

    if st.button(

        "🔄 Refresh",

        use_container_width=True

    ):

        st.rerun()

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("Summary")

    st.success(
        f"Knowledge Base contains {len(documents)} indexed document(s)."
    )

    # ------------------------------------------------------
    # Footer
    # ------------------------------------------------------

    st.markdown("---")

    st.caption(
        "Powered by FAISS • Sentence Transformers • Ollama"
    )

    logger.info(
        "Knowledge Base page rendered successfully."
    )
