"""
==========================================================
Incident Knowledge Assistant

pages/Incident_Search.py

Author : Pramod Prakash Jadhav
==========================================================

Incident Search Page
"""

import streamlit as st

from src.logger import get_logger

logger = get_logger()


# ==========================================================
# Incident Search Page
# ==========================================================

def show_page(
    pipeline,
    add_chat,
):
    """
    Incident Search Interface.
    """

    st.title("🔍 Incident Search")

    st.markdown(
        """
Search your knowledge base using natural language.

The RAG pipeline will:

1. Retrieve relevant documents

2. Build context

3. Generate an AI-powered answer
"""
    )

    st.markdown("---")

    # ------------------------------------------------------
    # User Question
    # ------------------------------------------------------

    question = st.text_area(

        "Ask a question",

        placeholder=(
            "Example:\n"
            "How do I reset my password?\n"
            "How do I access VPN?\n"
            "What is a P1 incident?"
        ),

        height=150,

    )

    col1, col2 = st.columns([3, 1])

    with col1:

        top_k = st.slider(

            "Documents to Retrieve",

            min_value=1,

            max_value=10,

            value=3,

            step=1,

            help="Number of relevant documents retrieved from FAISS."

        )

    with col2:

        st.metric(

            "Pipeline",

            "Ready"

        )

    st.markdown("---")

    # ------------------------------------------------------
    # Search Trigger
    # ------------------------------------------------------

    search_clicked = st.button(

        "🔎 Search",

        use_container_width=True,

        type="primary",

  )
      # ------------------------------------------------------
    # Execute Search
    # ------------------------------------------------------

    if search_clicked:

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

            return

        try:

            logger.info("=" * 60)
            logger.info(
                "Incident search started."
            )
            logger.info("=" * 60)

            with st.spinner(
                "Searching knowledge base..."
            ):

                result = pipeline.ask(

                    question=question,

                    top_k=top_k

                )

            answer = result.get(
                "answer",
                ""
            )

            documents = result.get(
                "documents",
                []
            )

            context = result.get(
                "context",
                ""
            )

            document_count = result.get(
                "document_count",
                0
            )

            add_chat(
                question=question,
                answer=answer
            )

            logger.info(
                "Incident search completed successfully."
            )

            st.session_state.search_result = {

                "question": question,

                "answer": answer,

                "documents": documents,

                "context": context,

                "document_count": document_count,

            }

        except Exception as error:

            logger.exception(
                "Incident search failed."
            )

            st.error(
                "Unable to process your request."
            )

            with st.expander(
                "Technical Details"
            ):

                st.exception(error)

            return
              # ------------------------------------------------------
    # Display Search Result
    # ------------------------------------------------------

    if "search_result" in st.session_state:

        result = st.session_state.search_result

        st.markdown("---")

        st.subheader("🤖 AI Response")

        st.success(
            result["answer"]
        )

        # --------------------------------------------------
        # Retrieval Statistics
        # --------------------------------------------------

        st.markdown("### 📊 Retrieval Summary")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Documents Retrieved",
                result["document_count"]
            )

        with col2:

            st.metric(
                "Question Length",
                len(result["question"])
            )

        # --------------------------------------------------
        # Retrieved Documents
        # --------------------------------------------------

        st.markdown("---")

        st.subheader("📄 Retrieved Documents")

        documents = result.get(
            "documents",
            []
        )

        if documents:

            for index, document in enumerate(
                documents,
                start=1
            ):

                with st.expander(
                    f"Document {index}"
                ):

                    distance = document.get(
                        "distance",
                        None
                    )

                    if distance is not None:

                        st.caption(
                            f"Similarity Distance: {distance:.4f}"
                        )

                    st.write(
                        document.get(
                            "document",
                            "No document text available."
                        )
                    )

        else:

            st.info(
                "No supporting documents were retrieved."
            )

        # --------------------------------------------------
        # Context Used
        # --------------------------------------------------

        st.markdown("---")

        with st.expander(
            "📚 Context Used for LLM"
        ):

            context = result.get(
                "context",
                ""
            )

            if context:

                st.text_area(
                    "Retrieved Context",
                    value=context,
                    height=250,
                    disabled=True,
                )

            else:

                st.info(
                    "No context available."
  )
                  # ------------------------------------------------------
    # Conversation History
    # ------------------------------------------------------

    st.markdown("---")

    st.subheader("💬 Conversation History")

    history = st.session_state.get(
        "chat_history",
        []
    )

    if history:

        for index, item in enumerate(
            reversed(history),
            start=1
        ):

            with st.expander(
                f"Question {len(history)-index+1}"
            ):

                st.markdown(
                    "**Question**"
                )

                st.write(
                    item["question"]
                )

                st.markdown(
                    "**Answer**"
                )

                st.write(
                    item["answer"]
                )

    else:

        st.info(
            "No conversation history available."
        )

    # ------------------------------------------------------
    # Export Result
    # ------------------------------------------------------

    if "search_result" in st.session_state:

        export_text = f"""
Question:
{result['question']}

Answer:
{result['answer']}

Documents Retrieved:
{result['document_count']}

Context:

{result['context']}
"""

        st.download_button(

            label="⬇ Download Search Result",

            data=export_text,

            file_name="incident_search_result.txt",

            mime="text/plain",

            use_container_width=True,

        )

    # ------------------------------------------------------
    # Clear Search
    # ------------------------------------------------------

    if st.button(
        "🗑 Clear Current Search",
        use_container_width=True
    ):

        if "search_result" in st.session_state:

            del st.session_state[
                "search_result"
            ]

        st.rerun()

    # ------------------------------------------------------
    # Footer
    # ------------------------------------------------------

    st.markdown("---")

    st.caption(
        "Powered by FAISS + Sentence Transformers + Ollama"
    )

    logger.info(
        "Incident Search page rendered successfully."
  )
