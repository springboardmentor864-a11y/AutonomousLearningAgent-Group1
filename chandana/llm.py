import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_content_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0.3,
    )

def get_mcq_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0.1,
    )
