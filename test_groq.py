from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

load_dotenv()

print("GROQ_API_KEY found:", bool(os.getenv("GROQ_API_KEY")))

llm = ChatGroq(
    model="llama-3.1-8b-instant",  # ✅ supported model
    temperature=0
)

response = llm.invoke("Explain Python decorators in one sentence")
print("\n🧠 Groq Response:")
print(response.content)
