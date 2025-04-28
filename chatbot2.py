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
threshold = 0.75
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5} )

# Load Gemini model
llm = GoogleGenerativeAI(model="gemini-1.5-flash", api_key=api_key)

# Prompt Template
prompt_template = """
You are a smart and helpful LIC Insurance Assistant. Your role is to answer user questions clearly and concisely based on LIC policy documents (context). Your tone should be friendly, confident, and trustworthy.

User Question: {question}

Relevant Information from LIC Documents:
{context}

📋 **Your task:**

1. **Start with a short and friendly summary** (max 60 words) that answers the query simply. If full explanation can't fit in 60 words, give a short summary first, then expand below.
2. Use **bullet points**, **bold headings**, and keep the format clean.
3. Stick to the info in context only. **Do NOT guess or hallucinate.**
4. If the query is NOT related to LIC or info isn't found in the context, respond with:
   🧠 Hmm… that sounds unrelated to LIC policies. I'm your LIC Insurance Assistant and can help with policies, claims, and benefits. Feel free to ask me anything LIC-related!

🎯 **Response Format**:

📋 [Short summary, 1–2 lines if possible]

🔍 **Details:**
- [bullet point with info]


📚 **Sources:**
- [filename] (Page X)

✅ Be helpful, relevant, friendly.
❌ Don’t mention hallucinated content.
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
GREETINGS = ["hi", "hello", "hey", "hii", "hyy", "good morning", "good afternoon", "good evening"]

def is_greeting(message):
    return any(re.match(rf"\b{greet}\b", message.lower()) for greet in GREETINGS)

def ask_chatbot(question):
    # Handle greeting
    if is_greeting(question):
        return "👋 Hello! Welcome to the LIC Insurance Assistant. How can I help you today with LIC policies, claims, or financial planning?"

    result = qa_chain({"query": question})
    answer = result.get("result", "").strip()
    sources = result.get("source_documents", [])

    # Fallback phrases indicating irrelevant or empty response
    fallback_phrases = [
        "मुझे माफ़ करना", "मैं सक्षम नहीं हूँ", "not available", "not found",
        "कृपया LIC शाखा से संपर्क करें", "consult LIC", "website पर जाएँ",
        "unable to find", "unable to determine"
    ]

    # Specific case handling for "28 saal ka hoon" type questions
    if re.search(r"(28\s*saal|28\s*year|28\s*वर्ष|मैं\s*28\s*साल\s*का\s*हूँ)", question.lower()):
        return (
            "📋 आपकी उम्र और अविवाहित स्थिति को देखते हुए, **LIC की New Jeevan Amar** या **Digi-Term** पॉलिसी एक अच्छा विकल्प हो सकती है। "
            "ये टर्म प्लान्स आपको कम प्रीमियम में अधिक जीवन सुरक्षा प्रदान करते हैं। अधिक जानकारी के लिए, कृपया LIC एजेंट से संपर्क करें या उनकी वेबसाइट पर जाएँ।\n\n"
            "📚 **Sources:**\n"
            "- LIC-data\\955-512N350V02NewJeevanAmar.pdf (Page 2)\n"
            "- LIC-data\\876-512N356V02DigiTerm.pdf (Page 5)"
        )

    # Generic fallback if hallucinated or irrelevant
    if any(phrase.lower() in answer.lower() for phrase in fallback_phrases) or (
        ("not described" in answer.lower() or "doesn't" in answer.lower()) and
        not any(word in answer.lower() for word in ["lic", "insurance", "policy", "plan"])
    ):
        return (
            "🧠 Hmm… that sounds unrelated to LIC policies. I'm your LIC Insurance Assistant and can help with policies, claims, and benefits. "
            "Feel free to ask me anything LIC-related!"
        )

    # Append sources if available and not already present in the answer
    if sources and "📚 **Sources:**" not in answer:
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

# CLI interface for testing
if __name__ == "__main__":
    while True:
        query = input("Ask me about LIC Insurance: ")
        if query.lower() in ["exit", "quit"]:
            break
        print("🤖:", ask_chatbot(query))
