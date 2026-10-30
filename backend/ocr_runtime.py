"""Portable OCR configuration and normalized image input."""
import io
import os
import shutil
import tempfile
from pathlib import Path
from PIL import Image, ImageOps


def configure_tesseract():
    import pytesseract
    explicit = os.getenv('TESSERACT_CMD')
    candidates = [explicit, shutil.which('tesseract')]
    if os.name == 'nt':
        for root in [os.getenv('ProgramFiles'), os.getenv('ProgramFiles(x86)'), os.getenv('LOCALAPPDATA')]:
            if root:
                candidates.extend([str(Path(root)/'Tesseract-OCR'/'tesseract.exe'), str(Path(root)/'Programs'/'Tesseract-OCR'/'tesseract.exe')])
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            pytesseract.pytesseract.tesseract_cmd = str(candidate)
            return str(candidate)
    raise pytesseract.TesseractNotFoundError()


def normalize_image(data):
    with Image.open(io.BytesIO(data)) as source:
        source.seek(0)
        image = ImageOps.exif_transpose(source)
        image.load()
        if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
            rgba = image.convert('RGBA')
            background = Image.new('RGBA', rgba.size, 'white')
            image = Image.alpha_composite(background, rgba).convert('RGB')
        else:
            image = image.convert('RGB')
        return image.copy()


def extract(data):
    image = normalize_image(data)
    if os.getenv('OCR_BACKEND', 'tesseract').strip().lower() == 'google':
        from ocr import extract_text_from_image
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return '\n'.join(extract_text_from_image(buffer.getvalue()))
    import pytesseract
    configure_tesseract()
    langs = pytesseract.get_languages(config='')
    available = [name for name in ('kor', 'eng') if name in langs]
    if not available:
        raise RuntimeError('OCR_LANGUAGE_MISSING: kor 또는 eng 언어 데이터가 필요합니다.')
    # Re-encode JPG/CMYK/palette/transparent inputs as a standard RGB PNG.
    with tempfile.TemporaryDirectory(prefix='study_ocr_') as temp:
        path = Path(temp)/'input.png'
        image.save(path, format='PNG')
        return pytesseract.image_to_string(str(path), lang='+'.join(available), config='--psm 6', timeout=90).strip()
