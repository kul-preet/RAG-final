"""
What this file do?
    Connects to the chroma db
    save-documents()  = store_text + vectors+ metadata
    search()  ->        search for the  question by matching embeddings
    count()  ->         count the number of chunks stored
    clear() ->          to clear the entries in the db    
    
    """
    
import uuid
import chromadb
import config
from embeddings.embedder import embed_text, embed_many


#step 1 :- create a client and fetch collections
client = chromadb.persistantClient(path=config.CHROMA_DIR)
collection = client.get_or_create_collection(
    name = config.CHROMA_COLLECTION_NAME,
    embedding_fnmetadata={"hnsw:space": "cosine"}
    # "cosine" means: measure similarity using the angle between vectors
    # (standard for text embeddings)
)

#--------------SAVING LOGIC----------------------
def save_documents(documents):
    # store a document dict in chroma db
    # each document will be having 
    #       Text -> the text to be embde to store
    #       metadata -> the dict of info about the store
    if not documents:
        print("No document file found")
        return
    
    # texts = ["Hello", "World"]
    # metadatas = [{"page": 1}, {"page": 2}]
    
    #extracting the text from the document
    texts = []
    for doc in documents:
        texts.append(doc["text"])
        
    # extracting the metadata from the document
    metadatas = []
    for doc in documents:
        metadatas.append(doc["metadata"])
        

    #chromadb only accept the string,bool,numbers as a metadata
    #need to conver the metadata to the string,bool, number
    clean_metadata = []
    for meta in metadatas:
        clean = {}z
        for key,value in meta.items():              # key="page", value=2
            if value is none:                       # key="tags", value=["AI", "ML"]
                clean[key] = ""
            elif isinstance(value, (list,dict)):
                clean[key] = str(value)
            else:
                clean[key] = str[value]
        clean_metadata.append(clean)
        
    
    ids = []
    for _  in documents:            # 👉 _ means: "I don’t care about the variable, just repeat"
        ids.append(str(uuid.uuid4()))
    #uuid created random id
    
    print(f"Embedding {len(text)} chunks")
    embeddings = embed_many(texts)
    
    #save everyting to the chromadb
    collection.add(
        ids = ids
        embeddings = embeddings
        documents = texts,
        metadatas = clean_metadata
    )
    
    print(f"saved the {len(documents)} to the chromaDB")
    
    
    


#step 3 :- search 
#search for text in db
def search(query, top_k = config.TOP_K):
    #embed the question
    query_vector = embed_text(query)
    
    results = collection.query(
    #checking for the close matches in chromadb
    query_embeddings = [query_vector], #wrapped in a list for multiple batches
    n_results = min(top_k , collection.count()),  #min prevents for asking more results than existing
    include = ["documents", "metadatas", "distan3ces"]
    )
    
    output = []
    for text,meta,distance in zip(
        results["documents"][0]
        results["metadatas"][0]
        results["distances"][0]
    ):
        # ChromaDB returns "distance" (lower = more similar)
        # We convert to "score" (higher = more similar) by: score = 1 - distance
        score = round(1 - distance, 3)  # 3 represents the 3decmals 0.987
        
        output.append({
            "text":     text,
            "metadata": meta,
            "score":    score
        })
 
    return output
    


#step 4 count()
#return total number of chunks in db
def count():
    return collection.count()


#step 5 clear()
#clear the entries in the db
def clear():
    all_ids = collection.get()["ids"]
    if all_ids:
        collection.delete(ids = all_ids)
    print("database cleared")