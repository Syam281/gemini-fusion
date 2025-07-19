import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from io import BytesIO
from PIL import Image

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API key not loaded. Check your .env file.")
    st.stop()

genai.configure(api_key=api_key)

st.title("GeminiFusion")

# Initialize history if not present
if "history" not in st.session_state:
    st.session_state["history"] = []

# Display history
def show_history():
    if st.session_state["history"]:
        st.subheader("🕘 Recent History")
        for entry in reversed(st.session_state["history"][-5:]):  # Show last 5
            st.markdown(f"**Mode**: {entry['mode']}")
            st.markdown(f"**Prompt**: {entry['prompt']}")
            if entry["text"]:
                st.markdown(f"**Response**: {entry['text']}")
            if entry["image"]:
                st.image(entry["image"], caption="Previous Image", use_column_width=True)
            st.markdown("---")

# Clear history button
if st.session_state["history"]:
    if st.button("🗑️ Clear History"):
        st.session_state["history"] = []
        st.experimental_rerun()

# UI controls
option = st.radio("Choose mode:", ("Text Generation", "Image Generation"))
prompt = st.text_input("Enter your prompt:")

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

# Show existing history
show_history()

if st.button("Generate"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Thinking..."):
            try:
                if option == "Text Generation":
                    model_name = "gemini-2.5-pro"
                    model = genai.GenerativeModel(model_name)
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
                    model_name = "gemini-2.0-flash-preview-image-generation"
                    model = genai.GenerativeModel(model_name)
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