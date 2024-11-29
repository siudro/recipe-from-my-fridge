import base64
import streamlit as st
from openai import OpenAI
from PIL import Image
import io

MODEL = st.secrets["model"]
api_key = st.secrets["api_key"]

client = OpenAI(
    api_key=api_key,
    base_url="https://api.openai.com/v1"
)

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_image(image_bytes):
    base64_image = encode_image(image_bytes)
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "You are a chef specializing in every cuisine in the world. Your task is to identify the ingredients present in the picture and create a detailed recipe based from what you see. List down all the foods present in the picture first in bullet form, and then proceed to recommend a recipe. When a customer asks you for further help, you will engage in a dialog with them to reach their task. If you don't identify any ingredients or foods from the picture create a recipe inspired by what you see."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ]
        }]
    )
    
    return response.choices[0].message.content

# Set page configuration
st.set_page_config(page_title="Fridgecipe", page_icon="🍳", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {background-color: #f8f9fa; padding: 2rem;}
    .header-container {text-align: center; padding: 2rem 0; background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%); border-radius: 15px; margin-bottom: 2rem;}
    .main-title {color: #2c3e50; font-size: 3.5rem !important; font-weight: 700;}
    .subtitle {color: #34495e; font-size: 1.2rem; font-weight: 400;}
    .stButton > button {width: 220px; height: 60px; background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%); color: white; font-weight: 600; border-radius: 25px; margin: 0.5rem; display: block; margin-left: auto; margin-right: auto;}
    .stButton > button:hover {transform: translateY(-2px);}
    .image-container {border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .message {background-color: #ffffff; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; color: #333;}
    .user-message {background-color: #d1e7dd; color: #000; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;}
    .assistant-message {background-color: #f8d7da; color: #000; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;}
    .input-container {margin-top: 1rem; text-align: center;}
    .center-content {display: flex; justify-content: center; align-items: center; flex-direction: column; margin-top: 1rem;}
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">🍳 Fridgecipe</h1>
        <p class="subtitle">Transform your ingredients into delicious recipes with AI</p>
    </div>
    """, unsafe_allow_html=True)

# Centered Content
st.markdown('<div class="center-content">', unsafe_allow_html=True)

# Tabs for image upload or camera capture
tab1, tab2 = st.tabs(["📁 Upload Image", "📸 Take Photo"])

# Initialize session states
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'recipe' not in st.session_state:
    st.session_state.recipe = ""

# Image Upload Tab
with tab1:
    st.markdown("<h3 style='text-align: center;'>Upload a photo of your fridge</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Fridge Contents", use_column_width=True)
        
        if st.button("✨ Create Recipe", key="upload_create_recipe"):
            with st.spinner("Creating your personalized recipe..."):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format)
                img_byte_arr = img_byte_arr.getvalue()
                
                st.session_state.recipe = analyze_image(img_byte_arr)  # Store recipe in session state

    # Display the recipe if it exists
    if st.session_state.recipe:
        st.markdown(f"""
            <div class="recipe-container">
                <h3>Recipe</h3>
                <div>{st.session_state.recipe}</div>
            </div>
        """, unsafe_allow_html=True)

    # Chatbot interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
                <div class="user-message"><strong>You:</strong> {message['content']}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="assistant-message"><strong>Chatbot:</strong> {message['content']}</div>
            """, unsafe_allow_html=True)
        
    user_input = st.text_input("Ask a follow-up question or request help", key="chat_input")
    if st.button("Send", key="send_button"):  # Add a button to send the message
        if user_input:
            # Store the user's message in chat history
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            # Prepare messages for the chatbot, including the recipe context
            messages = [{"role": "user", "content": user_input}]
            if st.session_state.recipe:
                messages.insert(0, {"role": "system", "content": f"The current recipe is: {st.session_state.recipe}"})
            # Get response from chatbot
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )
            chatbot_reply = response.choices[0].message.content
            st.session_state.chat_history.append({'role': 'assistant', 'content': chatbot_reply})
            st.markdown(f"""
                <div class="user-message"><strong>You:</strong> {user_input}</div>
                <div class="assistant-message"><strong>Chatbot:</strong> {chatbot_reply}</div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Camera Capture Tab
with tab2:
    st.markdown("<h3 style='text-align: center;'>Take a photo of your fridge</h3>", unsafe_allow_html=True)
    picture = st.camera_input("Capture your fridge")
    if picture is not None:
        st.image(picture, caption="Your Fridge Contents", use_column_width=True)
        
        if st.button("✨ Create Recipe", key="camera_create_recipe"):
            with st.spinner("Creating your personalized recipe..."):
                st.session_state.recipe = analyze_image(picture.getvalue())  # Store recipe in session state

    # Display the recipe if it exists
    if st.session_state.recipe:
        st.markdown(f"""
            <div class="recipe-container">
                <h3>Recipe</h3>
                <div>{st.session_state.recipe}</div>
            </div>
        """, unsafe_allow_html=True)

    # Chatbot interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
                <div class="user-message"><strong>You:</strong> {message['content']}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="assistant-message"><strong>Chatbot:</strong> {message['content']}</div>
            """, unsafe_allow_html=True)
        
    user_input = st.text_input("Ask a follow-up question or request help", key="camera_chat_input", on_change=None)
    if st.button("Send", key="camera_send_button"):  # Add a button to send the message
        if user_input:
            # Store the user's message in chat history
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            # Prepare messages for the chatbot, including the recipe context
            messages = [{"role": "user", "content": user_input}]
            if st.session_state.recipe:
                messages.insert(0, {"role": "system", "content": f"The current recipe is: {st.session_state.recipe}"})
            # Get response from chatbot
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )
            chatbot_reply = response.choices[0].message.content
            st.session_state.chat_history.append({'role': 'assistant', 'content': chatbot_reply})
            st.markdown(f"""
                <div class="user-message"><strong>You:</strong> {user_input}</div>
                <div class="assistant-message"><strong>Chatbot:</strong> {chatbot_reply}</div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style='text-align: center; color: #6c757d; padding: 2rem; margin-top: 3rem;'>
        <p>Made with ❤️ by Your Kitchen Assistant</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close the center-content div

