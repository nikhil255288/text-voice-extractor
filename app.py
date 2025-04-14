import streamlit as st
from PIL import Image
import easyocr
from googletrans import Translator
from langdetect import detect
from gtts import gTTS
import os
import json

import uuid
import numpy as np
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------ 🔥 FIREBASE SETUP ------------------
with open("translate-ocr-app-firebase-adminsdk-fbsvc-64596fd124.json") as f:
    firebase_config = json.load(f)

# Prepare credentials dictionary (handling private_key newlines)
firebase_admin_credentials = {
    "type": firebase_config["type"],
    "project_id": firebase_config["project_id"],
    "private_key_id": firebase_config["private_key_id"],
    "private_key": firebase_config["private_key"].replace('\\n', '\n'),
    "client_email": firebase_config["client_email"],
    "client_id": firebase_config["client_id"],
    "auth_uri": firebase_config["auth_uri"],
    "token_uri": firebase_config["token_uri"],
    "auth_provider_x509_cert_url": firebase_config["auth_provider_x509_cert_url"],
    "client_x509_cert_url": firebase_config["client_x509_cert_url"]
}

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_admin_credentials)
firebase_admin.initialize_app(cred)

print("✅ Firebase initialized successfully!")
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

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        try:
            reader = easyocr.Reader(['en'])  # Add more if needed
            result = reader.readtext(np.array(image), detail=0)
            extracted_text = ' '.join(result)
        except Exception as e:
            st.error(f"OCR Error: {e}")
            st.stop()

    elif input_text.strip() != "":
        extracted_text = input_text.strip()
    else:
        st.warning("Please upload an image or enter some text.")
        st.stop()

    st.subheader("🔍 Detected Text")
    st.write(extracted_text)

    try:
        detected_lang = detect(extracted_text)
    except:
        detected_lang = "unknown"

    st.write(f"🧭 Detected Language: {detected_lang}")

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

        # Log to Firestore
        doc_ref = db.collection("translations").document()
        doc_ref.set({
            "original_text": extracted_text,
            "translated_text": translated.text,
            "source_lang": detected_lang,
            "target_lang": languages[target_lang]
        })

    except Exception as e:
        st.error(f"Translation or TTS error: {e}")
bro is this coode corrert or if not make it live
