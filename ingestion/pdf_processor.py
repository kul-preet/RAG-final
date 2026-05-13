'''
reads the pdf file and extract the data from it 
'''

import fitz  #this is PyMuPDF, imported as fitz
import tempfile
import os
import config
from ingestion.image_processor import describe_image

def split_into_chunks (text):
    #this will split the pdf content for precise searching 
    #overlaping so that the content don't get lost at the edges
    chunks = []
    start = 0
    
    while start< len(text):
        end = start+ config.CHUNK_SIZE
        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
            
        start += config.CHUNK_SIZE - config.CHUNK_OVERLAP
        
    return chunks


def read_pdf(pdf_path):
    ''' read PDF and return the data
    "TEXT" -> the content of pdf
    "METADATA" -> source info 
    '''
    print(f"reading pdf {pdf_path}")
    
    file_name = os.path.basename(pdf_path)
    all_docs = []
    
    pdf = fitz.open(pdf_path)
    print(f"PDF has {len(pdf)} pages")
    
    for page_num in range(len(pdf)):
        page = pdf(page_num)
        
        #----------EXTRACTing TEXT from page------------
        page_text = page.get_text().strip()
        if page_text:
            chunks = split_into_chunks(page_text)
            
            for i,chunk in enumerate (chunks):
                all_docs.append({
                    "text":chunk,
                    "metadata": {
                        "source_type" : "pdf",
                        "file_name" :file_name,
                        "file_path" : pdf_path,
                        "page_number" : page_num+1,
                        "chunk_index" : i,
                        
                    }
                })
                
        #-----EXTRACTING image from the page------------------
        image_on_page = page.get_images()
        
        for img_index, img_info in enumerate(image_on_page):
            xref = img_info[0]  #xref is the image's inside the PDF
            try:
                raw_image = pdf.extract_image(xref)
                image_bytes = raw_image["image"]
                image_ext = raw_image ["ext"]
                
                #skipping tiny images 
                if raw_image.get ("width",0) < 80 or raw_image.get("height",0) < 80:
                    continue
                
                tmp = tempfile.NamedTemporaryFile(
                    suffix = f".{image_ext}", delete = False
                )
                tmp.write(image_bytes)
                tmp.close()
                
                img_doc = describe_image(tmp.name)
                
                #update metadata to show this image
                img_doc["metadata"]["source_type"] = "pdf_image"
                img_doc["metadata"]["file_name"] = file_name
                img_doc["metadata"]["file_path"] = pdf_path
                img_doc["metadata"]["page_number"] = page_num + 1

                all_docs.append(img_doc)

                os.unlink(tmp.name)  # delete the temp file

            except Exception as e:
                print(f"  Could not process image on page {page_num + 1}: {e}")
                
    pdf.close()
    print(f"  Done. Got {len(all_docs)} chunks from {file_name}")
    return all_docs


                