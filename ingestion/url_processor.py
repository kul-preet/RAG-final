"""
Downloading the web page and extracting the text content from it then return chunks.
FULL PIPELINE:
1. url
2. requests.get()
3. HTML
4. BeautifulSoup
5. remove junk
6. clean text
7. chunk text
8. attach metadata
9. return documents
"""

import requests  #Downloads the web page HTML
from bs4 import BeautifulSoup  #parse the above downloaded HTML
from ingestion.pdf_processor import split_into_chunks

def read_url(url):
    print(f"Reading URL: {url}")
    # set a user-agent header, without this, the request might be considered as a comming from bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()  #raise and error for bad status codes
    
    html = response.text #getting the raw html
    
    soup = BeautifulSoup(html, "lxml") #converts the raw html to the searchable format

    title_tag = soup.find("title")
    page_title = title_tag.get_text(strip=True) if title_tag else "No Title"
    
    #remove the useless tags
    for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
        tag.decompose() #decompose will completely remove the tags from the html    
    
    #find main content area
    main = (
        soup.find("main") or
        soup.find("article") or
        soup.find("body")
    )
    
    raw_text = main.get_text(separator="\n", strip=True)
    
    #clean up :- remove extra newlines and spaces
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    clean_line = [line for line in lines if len(line) > 2] #removing very short lines
    clean_text = "\n".join(clean_line)
    
    if not clean_text:
        print(f"No clean text found in the {url}")
        return []
    
    chunks = split_into_chunks(clean_text)
    
    all_docs = []
    for i,chunk in enumerate(chunks):
        all_docs.append({
            "text" : chunk,
            "metadata" : {
                "source_type" : "url",
                "url" :url,
                "page_title" : page_title,
                "chunk_index" : i
            }
        })
        
    print(f"Done, Got {len(all_docs)} chunks from the page'{page_title}'")
    
    return all_docs
    
