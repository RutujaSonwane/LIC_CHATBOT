import os
import re
from dotenv import load_dotenv

# Google Generative AI
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# FAISS & RAG
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("Google API Key not found. Please set it in your .env file.")

# Path to FAISS vector DB
faiss_path = "vector_store/faiss_index"
if not os.path.exists(f"{faiss_path}/index.faiss"):
    raise FileNotFoundError(f"FAISS index not found at {faiss_path}/index.faiss. Please create it first.")

# Load FAISS with embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
db = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)

retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Load Gemini model
llm = GoogleGenerativeAI(model="gemini-1.5-flash", api_key=api_key,temperature=0)

# Prompt Template
prompt_template = """
You are a smart, helpful LIC Insurance Assistant helping users with LIC policies and financial planning.

User Question: {question}

Relevant Information from LIC Documents:
{context}

Based on the above, provide a concise answer (max 60 words). If no LIC-related info is available, say so politely and suggest asking LIC directly.

Tips:
- Be accurate, short, friendly, and helpful.
- Use simple language.
- Don't add unrelated info.
- If the answer is not in context, say so.

Your concise reply:
"""

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

# RetrievalQA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT},
    chain_type="stuff"
)

# Friendly greetings
GREETINGS = ["hi", "hello", "hey", "hyy", "good morning", "good afternoon", "good evening"]

def is_greeting(message):
    return any(re.match(rf"\b{greet}\b", message.lower()) for greet in GREETINGS)

def ask_chatbot(question):
    # Handle greeting first
    if is_greeting(question):
        return "👋 Hello! Welcome to the LIC Insurance Assistant. How can I help you today with LIC policies, claims, or financial planning?"

    result = qa_chain({"query": question})
    answer = result.get("result", "").strip()
    sources = result.get("source_documents", [])

    # Detect irrelevant response (fallback logic)
    if ("doesn't" in answer or "not described" in answer or "not found" in answer or "not available" in answer.lower()) \
        and not any(keyword in answer.lower() for keyword in ["lic", "policy", "insurance", "plan"]):
        return (
            "🧠 Hmm… that sounds unrelated to LIC policies. I'm your LIC Insurance Assistant and can help with policies, claims, and benefits. "
            "Feel free to ask me anything LIC-related!"
        )

    # Add source info only if relevant context exists
    if sources and "not described" not in answer.lower() and "not found" not in answer.lower():
        answer += "\n\n📚 **Sources:**"
        seen_sources = set()
        for doc in sources:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "")
            source_info = f"{source} (Page {page})" if page else source
            if source_info not in seen_sources:
                seen_sources.add(source_info)
                answer += f"\n- {source_info}"

    return answer

# CLI interface (for testing)
if __name__ == "__main__":
    while True:
        query = input("Ask me about LIC Insurance: ")
        if query.lower() in ["exit", "quit"]:
            break
        print("🤖:", ask_chatbot(query))
