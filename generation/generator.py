'''
send the retrieved context + user question to the groq api and get the answer back
'''

from groq import Groq
import config

client = Groq(api_key = config.GROQ_API_KEY)

def generate_answer(question,context):
    #ask llm to answer the question based on the context
    prompt = f""" you are the helpful assistant. Answer the question using the context below
    if context does not contain enough information, say so clearly
    
    Context = {context}
    
    Question = {question}
    
    Answer """
    response = client.chat.completions.create(
        model = config.GROQ_TEXT_MODEL,
        messages = [
            {
                "role" : "user",
                "content" : prompt
            }
        ],
            max_tokens = 1024,
            temperature = 0.1
    )
    
    answer = response.choices[0].message.content.strip()
    return answer
