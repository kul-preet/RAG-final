""" 
here we will take user question
then build the context and search in chroma db
"""

from vectorstore.chroma_store import search
import config

def get_relevant_chunks(question, top_k = config.TOP_K):
    # search chroma db and return the top matching
    result = search(question, top_k = top_k)
    return result


def build_context(results):
    '''
    format previously retrieved chunks into a single context string
    Example output:
      [Source 1 - report.pdf (page 2) | score: 0.89]
      Revenue increased by 15% in Q3...
 
      [Source 2 - chart.png | score: 0.76]
      The bar chart shows quarterly sales with...
 
    Returns:
      context_text : the formatted string
    '''
    if not results:
        return "No relevant information found."

    context_parts = []
    for chunk in results:
        meta = chunk.get("metadata", {})
        score = chunk.get("score", 0)
        source_type = meta.get("source_type", "?")

        if source_type in ("pdf", "pdf_image"):
            source = f"{meta.get('file_name','?')} - page {meta.get('page_number','?')}"
        elif source_type == "url":
            source = meta.get("url", "?")
        elif source_type == "image":
            source = f"Image: {meta.get('file_name', '?')}"
        else:
            source = source_type

        context_parts.append(
            f"[Source: {source} | score: {score}]\n{chunk.get('text', '')}"
        )

    return "\n\n".join(context_parts)

    