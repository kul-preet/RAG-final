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

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
PDF_EXTENSION = ".pdf"

def ingest_all():
    folder = config.DOCUMENTS_FOLDER
    
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created the document folder {folder} .")
        print(f"Add your pdf and image files here an then run the ingest all again")
        return
    
    all_files = os.listdir(folder)
    
    if not all_files:
        print(f"No files found in the document folder {folder}.")
        return
    
    print(f"Found {len(all_files)} files in {folder}")
    
    total_chunks = 0
    for filename in all_files:
        file_path = os.path.join(folder,filename)
        if filename.startswith(".") or not os.path.isfile(file_path):
            continue
        
        extension = os.path.splitext(filename)[1].lower()
        
        print(f"Processing {filename}")
        
        try:
            if extension == PDF_EXTENSION:
                docs = read_pdf(file_path)
                save_documents(docs)
                total_chunks += len(docs)
                
            elif extension in IMAGE_EXTENSIONS:
                doc = describe_image(file_path)
                save_documents([doc])
                total_chunks += 1
            
            else:
                print(f"skipping unsupported file {filename}")
                
        except Exception as e:
            print(f"ERROR Processing file {filename} : {e}")
            
        print()
        
    print(f"Ingestion completed! Added the {total_chunks} total chunks")
    print(f"we can now run ask.py")
    
def ingest_url(url):
    print(f"Ingesting url {url}")
    docs = read_url(url)
    save_documents(docs)
    print(f"Done! Added {len(docs)} chunks from the URL")
    
if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "url":
        ingest_url(sys.argv[2])
    elif len(sys.argv) == 2:
        ingest_url(sys.argv[1])
    else:
        ingest_all()