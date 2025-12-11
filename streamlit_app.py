import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. SETUP
st.set_page_config(page_title="Qubikai Brief", page_icon="📩")

# 2. CONFIGURATIE
try:
    # Hier pakt hij je NIEUWE sleutel
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⚠️ Geen API Key gevonden.")
    st.stop()

# 3. MODEL KIEZEN (Nu werkt Flash wel!)
# Flash is het enige model dat snel is én foto's snapt.
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. INTERFACE
st.title("📩 Snap-mijn-Brief")
st.write("Upload je brief of maak een foto.")

uploaded_file = st.file_uploader("Kies bestand", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=300)
    
    with st.spinner('Analyseren met je nieuwe Key...'):
        try:
            # Test prompt
            prompt = "Wat zie je op deze afbeelding? Geef een korte samenvatting."
            
            # De aanroep naar Google
            response = model.generate_content([prompt, image])
            
            st.success("Gelukt! 🎉")
            st.write(response.text)
            
        except Exception as e:
            # Als hij nu nog faalt, zien we de ECHTE reden
            st.error("Toch nog een fout:")
            st.code(e)