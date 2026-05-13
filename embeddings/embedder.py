''' 
    This file converts the text to the vectors with the help of a modal
    that modal is stored locally and no api needed
    it takes text -> use modal -> converts the text to the 384 numbers
    This numbers will help in searching in chroma db
    
    It is downloaded one (90 mb) from hugging face
'''

import config
from sentence_transformers import SentenceTransformer

print ("Loading the embedding model")
model = SentenceTransformer(config.EMBEDDING_MODEL)


def embed_text (text):
    #creating the embeddings for the single string
    
    return model.encode(text).tolist()

    # "encode" runs the model and return numpy
    # "tolist" converts it to plain python list



def embed_many (texts):
    #converts the list of strings to the list of vertors
    '''
    embeddings = [
    array([0.1, 0.2, 0.3, ...]),
    array([0.4, 0.5, 0.6, ...]),
    array([0.7, 0.8, 0.9, ...])
    ]
    '''
    embeddings = model.encode(texts, show_progress_bar = True)
    result = []
    for emb in embeddings:
        result.append(emb.tolist())
        
    return result