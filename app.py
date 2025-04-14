import streamlit as st
from PIL import Image
import easyocr
from googletrans import Translator
from langdetect import detect
from gtts import gTTS
import numpy as np
from io import BytesIO

# ------------------ 🎨 PAGE CONFIG ------------------
st.set_page_config(page_title="OCR Translator", layout="centered")
st.markdown("<h1 style='text-align:center;'>🖼️ OCR Translator 🌍</h1>", unsafe_allow_html=True)

# ------------------ 📥 FILE UPLOAD ------------------
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
with st.expander("💬 Or enter text manually"):
    input_text = st.text_area("Paste your text here", "")

# ------------------ 🌐 LANGUAGE OPTIONS ------------------
translator = Translator()
languages = {
    'English': 'en', 'Hindi': 'hi', 'Telugu': 'te', 'Tamil': 'ta', 'Kannada': 'kn',
    'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Japanese': 'ja', 'Korean': 'ko'
}
lang_names = list(languages.keys())
target_lang = st.selectbox("Translate to", lang_names)

# ------------------ 🎯 TRANSLATION PROCESS ------------------
if st.button("Translate"):
    extracted_text = ""

    # OCR Process
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        try:
            reader = easyocr.Reader(['en', 'hi', 'te', 'ta', 'kn', 'es', 'fr', 'de', 'ja', 'ko'])  # Add more if needed
            result = reader.readtext(np.array(image), detail=0)
            extracted_text = ' '.join(result)
        except Exception as e:
            st.error(f"OCR Error: {e}")
            st.stop()

    # Text Input Process
    elif input_text.strip() != "":
        extracted_text = input_text.strip()
    else:
        st.warning("Please upload an image or enter some text.")
        st.stop()

    # Show detected text
    st.subheader("🔍 Detected Text")
    st.write(extracted_text)

    # Language detection
    try:
        detected_lang = detect(extracted_text)
    except:
        detected_lang = "unknown"

    st.write(f"🧭 Detected Language: {detected_lang}")

    # Translation Process
    try:
        translated = translator.translate(
            extracted_text,
            src=detected_lang,
            dest=languages[target_lang]
        )
        st.subheader("🌐 Translated Text")
        st.success(translated.text)

        # Text-to-speech
        tts = gTTS(text=translated.text, lang=languages[target_lang])
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        st.audio(audio_bytes, format='audio/mp3')
        st.download_button(
            "⬇️ Download Audio",
            data=audio_bytes,
            file_name="translated_audio.mp3",
            mime="audio/mp3"
        )

    except Exception as e:
        st.error(f"Translation or TTS error: {e}")
