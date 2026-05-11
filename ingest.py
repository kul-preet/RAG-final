'''
This file will take the documents from the DOCUMENT folder
and call injestion on each file type and save them to the chroma db
'''

import os
import sys
from ingestion.pdf_processor import read_pdf
from ingestion.image_processor import describe_image
from ingestion.url_processor import read_url
from vectorstore.chroma_store import save_documents
import config

IMAGE_EXTENSIONS = [".jpg", ""]
