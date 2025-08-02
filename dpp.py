import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from io import BytesIO
from PIL import Image

# --- Page Config ---
st.set_page_config(page_title="GeminiFusion", page_icon="🧠", layout="centered")

# --- Custom Vibrant CSS ---
st.markdown("""
    <style>
        html, body {
            background-color: #121212;
            margin: 0;
            padding: 0;
        }
        .main {
            padding: 0;
            margin: 0;
            font-family: 'Segoe UI', sans-serif;
        }
        .input-section {
            background-color: #000000;
            color: #00FF99;
            padding: 0 2rem 2rem 2rem; /* no top padding */
            border-radius: 0 0 10px 10px;
            box-shadow: 0px 0px 20px rgba(0,255,153,0.3);
        }
        .output-section {
            background-color: #00eaff;
            color: #000000;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0px 0px 20px rgba(0,234,255,0.3);
        }
        h1 {
            margin-top: 0;
            margin-bottom: 0.5rem;
            color: #00FF99;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
            padding: 10px;
            background-color: #1a1a1a;
            color: #00FF99;
            border: 1px solid #00FF99;
        }
        .stButton>button {
            background: linear-gradient(90deg, #00FF99, #00eaff);
            color: black;
            border: none;
            padding: 0.6em 1.5em;
            border-radius: 10px;
            font-size: 16px;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0px 0px 10px rgba(0,255,153,0.5);
        }
        .stRadio > div {
            gap: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load API Key ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API key not loaded. Check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

# --- Main Container ---
st.markdown("<div class='main'>", unsafe_allow_html=True)

# --- Input Section ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("<h1>🚀 GeminiFusion</h1>", unsafe_allow_html=True)
st.markdown("Transform your <strong>prompts</strong> into intelligent text or stunning AI-generated images.", unsafe_allow_html=True)

# --- Mode Selection ---
option = st.radio("Choose mode:", ("Text Generation", "Image Generation"))

# --- Prompt Input + Clear ---
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🧹 Clear", key="clear_button"):
        st.session_state["prompt_input"] = ""

with col1:
    prompt = st.text_input("Enter your prompt:", key="prompt_input")

st.markdown("</div>", unsafe_allow_html=True)

# --- Output Section ---
st.markdown("<div class='output-section'>", unsafe_allow_html=True)

# --- Session History ---
if "history" not in st.session_state:
    st.session_state["history"] = []

# --- Show History ---
def show_history():
    if st.session_state["history"]:
        st.subheader("🕘 Recent History")
        for entry in reversed(st.session_state["history"][-5:]):
            st.markdown(f"**Mode**: {entry['mode']}")
            st.markdown(f"**Prompt**: {entry['prompt']}")
            if entry["text"]:
                st.markdown(f"**Response**: {entry['text']}")
            if entry["image"]:
                st.image(entry["image"], caption="Previous Image", use_column_width=True)
            st.markdown("---")

show_history()

# --- Clear History ---
if st.session_state["history"]:
    if st.button("🗑️ Clear History"):
        st.session_state["history"] = []
        st.experimental_rerun()

# --- Download Helper ---
def download_image(img: Image.Image, filename="generated_image.png"):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_data = buf.getvalue()
    st.download_button(
        label="📥 Download Image",
        data=byte_data,
        file_name=filename,
        mime="image/png"
    )

# --- Generate Button ---
if st.button("Generate"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Thinking..."):
            try:
                if option == "Text Generation":
                    model = genai.GenerativeModel("gemini-2.5-pro")
                    response = model.generate_content(prompt)
                    output_text = response.text
                    st.success("Text Response:")
                    st.write(output_text)

                    st.session_state["history"].append({
                        "mode": option,
                        "prompt": prompt,
                        "text": output_text,
                        "image": None
                    })

                else:
                    model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
                    response = model.generate_content(
                        prompt,
                        generation_config={"response_modalities": ["TEXT", "IMAGE"]}
                    )

                    has_image = False
                    image_for_download = None
                    output_text = ""

                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            output_text = part.text
                            st.success("Description:")
                            st.write(output_text)

                        elif hasattr(part, 'inline_data') and part.inline_data and getattr(part.inline_data, 'data', None):
                            try:
                                image = Image.open(BytesIO(part.inline_data.data))
                                st.image(image, caption="Generated Image")
                                has_image = True
                                image_for_download = image
                            except Exception as img_err:
                                st.error(f"⚠️ Failed to decode image: {img_err}")
                                st.text(f"Raw starts with: {part.inline_data.data[:30]}...")

                    if has_image and image_for_download:
                        download_image(image_for_download)

                    if has_image or output_text:
                        st.session_state["history"].append({
                            "mode": option,
                            "prompt": prompt,
                            "text": output_text,
                            "image": image_for_download
                        })
                    else:
                        st.warning("No valid image or text returned. Try a different prompt.")

            except Exception as e:
                if "500" in str(e):
                    st.warning("Gemini had a hiccup. Try again shortly.")
                else:
                    st.error(f"❌ Error: {e}")

st.markdown("</div>", unsafe_allow_html=True)  # Close output section
st.markdown("</div>", unsafe_allow_html=True)  # Close main container
