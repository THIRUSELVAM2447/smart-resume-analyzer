import io
from pathlib import Path

import fitz
import pytesseract
from PIL import Image


# Configure Tesseract explicitly so the application does not depend
# on the Windows PATH environment variable.
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class PDFExtractionError(Exception):
    """
    Raised when a PDF file cannot be found, opened, or processed.
    """

    pass


OCR_RENDER_ZOOM = 2.0


class PDFService:
    """
    Stateless PDF text extraction service.

    Extraction order:

    1. Try normal embedded-text extraction using PyMuPDF.
    2. If no meaningful text is found, fall back to local OCR.
    3. Return the extracted text as plain text.

    This service does not:
    - parse resume structure
    - access the database
    - create ResumeVersion records
    - call external/cloud AI services
    """

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF.

        Normal text extraction is attempted first.
        OCR is used only when no meaningful embedded text exists.

        Raises:
            PDFExtractionError:
                If the PDF cannot be found, opened, extracted,
                or OCR cannot produce meaningful text.
        """

        path = Path(file_path)

        if not path.exists():
            raise PDFExtractionError(
                "PDF file not found on disk."
            )

        try:
            document = fitz.open(str(path))
        except Exception as exc:
            raise PDFExtractionError(
                "Failed to open PDF file."
            ) from exc

        try:
            # ---------------------------------------------------------
            # STEP 1: Normal embedded-text extraction
            # ---------------------------------------------------------
            text = self._extract_embedded_text(document)

            if self._is_meaningful(text):
                return text

            # ---------------------------------------------------------
            # STEP 2: OCR fallback
            # ---------------------------------------------------------
            ocr_text = self._extract_text_via_ocr(document)

            if self._is_meaningful(ocr_text):
                return ocr_text

            raise PDFExtractionError(
                "No meaningful text could be extracted from this PDF, "
                "even after OCR."
            )

        finally:
            document.close()

    def _extract_embedded_text(
        self,
        document: "fitz.Document",
    ) -> str:
        """
        Extract normal embedded text from every PDF page.
        """

        try:
            page_texts = [
                page.get_text()
                for page in document
            ]

        except Exception as exc:
            raise PDFExtractionError(
                "Failed to extract text from PDF."
            ) from exc

        return "\n".join(page_texts).strip()

    def _extract_text_via_ocr(
        self,
        document: "fitz.Document",
    ) -> str:
        """
        Render every PDF page to an in-memory image and run
        Tesseract OCR.

        No temporary image files are created.
        """

        try:
            page_ocr_texts = []

            matrix = fitz.Matrix(
                OCR_RENDER_ZOOM,
                OCR_RENDER_ZOOM,
            )

            for page in document:

                # Render PDF page to an in-memory pixmap.
                pixmap = page.get_pixmap(
                    matrix=matrix
                )

                # Convert rendered page to PNG bytes.
                image_bytes = pixmap.tobytes("png")

                # Release pixmap as soon as possible.
                pixmap = None

                # Open image from memory.
                with io.BytesIO(image_bytes) as buffer:

                    with Image.open(buffer) as image:

                        text = pytesseract.image_to_string(
                            image,
                            lang="eng",
                        )

                        page_ocr_texts.append(text)

            return "\n".join(page_ocr_texts).strip()

        except Exception as exc:
            raise PDFExtractionError(
                "Failed to extract text from PDF via OCR."
            ) from exc

    def _is_meaningful(self, text: str) -> bool:
        """
        Determine whether extracted text contains actual content.

        We intentionally do not use a minimum character count here.
        This preserves the original behavior: any non-whitespace
        extracted text is considered meaningful.
        """

        return bool(text.strip())