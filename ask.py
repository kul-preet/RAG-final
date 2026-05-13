''' 
Ask the questions about ingested documents
'''

import sys
from retreival.retreiver import build_context, get_relevant_chunks
from generation.generator import generate_answer
from vectorstore.chroma_store import count

def answer_question(question):
    print(f"Searching knowledge base....")
    #-----------R------------------
    results = get_relevant_chunks(question)
    
    if not results:
        print(f"No relavant information found")
        print(f"Make sure you ran the ingest.py file")
        return
    
    #-----------A---------------------
    context = build_context(results)
    
    #-----------G-------------------
    print(f"Found {len(results)} relavant chunks. Generating answers")
    answer = generate_answer(question,context)
    
    print("=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(answer)

    print("\n" + "-" * 60)
    print(f"SOURCES ({len(results)} chunks used)")
    print("-" * 60)
    
    for i, result in enumerate(results, start=1):
        meta = result["metadata"]
        score = result["score"]
        source_type = meta.get("source_type", "?")
        
        if source_type in ("pdf", "pdf_image"):
            source = f"{meta.get('file_name','?')} - page {meta.get('page_number','?')}"
        elif source_type == "url":
            source = meta.get("url","?")
        elif source_type == "image":
            source = f"Image: {meta.get('file_name', '?')}"
        else:
            source = source_type    

        print(f"{i}, {source} [score: {score}]")
    
    print()
    


def interative_mode():
    total = count()
    print(f"RAG ready. {total} chunks in the knowledge")
    print(f"Type you question and press enter. Type quit to exit")
    
    while True:
        try:
            question = input("Enter your question: ").strip()
            
        except (KeyboardInterrupt, EOFError):
            print("\n Bye")
            break
            
        if not question:
            continue
        
        if question.lower() in ("quit", "exit", "q"):
            print("\n Bye")
            break
        
        answer_question(question)
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        answer_question(question)
    else:
        interative_mode()
    
    