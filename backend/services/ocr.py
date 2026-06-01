import fitz  # PyMuPDF
from PIL import Image, ImageEnhance
import pytesseract
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Tesseract path if provided in .env
tess_path = os.getenv("TESSERACT_PATH")
if tess_path:
    pytesseract.pytesseract.tesseract_cmd = tess_path


def extract_text_from_file(file_path: str) -> dict:
    """
    Extract text from PDF or image file.
    Returns dict with text and page count.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]:
        return _extract_from_image(file_path)
    else:
        return {"text": "", "pages": 0, "error": "Unsupported file type"}


def _preprocess_image(image: Image.Image) -> Image.Image:
    """Enhance image for better OCR results"""
    # Convert to grayscale
    image = image.convert("L")
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    return image


def _extract_from_pdf(file_path: str) -> dict:
    try:
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            text = page.get_text()
            # If page has no text (scanned), use OCR
            if not text.strip():
                pix = page.get_pixmap(dpi=300) # Increased DPI
                img_path = file_path + f"_page_{page.number}.png"
                pix.save(img_path)
                image = Image.open(img_path)
                image = _preprocess_image(image)
                text = pytesseract.image_to_string(image)
                os.remove(img_path)
            full_text += text + "\n"
        return {
            "text": full_text.strip(),
            "pages": len(doc),
            "error": None
        }
    except Exception as e:
        return {"text": "", "pages": 0, "error": str(e)}


def _extract_from_image(file_path: str) -> dict:
    try:
        image = Image.open(file_path)
        image = _preprocess_image(image)
        text = pytesseract.image_to_string(image)
        return {
            "text": text.strip(),
            "pages": 1,
            "error": None
        }
    except Exception as e:
        return {"text": "", "pages": 1, "error": str(e)}