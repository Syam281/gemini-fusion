# GeminiFusion ✨

An interactive Streamlit app that lets you generate **text** and **images** using Google Gemini AI models. Includes prompt history tracking and image download support.

## 🚀 Features

- 🤖 Text generation using `gemini-2.5-pro`
- 🎨 Image + text generation using `gemini-2.0-flash-preview-image-generation`
- 📜 Prompt history (last 5 interactions)
- 📥 Download generated images
- 🔄 Clear history anytime

## 🛠️ Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory and add your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. Run the app using Streamlit:
   ```bash
   streamlit run app.py
   ```

## 📌 Notes

- Choose between **Text Generation** or **Image Generation** mode.
- Image output supports download.
- Works with Google Gemini models (ensure API access is enabled).

---
