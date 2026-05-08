import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_TEXT_MODEL = "llama-3.3-70b-versatile"
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  #groq model which will read the images 

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHROMA_DIR = "./chroma_db"
CHROMA_COLLECTION_NAME = "image_rag"

DOCUMENTS_FOLDER = "./documents"


#how many related chunks to get for answering
TOP_K = 3


#long text will be stored into chunks before sharing
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50