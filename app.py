import streamlit as st
from chatbot import ask_chatbot
import os

# Page configuration
st.set_page_config(
    page_title="Insurance Advisor AI",
    page_icon="💼",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
    }
    .subheader {
        font-size: 1.5rem;
        color: #558B2F;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# App tabs
tab1 = st.tabs(["Chat with Insurance Advisor"])[0]

with tab1:
    st.markdown('<p class="main-header">💼 Insurance Advisor AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Your AI-powered insurance assistant</p>', unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    query = st.chat_input("Ask me anything about insurance...")

    if query:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(query)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_chatbot(query)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with information
with st.sidebar:
    st.image("https://api.placeholder.com/120/120", width=120)
    st.markdown("### Insurance Advisor AI")
    st.markdown("This AI assistant helps with:")
    st.markdown("- Understanding insurance policies")
    st.markdown("- Claims process guidance")
    st.markdown("- Coverage and premium details")
    st.markdown("- General insurance FAQs")
    
    st.markdown("---")
    st.markdown("### Data Sources")
    st.markdown("This chatbot is trained on insurance regulations, policies, and industry best practices.")