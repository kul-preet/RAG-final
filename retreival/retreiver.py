""" 
here we will take user question
then build the context and search in chroma db
"""

from vectorstore.chroma_store import search
import config

def get_relevant_chunks(question, top_k = config.TOP_K):
    #search chroma db and return the top matching
    result = search(question, top_k = top_k)
    return results


def build_context (question, top_k = config.TOP_K):
    '''
    fetch relevant chunks and format them into single context
    Example output:
      [Source 1 - report.pdf (page 2) | score: 0.89]
      Revenue increased by 15% in Q3...
 
      [Source 2 - chart.png | score: 0.76]
      The bar chart shows quarterly sales with...
 
    Returns:
      context_text : the formatted string
      sources      : list of source dicts (for display to user)
    '''
    
    results = get_relevant_chunks(question, top_k)
    
    if not results:
        return "No relevant information found.", []
    
    context_parts = []
    sources       = []
    
    