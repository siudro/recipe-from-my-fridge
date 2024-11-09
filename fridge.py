import base64
import streamlit as st
from openai import OpenAI
from PIL import Image
import io

# Initialize OpenAI client with your API key
client = OpenAI(api_key=st.secrets["api_key"])

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_image(image_bytes):
    base64_image = encode_image(image_bytes)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Updated to correct model name
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "List down what ingredients are in this image. Make me a recipe based on the ingredients in this image.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    
    return response.choices[0].message.content

# Streamlit UI
st.title("Fridgecipe")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Upload Image", "Take Photo"])

with tab1:
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Analyze button with unique key
        if st.button("Make me a recipe", key="upload_button"):
            with st.spinner("Doing my magic..."):
                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format)
                img_byte_arr = img_byte_arr.getvalue()
                
                # Get and display analysis
                analysis = analyze_image(img_byte_arr)
                st.write("### Analysis Result:")
                st.write(analysis)

with tab2:
    picture = st.camera_input("Take a picture")
    if picture is not None:
        # Display the captured image
        st.image(picture, caption="Captured Image", use_column_width=True)
        
        # Analyze button with unique key
        if st.button("Make me a recipe", key="camera_button"):
            with st.spinner("Analyzing..."):
                # Get and display analysis
                analysis = analyze_image(picture.getvalue())
                st.write("### Analysis Result:")
                st.write(analysis)