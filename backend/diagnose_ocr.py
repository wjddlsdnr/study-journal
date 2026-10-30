import os,sys,traceback
from pathlib import Path
from ocr_runtime import configure_tesseract,extract
try:
 import pytesseract
 print('OCR_BACKEND:',os.getenv('OCR_BACKEND','tesseract'))
 print('Tesseract:',configure_tesseract())
 print('Version:',pytesseract.get_tesseract_version())
 print('Languages:',pytesseract.get_languages(config=''))
 print('TESSDATA_PREFIX:',os.getenv('TESSDATA_PREFIX','(not set)'))
 if len(sys.argv)>1:
  path=Path(sys.argv[1]);text=extract(path.read_bytes());print('OCR success. Extracted characters:',len(text))
 else:
  print('Image test: py diagnose_ocr.py "C:\\path\\rfic 5.jpg"')
except Exception:
 traceback.print_exc()
 sys.exit(1)
