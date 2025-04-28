import streamlit as st
from chatbot2 import ask_chatbot

# LIC Branding Colors
PRIMARY_BLUE = "#002060"
LIC_YELLOW = "#FDB913"
WHITE = "#FFFFFF"
LIGHT_GREY = "#F5F5F5"
DARK_TEXT = "#1c1c1c"

# Page Config
st.set_page_config(
    page_title="LIC Advisor Chatbot",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown(f"""
    <style>
        body {{
            background-color: {PRIMARY_BLUE};
        }}
        .main-header {{
            font-size: 2.8rem;
            color: {LIC_YELLOW};
            font-weight: 800;
            margin-bottom: 0;
        }}
        .subheader {{
            font-size: 1.2rem;
            color: {WHITE};
            margin-bottom: 2rem;
        }}
        .stChatMessage {{
            border-radius: 15px;
            padding: 1rem;
            margin: 10px 0;
        }}
        .stChatMessage.user {{
            background-color: #ffffff !important;
            color: #000000 !important;
            font-weight: 500;
            border-radius: 15px;
            padding: 1rem;
            box-shadow: 0 0 6px rgba(0,0,0,0.1);
        }}
        .stChatMessage.assistant {{
            background-color: #fff8dc !important;
            color: {DARK_TEXT} !important;
            border-radius: 15px;
            padding: 1rem;
            box-shadow: 0 0 6px rgba(0,0,0,0.1);
        }}
        .stTextInput > div > div > input {{
            border-radius: 8px;
            padding: 12px;
            background-color: #0f1c3f;
            color: {WHITE};
            border: 2px solid {LIC_YELLOW};
        }}
        .css-1v0mbdj p {{
            color: {WHITE};
        }}
        .block-container {{
            background-color: {PRIMARY_BLUE};
        }}
    </style>
""", unsafe_allow_html=True)

# Main title
st.markdown(f'<p class="main-header">💼 Insurance Advisor AI</p>', unsafe_allow_html=True)
st.markdown(f'<p class="subheader">Your Smart LIC Insurance Assistant</p>', unsafe_allow_html=True)

# Chat logic
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Type your LIC query here...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Let me check LIC records for you..."):
            response = ask_chatbot(query)

        # Assistant message in styled yellow box
        st.markdown(f"""
            <div style="background-color: #fff8dc; color: {DARK_TEXT}; padding: 1rem; border-radius: 12px;">
                <p style="margin:0;">
                    <span style="font-size:1.3rem;">📋</span> {response}
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.image("https://companieslogo.com/img/orig/LICI.NS-189af092.png?t=1720244492", width=130)
    st.markdown(f"### <span style='color:{LIC_YELLOW}'>LIC Advisor Chatbot</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 🤖 What I Can Help You With")
    st.markdown("🔹 **Policy Info**  \n🔹 **Claims**  \n🔹 **Premiums**  \n🔹 **FAQs**")

    st.markdown(" ")
    st.markdown("#### 📁 Data Sources")
    st.markdown("This chatbot uses LIC brochures, policy PDFs & IRDAI documents.")

    st.markdown("---")
    st.markdown("Made with 💛 by Rutuja & Komal", unsafe_allow_html=True)
