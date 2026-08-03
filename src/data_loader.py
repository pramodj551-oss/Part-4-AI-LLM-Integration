"""
==========================================================
Incident Knowledge Assistant (RAG)

data_loader.py

Author : Pramod Prakash Jadhav
==========================================================

Load, validate and prepare the incident knowledge dataset.
"""

from pathlib import Path

import pandas as pd

from src.config import DATASET_PATH
from src.logger import get_logger

logger = get_logger()


class DataLoader:
    """
    Load and prepare the incident knowledge dataset.
    """

    def __init__(
        self,
        dataset_path=DATASET_PATH
    ):

        self.dataset_path = Path(dataset_path)

        self.dataframe = pd.DataFrame()

    # ======================================================
    # Load Dataset
    # ======================================================

    def load_data(self):
        """
        Load dataset from CSV.

        Returns
        -------
        pandas.DataFrame
            Loaded dataset.
        """

        logger.info("=" * 60)
        logger.info("Loading incident dataset")
        logger.info("=" * 60)

        if not self.dataset_path.exists():

            raise FileNotFoundError(
                f"Dataset not found: "
                f"{self.dataset_path}"
            )

        self.dataframe = pd.read_csv(
            self.dataset_path,
            encoding="utf-8"
        )

        logger.info(
            f"Dataset loaded successfully."
        )

        logger.info(
            f"Shape : {self.dataframe.shape}"
        )

        logger.info(
            f"Columns : "
            f"{list(self.dataframe.columns)}"
        )

        return self.dataframe
      # ======================================================
    # Validate Dataset
    # ======================================================

    def validate_dataset(self):
        """
        Validate the loaded dataset.

        Returns
        -------
        bool
            True if validation succeeds.
        """

        logger.info("Validating dataset...")

        if self.dataframe.empty:

            raise ValueError(
                "Loaded dataset is empty."
            )

        required_columns = [
            "title",
            "category",
            "severity",
            "description",
            "resolution",
        ]

        missing_columns = [

            column

            for column in required_columns

            if column not in self.dataframe.columns

        ]

        if missing_columns:

            raise ValueError(
                "Missing required columns: "
                f"{missing_columns}"
            )

        logger.info(
            "Dataset validation completed successfully."
        )

        return True

    # ======================================================
    # Remove Duplicate Records
    # ======================================================

    def remove_duplicates(self):
        """
        Remove duplicate records.
        """

        duplicate_count = (
            self.dataframe.duplicated().sum()
        )

        if duplicate_count > 0:

            self.dataframe.drop_duplicates(
                inplace=True,
                ignore_index=True
            )

            logger.info(
                f"Removed {duplicate_count} duplicate rows."
            )

        else:

            logger.info(
                "No duplicate records found."
            )

        return self.dataframe

    # ======================================================
    # Handle Missing Values
    # ======================================================

    def handle_missing_values(self):
        """
        Fill missing values in text columns.
        """

        logger.info(
            "Handling missing values..."
        )

        missing_count = (
            self.dataframe.isnull().sum().sum()
        )

        if missing_count == 0:

            logger.info(
                "No missing values found."
            )

            return self.dataframe

        text_columns = self.dataframe.select_dtypes(
            include=["object"]
        ).columns

        for column in text_columns:

            self.dataframe[column] = (
                self.dataframe[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        logger.info(
            "Missing values handled successfully."
        )

        return self.dataframe
      # ======================================================
    # Clean Text
    # ======================================================

    def clean_text(
        self,
        text: str
    ) -> str:
        """
        Clean text for embedding generation.

        Parameters
        ----------
        text : str
            Input text.

        Returns
        -------
        str
            Cleaned text.
        """

        if pd.isna(text):

            return ""

        cleaned_text = (
            str(text)
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("\t", " ")
            .strip()
        )

        cleaned_text = " ".join(
            cleaned_text.split()
        )

        return cleaned_text

    # ======================================================
    # Prepare Documents
    # ======================================================

    def prepare_documents(self):
        """
        Prepare incident documents for
        embedding generation.

        Returns
        -------
        list
            List of formatted documents.
        """

        logger.info(
            "Preparing documents..."
        )

        documents = []

        for _, row in self.dataframe.iterrows():

            title = self.clean_text(
                row.get("title", "")
            )

            category = self.clean_text(
                row.get("category", "")
            )

            severity = self.clean_text(
                row.get("severity", "")
            )

            description = self.clean_text(
                row.get("description", "")
            )

            resolution = self.clean_text(
                row.get("resolution", "")
            )

            document = (
                f"Title: {title}\n"
                f"Category: {category}\n"
                f"Severity: {severity}\n"
                f"Description: {description}\n"
                f"Resolution: {resolution}"
            )

            documents.append(document)

        logger.info(
            f"Prepared {len(documents)} documents."
        )

        return documents

    # ======================================================
    # Dataset Summary
    # ======================================================

    def get_dataset_summary(self):
        """
        Generate dataset summary.

        Returns
        -------
        dict
            Dataset statistics.
        """

        summary = {

            "rows": len(self.dataframe),

            "columns": len(self.dataframe.columns),

            "missing_values": int(
                self.dataframe.isnull().sum().sum()
            ),

            "duplicate_rows": int(
                self.dataframe.duplicated().sum()
            ),

            "column_names": list(
                self.dataframe.columns
            ),
        }

        logger.info(
            "Dataset summary generated."
        )

        return summary
      # ======================================================
    # Search Records
    # ======================================================

    def search_records(
        self,
        keyword: str
    ):
        """
        Search records using a keyword.

        Parameters
        ----------
        keyword : str

        Returns
        -------
        pandas.DataFrame
        """

        if not keyword.strip():

            return self.dataframe

        keyword = keyword.lower()

        mask = self.dataframe.astype(str).apply(
            lambda column:
            column.str.lower().str.contains(
                keyword,
                na=False
            )
        ).any(axis=1)

        results = self.dataframe.loc[
            mask
        ].reset_index(drop=True)

        logger.info(
            f"Search returned {len(results)} records."
        )

        return results

    # ======================================================
    # Export Dataset
    # ======================================================

    def export_dataset(
        self,
        output_path
    ):
        """
        Export processed dataset.

        Parameters
        ----------
        output_path : str | Path
        """

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.dataframe.to_csv(
            output_path,
            index=False,
            encoding="utf-8"
        )

        logger.info(
            f"Dataset exported to {output_path}"
        )


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    logger.info("=" * 60)
    logger.info("Data Loader Demonstration")
    logger.info("=" * 60)

    try:

        loader = DataLoader()

        dataframe = loader.load_data()

        loader.validate_dataset()

        loader.remove_duplicates()

        loader.handle_missing_values()

        documents = loader.prepare_documents()

        summary = loader.get_dataset_summary()

        logger.info("=" * 60)
        logger.info("Dataset Summary")

        for key, value in summary.items():

            logger.info(f"{key}: {value}")

        logger.info("=" * 60)
        logger.info(
            f"Prepared Documents: {len(documents)}"
        )

        if documents:

            logger.info("Sample Document")

            logger.info(documents[0])

        logger.info("=" * 60)
        logger.info(
            "data_loader.py executed successfully."
        )
        logger.info("=" * 60)

    except Exception as error:

        logger.exception(
            "Data Loader execution failed."
        )

        raise error
